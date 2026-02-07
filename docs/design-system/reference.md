# PropHero Design System Reference

> Source: `github.com/PropHero-Tech/design-system`
> Tokens generated from Figma via `figma/tokens/figma-variables.json`
> Package: `@prophero-ds/web-tokens` + `@prophero-ds/web-react`

---

## Quick Reference

| Property | Value |
|----------|-------|
| **Font** | Inter |
| **Primary Color** | `#2050f6` (Blue 600) |
| **Background** | `#fafafa` (page), `#ffffff` (card) |
| **Foreground** | `#212121` (primary text) |
| **Base Spacing** | 4px (`x1`) |
| **Default Radius** | 8px (`r2`) |
| **Animation** | 120ms default, 150ms fast, 250ms base, 350ms slow |
| **Mobile Breakpoint** | 640px |

---

## Typography

| Style | Size | Weight | Line Height | Letter Spacing |
|-------|------|--------|-------------|----------------|
| **body** | 16px | 400 (regular) | 1.5 | -0.7px |
| **label** | 14px | 600 (semibold) | 1.43 | -0.5px |
| **title** | 24px | 600 (semibold) | 1.33 | -1.5px |

### Font Sizes

| Token | px |
|-------|----|
| `xs` | 12 |
| `sm` | 14 |
| `base` | 16 |
| `lg` | 18 |
| `xl` | 20 |
| `2xl` | 24 |
| `3xl` | 32 |
| `4xl` | 36 |
| `5xl` | 48 |

### Font Weights

| Token | Value |
|-------|-------|
| `regular` | 400 |
| `medium` | 500 |
| `semibold` | 600 |

---

## Spacing Scale

Base unit: **4px**

| Token | px | Token | px |
|-------|----|-------|----|
| `x0` | 0 | `x8` | 32 |
| `x05` | 2 | `x9` | 36 |
| `x1` | 4 | `x10` | 40 |
| `x1_5` | 6 | `x12` | 48 |
| `x2` | 8 | `x14` | 56 |
| `x2_5` | 10 | `x16` | 64 |
| `x3` | 12 | `x20` | 80 |
| `x4` | 16 | `x24` | 96 |
| `x5` | 20 | `x32` | 128 |
| `x6` | 24 | `x40` | 160 |
| `x7` | 28 | | |

### Layout Padding (Container)

| Token | px | Use |
|-------|-----|-----|
| `xs` | 16 | Mobile |
| `sm` | 32 | Small screens |
| `md` | 40 | Medium screens |
| `lg` | 80 | Large screens |
| `xl` | 100 | Extra large |
| `xxl` | 112 | Max width |

---

## Border Radius

| Token | px | Use |
|-------|-----|-----|
| `r0` | 0 | Sharp corners |
| `r1` | 4 | Subtle rounding |
| `r2` | 8 | **Default** (cards, inputs) |
| `r3` | 12 | Medium rounding |
| `r4` | 16 | Large rounding |
| `r6` | 24 | Extra large |
| `full` | 9999 | Pill shape |

---

## Elevation (Shadows)

| Token | CSS | Use |
|-------|-----|-----|
| `sm` | `0px 1px 2px rgba(0,0,0,0.05)` | Cards (subtle) |
| `level-1` | `0px 0px 16px rgba(0,0,0,0.04)` | Cards |
| `level-2` | `0px 0px 16px rgba(0,0,0,0.1)` | Floating elements |
| `level-3` | `0px 0px 24px rgba(0,0,0,0.16)` | Modals |
| `level-4` | `0px 0px 32px rgba(0,0,0,0.2)` | Overlays |

### Blur

| Token | CSS | Use |
|-------|-----|-----|
| `level-1` | `blur(8px)` | Soft background |
| `level-3` | `blur(16px)` | Overlays |
| `level-5` | `blur(32px)` | Modal backdrops |
| `level-8` | `blur(64px)` | Maximum blur |

---

## Transitions

### Duration

| Token | ms | Use |
|-------|-----|-----|
| `fast` | 150 | Micro-animations, hovers |
| `base` | 250 | Standard UI transitions |
| `slow` | 350 | Important state changes |

### Easing

| Token | CSS | Use |
|-------|-----|-----|
| `ease-in` | `cubic-bezier(0.4, 0, 1, 1)` | Elements entering |
| `ease-out` | `cubic-bezier(0, 0, 0.2, 1)` | Elements exiting |
| `ease-in-out` | `cubic-bezier(0.4, 0, 0.2, 1)` | State changes |

---

## Colors

### Semantic Backgrounds

| Token | Hex | Use |
|-------|-----|-----|
| `bg.page` | `#fafafa` | Page background |
| `bg.card` | `#ffffff` | Card background |
| `bg.elevated` | `#e4e4e7` | Elevated surfaces |
| `bg.disabled` | `#f5f5f5` | Disabled state |
| `bg.primary` | `#2050f6` | Primary actions |
| `bg.secondary` | `#212121` | Secondary/dark |
| `bg.primaryAlt` | `#eef4ff` | Light primary (ghost hover) |
| `bg.error` | `#ef4444` | Error state |
| `bg.errorAlt` | `#fee2e2` | Error background (light) |
| `bg.warning` | `#f97316` | Warning state |
| `bg.warningAlt` | `#ffedd5` | Warning background (light) |
| `bg.success` | `#22c55e` | Success state |
| `bg.successAlt` | `#dcfce7` | Success background (light) |

### Semantic Foreground (Text)

| Token | Hex | Use |
|-------|-----|-----|
| `fg.primary` | `#212121` | Primary text |
| `fg.secondary` | `#71717a` | Secondary/muted text |
| `fg.tertiary` | `#a1a1aa` | Tertiary/placeholder |
| `fg.disabled` | `#a3a3a3` | Disabled text |
| `fg.white` | `#ffffff` | Text on dark/primary bg |
| `fg.brand` | `#2050f6` | Brand/link color |
| `fg.brandHover` | `#1337e2` | Brand hover |
| `fg.error` | `#b91c1c` | Error text |
| `fg.warning` | `#c2410c` | Warning text |
| `fg.success` | `#15803d` | Success text |
| `fg.info` | `#162eb7` | Info text |
| `fg.divider` | `#e4e4e7` | Divider lines |

### Semantic Borders

| Token | Hex | Use |
|-------|-----|-----|
| `border.default` | `#d1d1d1` | Default borders |
| `border.focus` | `#5d5d5d` | Focus ring |
| `border.error` | `#dc2626` | Error state |
| `border.warning` | `#ea580c` | Warning state |
| `border.success` | `#16a34a` | Success state |
| `border.brand` | `#2050f6` | Brand/primary |
| `border.disabled` | `#e7e7e7` | Disabled borders |

### Primary Color Scale

| Token | Hex |
|-------|-----|
| `primary50` | `#eef4ff` |
| `primary100` | `#d9e7ff` |
| `primary200` | `#cfe1ff` |
| `primary300` | `#8dbbff` |
| `primary400` | `#5895ff` |
| `primary500` | `#316eff` |
| `primary600` | `#2050f6` (**main**) |
| `primary700` | `#1337e2` |
| `primary800` | `#162eb7` |
| `primary900` | `#182c90` |
| `primary950` | `#141d57` |

---

## Component Tokens

### Button Colors

| Variant | bg default | bg hover | bg active | fg |
|---------|-----------|----------|-----------|-----|
| **Primary** | `#2050f6` | `#1337e2` | `#162eb7` | `#ffffff` |
| **Secondary** | `#d9e7ff` | `#eef4ff` | `#cfe1ff` | `#2050f6` |
| **Ghost** | transparent | `#eef4ff` | `#cfe1ff` | `#2050f6` |
| **Destructive** | `#dc2626` | `#b91c1c` | `#991b1b` | `#ffffff` |
| **Destructive Ghost** | transparent | `#f5f5f5` | `#e4e4e7` | `#b91c1c` |
| **Disabled** | `#e5e5e5` | - | - | `#737373` |

### Input Colors

| State | Value |
|-------|-------|
| bg | `#fafafa` |
| bg hover | `#f5f5f5` |
| bg active | `#e4e4e7` |
| bg disabled | `#e4e4e7` |
| fg | `#212121` |
| fg placeholder | `#a1a1aa` |
| border | `#d4d4d8` |
| border focus | `#71717a` |
| border error | `#dc2626` |
| border primary | `#2050f6` |
| radius | `8px` |

### Alert Colors

| Variant | bg | fg | border |
|---------|-----|-----|--------|
| **Success** | `#dcfce7` | `#15803d` | `#bbf7d0` |
| **Error** | `#fee2e2` | `#b91c1c` | `#fecaca` |
| **Warning** | `#ffedd5` | `#c2410c` | `#fed7aa` |
| **Info** | `#eef4ff` | `#162eb7` | `#cfe1ff` |

### Card

| Property | Value |
|----------|-------|
| bg | `#ffffff` |
| border | `#e4e4e7` |
| radius | `8px` |

---

## Components API Reference

### Button (`PropHeroButton`)

| Prop | Type | Default | Values |
|------|------|---------|--------|
| `variant` | enum | `primary` | `primary`, `secondary`, `ghost`, `destructive`, `destructiveGhost` |
| `size` | enum | - | `sm`, `md`, `lg` |
| `type` | enum | `button` | `button`, `iconButton` |
| `iconName` | string | - | Icon name from DS icon set |
| `iconPosition` | enum | - | `left`, `right` |
| `loading` | boolean | `false` | - |
| `stretch` | boolean | `false` | Full width |

### Card (`PropHeroCard`)

| Prop | Type | Default | Values |
|------|------|---------|--------|
| `size` | enum | - | `sm`, `md`, `lg` |
| `headerAlignment` | enum | `left` | `left`, `center` |
| `footerLayout` | enum | - | `horizontal`, `vertical`, `fill` |
| `clickable` | boolean | `false` | - |
| `hoverable` | boolean | `false` | - |
| `title` | ReactNode | - | - |
| `description` | ReactNode | - | - |
| `headerEnd` | ReactNode | - | Slot at header end |
| `primaryAction` | ReactNode | - | - |
| `secondaryAction` | ReactNode | - | - |

### Dialog (`PropHeroDialog`)

| Prop | Type | Default | Values |
|------|------|---------|--------|
| `size` | enum | `sm` | `sm` (400px), `md` (600px), `lg` (800px), `xl` (968px) |
| `visible` | boolean | `false` | - |
| `closeOnBackdropClick` | boolean | `true` | - |
| `closeOnEscape` | boolean | `true` | - |
| `mobileCloseVariant` | enum | `back` | `back`, `close`, `none` |
| `header` | ReactNode | - | - |
| `footer` | ReactNode | - | - |
| `primaryAction` | ReactNode | - | - |
| `secondaryAction` | ReactNode | - | - |

Mobile breakpoint: **640px**

### Alert (`PropHeroAlert`)

| Prop | Type | Default | Values |
|------|------|---------|--------|
| `variant` | enum | `warning` | `info`, `warning`, `success`, `error` |
| `size` | enum | `lg` | `sm`, `lg` |
| `title` | string | - | - |
| `description` | string | - | - |
| `showIcon` | boolean | `true` | - |
| `showClose` | boolean | `false` | - |
| `showActions` | boolean | `false` | - |
| `actionLabel` | string | `Undo` | - |
| `stretch` | boolean | `false` | Full width |

Icons by variant: info=`info`, warning=`circle-alert`, success=`circle-check`, error=`circle-alert`

### Badge (`PropHeroBadge`)

| Prop | Type | Default | Values |
|------|------|---------|--------|
| `badgeStyle` | enum | `standard` | `standard`, `dot` |
| `color` | enum | `default` | `default`, `primary`, `brand`, `error`, `warning`, `success` |
| `count` | number/string | - | Priority over text |
| `text` | string | - | Priority over children |

### TextInput (`PropHeroTextInput`)

| Prop | Type | Default | Values |
|------|------|---------|--------|
| `variant` | enum | `default` | `default`, `error` |
| `label` | string | - | - |
| `optionalText` | string | - | Shows "(optional)" or custom |
| `helperText` | string | - | Below input |
| `leftIcon` | string | - | Icon name |
| `rightIcon` | string | - | Icon name |
| `suffix` | string | - | Text suffix |
| `disabled` | boolean | `false` | - |

### Select (`PropHeroSelect`)

| Prop | Type | Default | Values |
|------|------|---------|--------|
| `state` | enum | `default` | `default`, `filled`, `disabled`, `focus`, `active`, `active-filled`, `error` |
| `label` | string | - | - |
| `placeholder` | string | - | - |
| `items` | array | - | `{ id, label, value, disabled? }` |
| `errorMessage` | string | - | - |
| `disabled` | boolean | `false` | - |

### TabBar (`PropHeroTabBar`)

| Prop | Type | Default | Values |
|------|------|---------|--------|
| `variant` | enum | `main` | `main`, `segmented` |
| `value` | string | - | Controlled |
| `items` | array | - | `{ value, label, iconName?, notification?, tag? }` |

### Toast (`PropHeroToast`)

Imperative API via ref: `show(toast)`, `dismiss(id)`, `clear()`

| Prop | Type | Default | Values |
|------|------|---------|--------|
| `position` | enum | `bottom` | `top`, `bottom` |
| `maxVisible` | number | `3` | - |
| `defaultDurationMs` | number | `4000` | 6000 with action |

Toast input: `{ state, title, description, actionLabel, onAction, durationMs, showClose }`

States: `default`, `success`, `warning`, `error`

A11y: warning/error use `role="alert"` + `aria-live="assertive"`

### Accordion (`PropHeroAccordion`)

| Prop | Type | Default | Values |
|------|------|---------|--------|
| `items` | array | - | `{ title, titlePrefix?, content, disabled? }` |
| `multiple` | boolean | `false` | Allow multiple open |
| `withDivider` | boolean | - | Show dividers |

### Sidebar (`PropHeroSidebar`)

| Prop | Type | Default | Values |
|------|------|---------|--------|
| `groups` | array | - | `{ title?, items: SidebarItem[] }` |
| `activeItem` | string | - | Item id |
| `collapsed` | boolean | - | Controlled |
| `showCollapseToggle` | boolean | `true` | - |
| `logo` | ReactNode | - | - |
| `user` | object | - | `{ name?, email? }` |
| `footerMenu` | object | - | `{ title?, items: FooterItem[] }` |

SidebarItem: `{ id, label, icon?, href?, children?, progress?, counter? }`

### Navbar (`PropHeroNavbar`)

| Prop | Type | Default | Values |
|------|------|---------|--------|
| `device` | enum | `desktop` | `mobile`, `desktop` |
| `title` | string | - | - |
| `showBack` | boolean | `true` | - |
| `primaryButtonLabel` | string | - | - |
| `secondaryButtonLabel` | string | - | - |
| `slot` | ReactNode | - | Custom content (e.g., search) |
| `showDivider` | boolean | `true` | - |

### Other Components

| Component | Key Props |
|-----------|-----------|
| **Autocomplete** | Search input with dropdown suggestions |
| **Calendar** | Date grid picker |
| **Checkbox** | Standard checkbox with label |
| **DatePicker** | Input + Calendar combination |
| **Divider** | Horizontal separator line |
| **ElementHeader** | Section header with optional actions |
| **FileItem** | File upload display item |
| **FooterActions** | Action buttons container (for dialogs/pages) |
| **Icon** | DS icon renderer |
| **Item** | List item with icon, text, actions |
| **ItemGroup** | Grouped list items |
| **Link** | Styled anchor/link |
| **PageHeading** | Page-level heading with breadcrumbs |
| **PhoneInput** | Phone number with country code |
| **ProgressCircle** | Circular progress indicator |
| **RadioButton** | Standard radio |
| **RadioButtonIcon** | Radio with icon variant |
| **SearchBar** | Search input with clear |
| **SectionHeading** | Section title with optional actions |
| **Skeleton** | Loading placeholder |
| **Spinner** | Loading spinner |
| **Stepper** | Multi-step progress |
| **Switch** | Toggle switch |
| **Tag** | Label/tag chip |
| **Text** | Typography component |
| **TextArea** | Multi-line text input |
| **Uploader** | File upload with drag & drop |

---

## UX Review Checklist

When reviewing designs or implementations against this design system:

### Colors
- [ ] Using semantic tokens, not raw hex values
- [ ] Primary actions use `#2050f6`, destructive use `#dc2626`
- [ ] Text hierarchy: primary `#212121` > secondary `#71717a` > tertiary `#a1a1aa`
- [ ] Backgrounds: page `#fafafa`, cards `#ffffff`
- [ ] Status colors consistent: success=green, error=red, warning=orange, info=blue

### Typography
- [ ] Font is Inter
- [ ] Body text: 16px/400, Labels: 14px/600, Titles: 24px/600
- [ ] Using design system font sizes (not arbitrary values)

### Spacing
- [ ] Using 4px base grid (multiples of 4)
- [ ] Container padding follows responsive scale (16px mobile -> 112px xxl)
- [ ] Consistent internal spacing (8px, 12px, 16px, 24px)

### Components
- [ ] Using DS components instead of custom implementations
- [ ] Button variants match intent (primary for main action, ghost for secondary)
- [ ] Inputs have proper states (default, focus, error, disabled)
- [ ] Alerts use correct variant for message type
- [ ] Dialogs use appropriate size for content

### States & Feedback
- [ ] All interactive elements have hover, active, focus, disabled states
- [ ] Error states show red border + error message
- [ ] Loading states use Spinner or Skeleton
- [ ] Toast for transient feedback, Alert for persistent messages
- [ ] Transitions use DS durations (150ms fast, 250ms base, 350ms slow)

### Accessibility
- [ ] Color contrast meets WCAG AA
- [ ] Focus states visible
- [ ] Toast warning/error use `role="alert"` + `aria-live="assertive"`
- [ ] Dialog traps focus and supports Escape to close
- [ ] Interactive elements are keyboard accessible

### Layout
- [ ] Card radius: 8px, Input radius: 8px
- [ ] Shadows follow elevation scale (sm < level-1 < level-2 < level-3)
- [ ] Mobile breakpoint at 640px
- [ ] Sidebar collapsible on smaller screens
