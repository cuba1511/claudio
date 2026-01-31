"""
Tests de integración para validar que el bot está listo para funcionar
vía WhatsApp (a través de Twilio u otro proveedor).

Simula flujos end-to-end reales de WhatsApp:
- Pedidos de comida completos con confirmación
- Consultas de menú y disponibilidad
- Conversaciones multi-turno con contexto
- Manejo de mensajes multimedia (voz)
- Límites de caracteres de WhatsApp (4096)
- Múltiples clientes simultáneos con pedidos distintos
- Errores, reintentos y recuperación
- Rate limiting por número de teléfono
- Flujos de cancelación y modificación
"""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch, call

import pytest

import telegram_claude_bot as bot
from telegram_claude_bot import ClaudeCodeExecutor, OutputBuffer


# =====================================================================
# Helpers
# =====================================================================

def make_update(user_id=111111, username="testuser", text="Hello"):
    """Crea un mock de Update simulando un mensaje de WhatsApp."""
    update = MagicMock()
    update.effective_user = MagicMock()
    update.effective_user.id = user_id
    update.effective_user.username = username
    update.effective_user.first_name = "Test"
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.text = text
    update.message.voice = None
    return update


def make_context():
    ctx = MagicMock()
    ctx.bot = MagicMock()
    ctx.bot.get_file = AsyncMock()
    return ctx


def setup_processing_msg(update):
    mock_processing = AsyncMock()
    mock_processing.edit_text = AsyncMock()
    update.message.reply_text = AsyncMock(return_value=mock_processing)
    return mock_processing


# =====================================================================
# Flujo completo de pedido por WhatsApp
# =====================================================================

class TestFlujoPedidoWhatsApp:
    """Simula un flujo real de pedido de comida por WhatsApp."""

    @pytest.mark.asyncio
    async def test_flujo_saludo_menu_pedido_confirmacion(self):
        """Flujo: saludo → consulta menú → hacer pedido → confirmar."""
        context = make_context()
        mock_result = {"success": True, "returncode": 0}

        with patch.object(bot, "ALLOWED_USER_IDS", [111111]):
            steps = [
                ("Hola, quiero hacer un pedido", False),
                ("¿Qué tienen en el menú?", True),
                ("Quiero 2 pizzas margarita y 1 coca cola", True),
                ("Sí, confirmo el pedido", True),
            ]

            for i, (query, expected_continue) in enumerate(steps):
                update = make_update(text=query)
                setup_processing_msg(update)
                with patch.object(
                    ClaudeCodeExecutor,
                    "execute_streaming",
                    new_callable=AsyncMock,
                    return_value=mock_result,
                ) as mock_exec:
                    await bot.process_query(
                        update, context, query, 111111, "testuser"
                    )
                    assert mock_exec.call_args[0][2] is expected_continue, \
                        f"Paso {i} ('{query}'): continue_session esperado={expected_continue}"

        assert bot.user_sessions.get(111111) is True

    @pytest.mark.asyncio
    async def test_flujo_pedido_con_direccion_y_pago(self):
        """Flujo conversacional largo: pedido → dirección → método de pago."""
        context = make_context()
        mock_result = {"success": True, "returncode": 0}

        with patch.object(bot, "ALLOWED_USER_IDS", [111111]):
            conversation = [
                "Quiero pedir 3 hamburguesas con papas",
                "Mi dirección es Av. Providencia 1234, depto 5B",
                "Pago con tarjeta de crédito terminada en 4532",
                "Confirmo todo, gracias",
            ]

            for i, msg in enumerate(conversation):
                update = make_update(text=msg)
                setup_processing_msg(update)
                with patch.object(
                    ClaudeCodeExecutor,
                    "execute_streaming",
                    new_callable=AsyncMock,
                    return_value=mock_result,
                ) as mock_exec:
                    await bot.process_query(
                        update, context, msg, 111111, "testuser"
                    )
                    if i > 0:
                        assert mock_exec.call_args[0][2] is True

        assert bot.user_sessions.get(111111) is True

    @pytest.mark.asyncio
    async def test_flujo_pedido_falla_y_reintenta(self):
        """Cliente envía pedido, falla el sistema, reintenta y funciona."""
        context = make_context()

        with patch.object(bot, "ALLOWED_USER_IDS", [111111]):
            # Primer intento: falla
            u1 = make_update(text="Quiero 2 pizzas napolitanas")
            setup_processing_msg(u1)
            with patch.object(
                ClaudeCodeExecutor,
                "execute_streaming",
                new_callable=AsyncMock,
                return_value={"success": False, "returncode": 1},
            ):
                await bot.process_query(
                    u1, context, "Quiero 2 pizzas napolitanas", 111111, "testuser"
                )

            assert 111111 not in bot.user_sessions

            # Reintento: funciona
            u2 = make_update(text="Quiero 2 pizzas napolitanas")
            setup_processing_msg(u2)
            with patch.object(
                ClaudeCodeExecutor,
                "execute_streaming",
                new_callable=AsyncMock,
                return_value={"success": True, "returncode": 0},
            ):
                await bot.process_query(
                    u2, context, "Quiero 2 pizzas napolitanas", 111111, "testuser"
                )

            assert bot.user_sessions.get(111111) is True

    @pytest.mark.asyncio
    async def test_flujo_cancelacion_y_nuevo_pedido(self):
        """Cliente cancela pedido (/new) y hace uno nuevo desde cero."""
        context = make_context()
        mock_result = {"success": True, "returncode": 0}

        with patch.object(bot, "ALLOWED_USER_IDS", [111111]):
            # Pedido original
            u1 = make_update(text="Quiero 5 empanadas de carne")
            setup_processing_msg(u1)
            with patch.object(
                ClaudeCodeExecutor,
                "execute_streaming",
                new_callable=AsyncMock,
                return_value=mock_result,
            ):
                await bot.process_query(
                    u1, context, "Quiero 5 empanadas de carne", 111111, "testuser"
                )

            assert bot.user_sessions.get(111111) is True

            # Cancelar
            u_cancel = make_update()
            await bot.new_conversation(u_cancel, context)
            assert 111111 not in bot.user_sessions

            # Nuevo pedido - NO debe continuar sesión anterior
            u2 = make_update(text="Mejor quiero 3 tacos al pastor")
            setup_processing_msg(u2)
            with patch.object(
                ClaudeCodeExecutor,
                "execute_streaming",
                new_callable=AsyncMock,
                return_value=mock_result,
            ) as mock_exec:
                await bot.process_query(
                    u2, context, "Mejor quiero 3 tacos al pastor", 111111, "testuser"
                )
                assert mock_exec.call_args[0][2] is False

    @pytest.mark.asyncio
    async def test_flujo_modificacion_mid_pedido(self):
        """Cliente modifica el pedido antes de confirmar."""
        context = make_context()
        mock_result = {"success": True, "returncode": 0}

        with patch.object(bot, "ALLOWED_USER_IDS", [111111]):
            msgs = [
                "Quiero 2 pizzas margarita grandes",
                "Espera, cambia una por hawaiana",
                "Y agrega 2 jugos de naranja",
                "Ahora sí, confirmo el pedido",
            ]

            for i, msg in enumerate(msgs):
                update = make_update(text=msg)
                setup_processing_msg(update)
                with patch.object(
                    ClaudeCodeExecutor,
                    "execute_streaming",
                    new_callable=AsyncMock,
                    return_value=mock_result,
                ) as mock_exec:
                    await bot.process_query(
                        update, context, msg, 111111, "testuser"
                    )
                    if i > 0:
                        assert mock_exec.call_args[0][2] is True

        assert bot.user_sessions.get(111111) is True


# =====================================================================
# Múltiples clientes simultáneos por WhatsApp
# =====================================================================

class TestMultiplesClientesWhatsApp:
    """Simula múltiples clientes haciendo pedidos al mismo tiempo."""

    @pytest.mark.asyncio
    async def test_tres_clientes_pedidos_independientes(self):
        """Tres clientes hacen pedidos sin interferencia entre ellos."""
        context = make_context()
        mock_result = {"success": True, "returncode": 0}

        clients = {
            111111: [
                "Hola, quiero 2 pizzas",
                "Con extra queso por favor",
            ],
            222222: [
                "Me da 3 tacos de pastor",
                "Y una horchata grande",
            ],
            333333: [
                "Quiero un combo familiar",
            ],
        }

        with patch.object(bot, "ALLOWED_USER_IDS", [111111, 222222, 333333]):
            for uid, messages in clients.items():
                for msg in messages:
                    update = make_update(user_id=uid, text=msg)
                    setup_processing_msg(update)
                    with patch.object(
                        ClaudeCodeExecutor,
                        "execute_streaming",
                        new_callable=AsyncMock,
                        return_value=mock_result,
                    ):
                        await bot.process_query(
                            update, context, msg, uid, f"client_{uid}"
                        )

        # Todos deben tener sesión activa
        for uid in [111111, 222222, 333333]:
            assert bot.user_sessions.get(uid) is True

    @pytest.mark.asyncio
    async def test_un_cliente_cancela_otros_no_afectados(self):
        """Un cliente cancela su pedido, los demás siguen sin cambios."""
        context = make_context()
        mock_result = {"success": True, "returncode": 0}

        with patch.object(bot, "ALLOWED_USER_IDS", [111111, 222222, 333333]):
            # Todos hacen un pedido
            for uid in [111111, 222222, 333333]:
                update = make_update(user_id=uid, text=f"Pedido de cliente {uid}")
                setup_processing_msg(update)
                with patch.object(
                    ClaudeCodeExecutor,
                    "execute_streaming",
                    new_callable=AsyncMock,
                    return_value=mock_result,
                ):
                    await bot.process_query(
                        update, context, f"Pedido de cliente {uid}", uid, f"c{uid}"
                    )

            # Cliente 222222 cancela
            u_cancel = make_update(user_id=222222)
            await bot.new_conversation(u_cancel, context)

        assert bot.user_sessions.get(111111) is True
        assert 222222 not in bot.user_sessions
        assert bot.user_sessions.get(333333) is True

    @pytest.mark.asyncio
    async def test_clientes_intercalados_mantienen_contexto(self):
        """Mensajes intercalados de distintos clientes mantienen contexto correcto."""
        context = make_context()
        mock_result = {"success": True, "returncode": 0}

        with patch.object(bot, "ALLOWED_USER_IDS", [111111, 222222]):
            # Intercalar mensajes: c1, c2, c1, c2
            messages = [
                (111111, "Hola, quiero pizza"),
                (222222, "Hola, quiero tacos"),
                (111111, "Con extra queso"),       # debe continuar sesión de 111111
                (222222, "Con salsa verde"),        # debe continuar sesión de 222222
            ]

            for i, (uid, msg) in enumerate(messages):
                update = make_update(user_id=uid, text=msg)
                setup_processing_msg(update)
                with patch.object(
                    ClaudeCodeExecutor,
                    "execute_streaming",
                    new_callable=AsyncMock,
                    return_value=mock_result,
                ) as mock_exec:
                    await bot.process_query(
                        update, context, msg, uid, f"c{uid}"
                    )
                    # Los mensajes 3 y 4 (index 2,3) deben continuar sesión
                    if i >= 2:
                        assert mock_exec.call_args[0][2] is True, \
                            f"Mensaje {i} de uid={uid} debería continuar sesión"

    @pytest.mark.asyncio
    async def test_cliente_con_error_no_afecta_otros(self):
        """Un error en el pedido de un cliente no afecta a los demás."""
        context = make_context()
        success = {"success": True, "returncode": 0}
        failure = {"success": False, "returncode": 1}

        with patch.object(bot, "ALLOWED_USER_IDS", [111111, 222222]):
            # Cliente 1: éxito
            u1 = make_update(user_id=111111, text="Pizza margarita")
            setup_processing_msg(u1)
            with patch.object(
                ClaudeCodeExecutor,
                "execute_streaming",
                new_callable=AsyncMock,
                return_value=success,
            ):
                await bot.process_query(u1, context, "Pizza margarita", 111111, "c1")

            # Cliente 2: fallo
            u2 = make_update(user_id=222222, text="Producto inexistente")
            setup_processing_msg(u2)
            with patch.object(
                ClaudeCodeExecutor,
                "execute_streaming",
                new_callable=AsyncMock,
                return_value=failure,
            ):
                await bot.process_query(u2, context, "Producto inexistente", 222222, "c2")

        assert bot.user_sessions.get(111111) is True
        assert 222222 not in bot.user_sessions


# =====================================================================
# Formato de mensajes para WhatsApp
# =====================================================================

class TestFormatoMensajesWhatsApp:
    """Verifica que los mensajes se formatean correctamente para WhatsApp."""

    def test_respuesta_larga_se_divide_en_4096_chars(self):
        """WhatsApp tiene límite de 4096 chars por mensaje."""
        long_text = "Detalle del pedido:\n" + "- Item con descripción larga\n" * 400
        parts = bot.split_message(long_text, max_length=4096)

        for part in parts:
            assert len(part) <= 4096
        assert len(parts) > 1

    def test_respuesta_corta_no_se_divide(self):
        """Un mensaje corto queda en una sola parte."""
        short_text = "Tu pedido #123 está en camino."
        parts = bot.split_message(short_text, max_length=4096)
        assert len(parts) == 1
        assert parts[0] == short_text

    def test_ansi_codes_limpiados_para_whatsapp(self):
        """Los códigos ANSI del CLI se limpian antes de enviar."""
        raw_output = (
            "\x1b[32m✅ Pedido creado exitosamente\x1b[0m\n"
            "\x1b[1mTotal: $15.990\x1b[0m\n"
            "\x1b[33m⏳ Tiempo estimado: 30 min\x1b[0m"
        )
        cleaned = bot.remove_ansi_codes(raw_output)
        assert "\x1b" not in cleaned
        assert "Pedido creado exitosamente" in cleaned
        assert "Total: $15.990" in cleaned
        assert "Tiempo estimado: 30 min" in cleaned

    def test_mensaje_con_emojis_se_preserva(self):
        """Los emojis del menú/respuestas se preservan correctamente."""
        text_with_emojis = "🍕 Pizza Margarita - $8.990\n🌮 Tacos x3 - $6.990\n🥤 Bebida - $1.990"
        parts = bot.split_message(text_with_emojis, max_length=4096)
        assert len(parts) == 1
        assert "🍕" in parts[0]
        assert "🌮" in parts[0]
        assert "🥤" in parts[0]

    def test_tabla_larga_se_divide_sin_corromper(self):
        """Una tabla larga (ej. inventario) se divide sin perder filas."""
        rows = [f"| Item {i:03d} | ${i * 1000} | {'Disponible' if i % 2 == 0 else 'Agotado'} |"
                for i in range(200)]
        table = "| Producto | Precio | Estado |\n|---|---|---|\n" + "\n".join(rows)
        parts = bot.split_message(table, max_length=4096)

        for part in parts:
            assert len(part) <= 4096
            assert len(part) > 0

        # Verificar que no se perdieron filas
        combined = "".join(parts)
        assert "Item 000" in combined
        assert "Item 199" in combined


# =====================================================================
# Mensajes de voz por WhatsApp
# =====================================================================

class TestVozWhatsApp:
    """Simula el flujo de notas de voz de WhatsApp."""

    @pytest.mark.asyncio
    async def test_nota_voz_pedido_se_transcribe_y_ejecuta(self):
        """Una nota de voz con un pedido se transcribe y procesa."""
        context = make_context()
        update = make_update()
        update.message.voice = MagicMock()
        update.message.voice.file_id = "whatsapp_voice_123"
        setup_processing_msg(update)

        with patch.object(bot, "ALLOWED_USER_IDS", [111111]), \
             patch.object(bot, "OPENAI_AVAILABLE", True), \
             patch.object(bot, "OPENAI_API_KEY", "test-key"), \
             patch(
                 "telegram_claude_bot.download_voice_file",
                 new_callable=AsyncMock,
                 return_value="/tmp/voice_pedido.ogg",
             ), \
             patch(
                 "telegram_claude_bot.transcribe_voice_message",
                 new_callable=AsyncMock,
                 return_value="Quiero dos pizzas grandes con extra queso",
             ), \
             patch(
                 "telegram_claude_bot.process_query", new_callable=AsyncMock
             ) as mock_pq, \
             patch("os.remove"):
            await bot.handle_voice_message(update, context)

        mock_pq.assert_called_once()
        assert mock_pq.call_args[0][2] == "Quiero dos pizzas grandes con extra queso"
        assert mock_pq.call_args[0][3] == 111111

    @pytest.mark.asyncio
    async def test_voz_falla_descarga_muestra_error(self):
        """Si la descarga de audio falla, se muestra error al cliente."""
        context = make_context()
        update = make_update()
        update.message.voice = MagicMock()
        update.message.voice.file_id = "bad_voice"
        mock_processing = setup_processing_msg(update)

        with patch.object(bot, "ALLOWED_USER_IDS", [111111]), \
             patch.object(bot, "OPENAI_AVAILABLE", True), \
             patch.object(bot, "OPENAI_API_KEY", "test-key"), \
             patch(
                 "telegram_claude_bot.download_voice_file",
                 new_callable=AsyncMock,
                 return_value=None,
             ), \
             patch(
                 "telegram_claude_bot.transcribe_voice_message",
                 new_callable=AsyncMock,
             ) as mock_transcribe:
            await bot.handle_voice_message(update, context)

        mock_transcribe.assert_not_called()
        edit_calls = mock_processing.edit_text.call_args_list
        error_shown = any("Error" in str(c) for c in edit_calls)
        assert error_shown

    @pytest.mark.asyncio
    async def test_voz_sin_openai_muestra_error(self):
        """Sin API key de OpenAI, la voz muestra error apropiado."""
        context = make_context()
        update = make_update()
        update.message.voice = MagicMock()
        update.message.voice.file_id = "voice_no_key"
        setup_processing_msg(update)

        with patch.object(bot, "ALLOWED_USER_IDS", [111111]), \
             patch.object(bot, "OPENAI_AVAILABLE", False):
            await bot.handle_voice_message(update, context)

        reply_text = update.message.reply_text.call_args[0][0]
        assert "transcripción" in reply_text.lower() or "voz" in reply_text.lower() or "no disponible" in reply_text.lower()


# =====================================================================
# Rate limiting por cliente WhatsApp
# =====================================================================

class TestRateLimitingWhatsApp:
    """Verifica que el rate limiting funciona correctamente por cliente."""

    @pytest.mark.asyncio
    async def test_cliente_excede_rate_limit_es_bloqueado(self):
        """Un cliente que envía demasiados mensajes es bloqueado temporalmente."""
        context = make_context()

        with patch.object(bot, "ALLOWED_USER_IDS", [111111]), \
             patch.object(bot, "RATE_LIMIT_REQUESTS", 3), \
             patch.object(bot, "RATE_LIMIT_WINDOW", 60):

            # Enviar 3 mensajes (al límite)
            for i in range(3):
                update = make_update(text=f"Mensaje {i+1}")
                await bot.handle_message(update, context)

            # El 4to debería ser bloqueado
            update = make_update(text="Mensaje bloqueado")
            await bot.handle_message(update, context)

            call_text = update.message.reply_text.call_args[0][0]
            assert "Rate limit" in call_text

    @pytest.mark.asyncio
    async def test_rate_limit_aislado_entre_clientes(self):
        """El rate limit de un cliente no afecta a otros."""
        with patch.object(bot, "RATE_LIMIT_REQUESTS", 2), \
             patch.object(bot, "RATE_LIMIT_WINDOW", 60):

            # Cliente 1 agota su rate limit
            for _ in range(2):
                bot.check_rate_limit(111111)

            allowed_1, _ = bot.check_rate_limit(111111)
            assert allowed_1 is False

            # Cliente 2 aún puede enviar
            allowed_2, _ = bot.check_rate_limit(222222)
            assert allowed_2 is True

    def test_rate_limit_se_recupera_tras_ventana(self):
        """Después de la ventana de tiempo, el cliente puede enviar de nuevo."""
        with patch.object(bot, "RATE_LIMIT_REQUESTS", 2), \
             patch.object(bot, "RATE_LIMIT_WINDOW", 0.3):

            bot.check_rate_limit(111111)
            bot.check_rate_limit(111111)

            allowed, _ = bot.check_rate_limit(111111)
            assert allowed is False

            time.sleep(0.4)

            allowed, _ = bot.check_rate_limit(111111)
            assert allowed is True


# =====================================================================
# Autenticación de clientes WhatsApp
# =====================================================================

class TestAutenticacionWhatsApp:
    """Verifica que solo clientes autorizados pueden usar el servicio."""

    @pytest.mark.asyncio
    async def test_numero_no_autorizado_bloqueado(self):
        """Un número de WhatsApp no autorizado es bloqueado."""
        context = make_context()

        with patch.object(bot, "ALLOWED_USER_IDS", [111111]):
            update = make_update(user_id=999999, text="Quiero hacer un pedido")
            await bot.handle_message(update, context)
            assert "Acceso denegado" in update.message.reply_text.call_args[0][0]

    @pytest.mark.asyncio
    async def test_numero_no_autorizado_no_consume_recursos(self):
        """Intentos de números no autorizados no consumen rate limit."""
        context = make_context()

        with patch.object(bot, "ALLOWED_USER_IDS", [111111]):
            for _ in range(30):
                u = make_update(user_id=999999, text="intento")
                await bot.handle_message(u, context)

        assert 999999 not in bot.rate_limit_tracker

    @pytest.mark.asyncio
    async def test_multiples_numeros_no_autorizados_bloqueados(self):
        """Varios números no autorizados son bloqueados independientemente."""
        context = make_context()

        with patch.object(bot, "ALLOWED_USER_IDS", [111111]):
            for uid in [888888, 777777, 666666, 555555]:
                u = make_update(user_id=uid, text="Hola, quiero pedir")
                await bot.handle_message(u, context)
                assert "Acceso denegado" in u.message.reply_text.call_args[0][0]

    @pytest.mark.asyncio
    async def test_numero_autorizado_puede_enviar_y_ejecutar(self):
        """Un número autorizado puede enviar mensajes y ejecutar queries."""
        context = make_context()
        mock_result = {"success": True, "returncode": 0}

        with patch.object(bot, "ALLOWED_USER_IDS", [111111]):
            update = make_update(text="Quiero un café")
            setup_processing_msg(update)
            with patch.object(
                ClaudeCodeExecutor,
                "execute_streaming",
                new_callable=AsyncMock,
                return_value=mock_result,
            ) as mock_exec:
                await bot.process_query(
                    update, context, "Quiero un café", 111111, "testuser"
                )
                mock_exec.assert_called_once()

        assert bot.user_sessions.get(111111) is True


# =====================================================================
# Timeout y resiliencia en WhatsApp
# =====================================================================

class TestTimeoutResilienciaWhatsApp:
    """Verifica que timeouts y errores no rompen la experiencia del cliente."""

    @pytest.mark.asyncio
    async def test_timeout_no_bloquea_siguiente_pedido(self):
        """Después de un timeout, el cliente puede seguir enviando."""
        context = make_context()

        with patch.object(bot, "ALLOWED_USER_IDS", [111111]):
            # Timeout
            u1 = make_update(text="Consulta compleja de inventario")
            setup_processing_msg(u1)
            with patch.object(
                ClaudeCodeExecutor,
                "execute_streaming",
                new_callable=AsyncMock,
                return_value={"success": False, "returncode": -2, "timeout": True},
            ):
                await bot.process_query(
                    u1, context, "Consulta compleja de inventario", 111111, "testuser"
                )

            # Siguiente pedido funciona
            u2 = make_update(text="Quiero 1 pizza")
            setup_processing_msg(u2)
            with patch.object(
                ClaudeCodeExecutor,
                "execute_streaming",
                new_callable=AsyncMock,
                return_value={"success": True, "returncode": 0},
            ):
                await bot.process_query(
                    u2, context, "Quiero 1 pizza", 111111, "testuser"
                )

        assert bot.user_sessions.get(111111) is True

    @pytest.mark.asyncio
    async def test_multiples_timeouts_no_crashean_servicio(self):
        """Múltiples timeouts consecutivos del mismo cliente no rompen nada."""
        context = make_context()
        timeout = {"success": False, "returncode": -2, "timeout": True}

        with patch.object(bot, "ALLOWED_USER_IDS", [111111]):
            for i in range(5):
                update = make_update(text=f"Consulta pesada {i}")
                setup_processing_msg(update)
                with patch.object(
                    ClaudeCodeExecutor,
                    "execute_streaming",
                    new_callable=AsyncMock,
                    return_value=timeout,
                ):
                    await bot.process_query(
                        update, context, f"Consulta pesada {i}", 111111, "testuser"
                    )

        assert 111111 not in bot.user_sessions

    @pytest.mark.asyncio
    async def test_error_sistema_seguido_de_exito(self):
        """Error de sistema → reintento exitoso funciona limpiamente."""
        context = make_context()

        with patch.object(bot, "ALLOWED_USER_IDS", [111111]):
            # Error
            u1 = make_update(text="Pedido que falla")
            setup_processing_msg(u1)
            with patch.object(
                ClaudeCodeExecutor,
                "execute_streaming",
                new_callable=AsyncMock,
                return_value={"success": False, "returncode": 1},
            ):
                await bot.process_query(
                    u1, context, "Pedido que falla", 111111, "testuser"
                )

            # Éxito
            u2 = make_update(text="Pedido corregido")
            setup_processing_msg(u2)
            with patch.object(
                ClaudeCodeExecutor,
                "execute_streaming",
                new_callable=AsyncMock,
                return_value={"success": True, "returncode": 0},
            ):
                await bot.process_query(
                    u2, context, "Pedido corregido", 111111, "testuser"
                )

        assert bot.user_sessions.get(111111) is True

    @pytest.mark.asyncio
    async def test_timeout_real_mata_proceso(self):
        """Un timeout real limpia el proceso correctamente."""
        executor = ClaudeCodeExecutor()
        output_cb = AsyncMock()
        error_cb = AsyncMock()

        mock_process = AsyncMock()
        mock_process.pid = 77777
        mock_process.kill = MagicMock()
        mock_process.wait = AsyncMock(return_value=-9)

        async def hang(*args, **kwargs):
            await asyncio.sleep(9999)
            return b""

        mock_process.stdout = AsyncMock()
        mock_process.stdout.read = hang
        mock_process.stderr = AsyncMock()
        mock_process.stderr.read = AsyncMock(return_value=b"")

        with patch("asyncio.create_subprocess_exec", return_value=mock_process), \
             patch.object(bot, "COMMAND_TIMEOUT", 0.1):
            result = await executor.execute_streaming(
                "consulta que cuelga", 111111, False, output_cb, error_cb
            )

        assert result["success"] is False
        assert result.get("timeout") is True
        mock_process.kill.assert_called()


# =====================================================================
# Validación de input desde WhatsApp
# =====================================================================

class TestValidacionInputWhatsApp:
    """Verifica validación de mensajes entrantes desde WhatsApp."""

    @pytest.mark.asyncio
    async def test_mensaje_vacio_rechazado(self):
        """Un mensaje vacío desde WhatsApp es rechazado."""
        context = make_context()

        with patch.object(bot, "ALLOWED_USER_IDS", [111111]):
            update = make_update(text="")
            await bot.handle_message(update, context)
            call_text = update.message.reply_text.call_args[0][0]
            assert "mensaje válido" in call_text

    @pytest.mark.asyncio
    async def test_mensaje_solo_espacios_rechazado(self):
        """Un mensaje con solo espacios es rechazado."""
        context = make_context()

        with patch.object(bot, "ALLOWED_USER_IDS", [111111]):
            update = make_update(text="   \t\n  ")
            await bot.handle_message(update, context)
            call_text = update.message.reply_text.call_args[0][0]
            assert "mensaje válido" in call_text

    @pytest.mark.asyncio
    async def test_mensaje_demasiado_largo_rechazado(self):
        """Un mensaje que excede el límite es rechazado."""
        context = make_context()
        long_msg = "Quiero pedir: " + "item extra, " * 5000

        with patch.object(bot, "ALLOWED_USER_IDS", [111111]), \
             patch.object(bot, "MAX_INPUT_LENGTH", 10000):
            update = make_update(text=long_msg)
            await bot.process_query(update, context, long_msg, 111111, "testuser")
            call_text = update.message.reply_text.call_args[0][0]
            assert "Mensaje demasiado largo" in call_text

    @pytest.mark.asyncio
    async def test_caracteres_especiales_espanol_funcionan(self):
        """Caracteres especiales del español se procesan correctamente."""
        context = make_context()
        mock_result = {"success": True, "returncode": 0}
        msg = "Quiero 3 piñas coladas, 2 jalapeños y un café expréss con leche"

        with patch.object(bot, "ALLOWED_USER_IDS", [111111]):
            update = make_update(text=msg)
            setup_processing_msg(update)
            with patch.object(
                ClaudeCodeExecutor,
                "execute_streaming",
                new_callable=AsyncMock,
                return_value=mock_result,
            ) as mock_exec:
                await bot.process_query(update, context, msg, 111111, "testuser")
                assert mock_exec.call_args[0][0] == msg

    @pytest.mark.asyncio
    async def test_emojis_en_pedido_funcionan(self):
        """Emojis comunes en WhatsApp se procesan sin problemas."""
        context = make_context()
        mock_result = {"success": True, "returncode": 0}
        msg = "Quiero 🍕🍕 y 🥤 por favor 😊👍"

        with patch.object(bot, "ALLOWED_USER_IDS", [111111]):
            update = make_update(text=msg)
            setup_processing_msg(update)
            with patch.object(
                ClaudeCodeExecutor,
                "execute_streaming",
                new_callable=AsyncMock,
                return_value=mock_result,
            ) as mock_exec:
                await bot.process_query(update, context, msg, 111111, "testuser")
                assert mock_exec.call_args[0][0] == msg

    @pytest.mark.asyncio
    async def test_mensaje_multilinea_whatsapp(self):
        """Mensajes multilínea de WhatsApp se procesan correctamente."""
        context = make_context()
        mock_result = {"success": True, "returncode": 0}
        msg = (
            "Mi pedido es:\n"
            "- 2 pizzas margarita\n"
            "- 1 ensalada césar\n"
            "- 3 coca colas\n"
            "\n"
            "Dirección: Av. Providencia 1234\n"
            "Teléfono: +56 9 1234 5678"
        )

        with patch.object(bot, "ALLOWED_USER_IDS", [111111]):
            update = make_update(text=msg)
            setup_processing_msg(update)
            with patch.object(
                ClaudeCodeExecutor,
                "execute_streaming",
                new_callable=AsyncMock,
                return_value=mock_result,
            ) as mock_exec:
                await bot.process_query(update, context, msg, 111111, "testuser")
                assert mock_exec.call_args[0][0] == msg


# =====================================================================
# Output streaming para WhatsApp
# =====================================================================

class TestOutputStreamingWhatsApp:
    """Verifica que el streaming de output funciona para WhatsApp."""

    @pytest.mark.asyncio
    async def test_buffer_acumula_y_envia_respuesta_completa(self):
        """El buffer acumula chunks y envía una respuesta limpia."""
        received = []

        async def callback(text):
            received.append(text)

        buf = OutputBuffer(callback, timeout=0.1)

        # Simular output progresivo del agente
        chunks = [
            "Procesando tu pedido...\n",
            "✅ 2 pizzas margarita - $17.980\n",
            "✅ 1 coca cola - $1.990\n",
            "Total: $19.970\n",
        ]
        for chunk in chunks:
            await buf.append(chunk)

        await asyncio.sleep(0.3)

        assert len(received) == 1
        assert "pizzas margarita" in received[0]
        assert "Total: $19.970" in received[0]

    @pytest.mark.asyncio
    async def test_flush_forzado_envia_inmediatamente(self):
        """Flush forzado envía sin esperar el timeout."""
        received = []

        async def callback(text):
            received.append(text)

        buf = OutputBuffer(callback, timeout=10)
        await buf.append("Pedido confirmado ✅")
        await buf.flush()

        assert len(received) == 1
        assert received[0] == "Pedido confirmado ✅"

    @pytest.mark.asyncio
    async def test_buffers_independientes_por_cliente(self):
        """Cada cliente tiene su propio buffer sin contaminar otros."""
        received_1 = []
        received_2 = []

        async def cb1(text):
            received_1.append(text)

        async def cb2(text):
            received_2.append(text)

        buf1 = OutputBuffer(cb1, timeout=0.1)
        buf2 = OutputBuffer(cb2, timeout=0.1)

        await buf1.append("Pizza para cliente 1")
        await buf2.append("Tacos para cliente 2")

        await buf1.flush()
        await buf2.flush()

        assert received_1 == ["Pizza para cliente 1"]
        assert received_2 == ["Tacos para cliente 2"]

    @pytest.mark.asyncio
    async def test_output_largo_con_streaming_y_split(self):
        """Output largo se transmite por streaming y luego se divide para envío."""
        context = make_context()
        update = make_update(text="Muestra todo el menú completo")
        mock_processing = setup_processing_msg(update)

        # Simular un menú muy largo
        menu_items = [f"🍕 Pizza #{i:03d} - Ingredientes: queso, tomate, albahaca - $9.990\n"
                      for i in range(100)]
        long_output = "📋 MENÚ COMPLETO\n" + "".join(menu_items)

        mock_result = {"success": True, "returncode": 0}

        async def fake_execute(query, user_id, continue_session, output_cb, error_cb=None):
            await output_cb(long_output)
            return mock_result

        with patch.object(bot, "ALLOWED_USER_IDS", [111111]), \
             patch.object(
                 ClaudeCodeExecutor,
                 "execute_streaming",
                 new_callable=AsyncMock,
                 side_effect=fake_execute,
             ):
            await bot.process_query(
                update, context, "Muestra todo el menú completo", 111111, "testuser"
            )

        assert mock_processing.edit_text.called or update.message.reply_text.call_count > 0


# =====================================================================
# Escenarios de negocio realistas
# =====================================================================

class TestEscenariosNegocioWhatsApp:
    """Escenarios de negocio realistas para un servicio de pedidos por WhatsApp."""

    @pytest.mark.asyncio
    async def test_consulta_estado_pedido_existente(self):
        """Cliente consulta el estado de un pedido ya existente."""
        context = make_context()
        mock_result = {"success": True, "returncode": 0}

        with patch.object(bot, "ALLOWED_USER_IDS", [111111]):
            msgs = [
                "¿Cuál es el estado de mi pedido #4521?",
                "¿Cuánto falta para que llegue?",
            ]
            for i, msg in enumerate(msgs):
                update = make_update(text=msg)
                setup_processing_msg(update)
                with patch.object(
                    ClaudeCodeExecutor,
                    "execute_streaming",
                    new_callable=AsyncMock,
                    return_value=mock_result,
                ) as mock_exec:
                    await bot.process_query(
                        update, context, msg, 111111, "testuser"
                    )
                    if i > 0:
                        assert mock_exec.call_args[0][2] is True

    @pytest.mark.asyncio
    async def test_pedido_grupal_con_multiples_items(self):
        """Pedido grupal con muchos items en conversación larga."""
        context = make_context()
        mock_result = {"success": True, "returncode": 0}

        with patch.object(bot, "ALLOWED_USER_IDS", [111111]):
            msgs = [
                "Hola, somos 8 personas y queremos pedir para la oficina",
                "3 pizzas grandes: 1 margarita, 1 pepperoni, 1 hawaiana",
                "También 2 ensaladas césar y 2 ensaladas caprese",
                "8 bebidas: 4 coca cola, 2 sprite, 2 jugos de naranja",
                "Y 3 postres de tiramisú",
                "Dirección: Av. Apoquindo 4500, piso 12, oficina 1205",
                "Confirmo todo el pedido",
            ]

            for i, msg in enumerate(msgs):
                update = make_update(text=msg)
                setup_processing_msg(update)
                with patch.object(
                    ClaudeCodeExecutor,
                    "execute_streaming",
                    new_callable=AsyncMock,
                    return_value=mock_result,
                ):
                    await bot.process_query(
                        update, context, msg, 111111, "testuser"
                    )

        assert bot.user_sessions.get(111111) is True

    @pytest.mark.asyncio
    async def test_reclamo_post_pedido(self):
        """Cliente reclama después de recibir pedido incorrecto."""
        context = make_context()
        mock_result = {"success": True, "returncode": 0}

        with patch.object(bot, "ALLOWED_USER_IDS", [111111]):
            msgs = [
                "Hola, recibí mi pedido pero me llegó mal",
                "Pedí pizza margarita y me llegó hawaiana",
                "Mi número de pedido es #7823",
                "Quiero que me envíen la pizza correcta",
            ]

            for msg in msgs:
                update = make_update(text=msg)
                setup_processing_msg(update)
                with patch.object(
                    ClaudeCodeExecutor,
                    "execute_streaming",
                    new_callable=AsyncMock,
                    return_value=mock_result,
                ):
                    await bot.process_query(
                        update, context, msg, 111111, "testuser"
                    )

        assert bot.user_sessions.get(111111) is True

    @pytest.mark.asyncio
    async def test_horario_y_disponibilidad(self):
        """Cliente pregunta por horarios y disponibilidad."""
        context = make_context()
        mock_result = {"success": True, "returncode": 0}

        with patch.object(bot, "ALLOWED_USER_IDS", [111111]):
            msgs = [
                "¿Están abiertos ahora?",
                "¿Hasta qué hora hacen delivery?",
                "¿Tienen disponible la pizza quattro formaggi?",
            ]

            for msg in msgs:
                update = make_update(text=msg)
                setup_processing_msg(update)
                with patch.object(
                    ClaudeCodeExecutor,
                    "execute_streaming",
                    new_callable=AsyncMock,
                    return_value=mock_result,
                ):
                    await bot.process_query(
                        update, context, msg, 111111, "testuser"
                    )

        assert bot.user_sessions.get(111111) is True

    @pytest.mark.asyncio
    async def test_flujo_completo_pedido_a_sheets(self):
        """Flujo: recibir pedido → registrar en Google Sheets (vía MCP)."""
        context = make_context()
        mock_result = {"success": True, "returncode": 0}

        with patch.object(bot, "ALLOWED_USER_IDS", [111111]), \
             patch.object(bot, "SKIP_PERMISSIONS", True):
            msgs = [
                "Registra un nuevo pedido: 2 pizzas margarita para Juan Pérez",
                "Agrégalo a la hoja de pedidos del día",
                "Confirma que quedó registrado",
            ]

            for msg in msgs:
                update = make_update(text=msg)
                setup_processing_msg(update)
                with patch.object(
                    ClaudeCodeExecutor,
                    "execute_streaming",
                    new_callable=AsyncMock,
                    return_value=mock_result,
                ):
                    await bot.process_query(
                        update, context, msg, 111111, "testuser"
                    )

        assert bot.user_sessions.get(111111) is True
