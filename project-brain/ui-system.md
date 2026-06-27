# UI System

## Design System Philosophy

Our design system is built on the principle of **consistency through constraint**. Rather than providing infinite flexibility, we establish a finite set of composable, well-tested primitives that handle 95% of interface needs. The remaining 5% is accommodated through escape hatches that are clearly documented and audited.

### Core Principles

1. **Progressive Enhancement** — Every component must work without JavaScript. JavaScript enhances, never replaces, core functionality.
2. **Accessibility First** — Accessibility is not a layer on top of design; it is the foundation. Every component is built to WCAG 2.1 AA at minimum before any visual polish is applied.
3. **Composition Over Configuration** — Components are composed from smaller primitives rather than configured through sprawling prop APIs. This keeps surface area small and testing straightforward.
4. **Performance as a Feature** — Bundle size budgets, render cycle limits, and layout shift targets are enforced at the CI level. Components that exceed thresholds must be optimized before merging.
5. **Design Token Driven** — Every visual property flows from design tokens. Hard-coded values are prohibited in component code. Tokens are the single source of truth for the visual language.

## Component Hierarchy and Architecture

### Layer Structure

```
Tokens (design primitives)
  └─ Foundations (themes, breakpoints, typography scale)
       └─ Primitives (Button, Input, Text, Box, Stack)
            └─ Composites (FormField, Card, Dialog, Table)
                 └─ Patterns (DataTable, Wizard, SearchResults)
                      └─ Pages (Dashboard, Settings, Profile)
```

### Component Classification

| Layer | Examples | Responsibility | Can Use |
|-------|----------|----------------|---------|
| Primitives | Button, Input, Text, Icon, Box, Stack, Spinner | Atomic UI elements, no business logic | Tokens only |
| Composites | FormField, Card, Dialog, DataTable, Tabs | Combine primitives, introduce layout patterns | Primitives + Tokens |
| Patterns | SearchResults, Wizard, NotificationCenter | Solve specific UX problems, may use state | Composites + Primitives |
| Pages | UserDashboard, InvoiceList | Route-level compositions, data fetching | Patterns + Composites |

### Component Contract

Every component must implement:

```typescript
interface UIComponent<T = HTMLElement> {
  // Required
  className?: string;
  style?: React.CSSProperties;
  id?: string;
  role?: string;
  'data-testid'?: string;
  'aria-label'?: string;

  // Events (optional, component-specific)
  onChange?: (value: any) => void;
  onBlur?: (event: FocusEvent<T>) => void;
  onFocus?: (event: FocusEvent<T>) => void;
}
```

### Naming Conventions

- **Primitives**: PascalCase, no prefix (`Button`, `Input`, `Text`)
- **Composites**: PascalCase, domain context (`FormField`, `DataTable`)
- **Hooks**: camelCase, `use` prefix (`useDebounce`, `useMediaQuery`)
- **Context Providers**: PascalCase, `Provider` suffix (`ThemeProvider`, `FormProvider`)
- **Higher-Order Components**: camelCase, `with` prefix (`withAuthentication`, `withTracking`)

## UI Component Catalog

### Primitives

#### `Box`
The foundational layout primitive. Renders a div with themed spacing, background, border, and shadow support. All other layout components compose from Box.

Props: `padding`, `margin`, `background`, `border`, `shadow`, `display`, `position`, `width`, `height`, `overflow`

#### `Stack`
Manages vertical or horizontal spacing between children. Replaces manual margin hacks. Supports responsive direction changes.

Props: `direction` (row/column), `spacing` (token-based), `align`, `justify`, `wrap`, `splitAfter` (inserts auto-margin after nth child)

#### `Text`
Renders typographic content with automatic heading hierarchy mapping. Supports semantic HTML element mapping via the `as` prop.

Props: `variant` (h1-h6, body, caption, label, code), `color`, `align`, `weight`, `truncate` (ellipsis overflow), `as` (semantic element override)

#### `Button`
Triggerable action element. Supports multiple variants, sizes, loading state, and icon composition. Always includes visible focus ring.

Props: `variant` (primary, secondary, tertiary, danger, ghost), `size` (sm, md, lg), `loading` (shows spinner, disables), `icon`, `iconPosition`, `fullWidth`, `type` (button/submit/reset), `disabled`

States: default, hover, active, focus-visible, loading, disabled

#### `Input`
Text input with integrated validation display, character count, and prefix/suffix adornments.

Props: `value`, `onChange`, `error` (message string), `hint` (helper text), `label`, `placeholder`, `maxLength`, `prefix` (icon/element), `suffix`, `disabled`, `readOnly`, `required`, `autoFocus`

States: default, focus, filled, error, disabled, readonly, loading (skeleton)

#### `Select`
Native-feel select with optional search filtering and multi-select support. Uses a popover pattern rather than native select for consistent styling.

Props: `options` (array of {value, label, disabled, group}), `value`, `onChange`, `placeholder`, `searchable`, `multiple`, `error`, `hint`, `disabled`, `loading`, `clearable`

#### `Checkbox` / `Radio`
Form control primitives with indeterminate state support for Checkbox. Both compose from a shared `TogglePrimitive`.

Props: `checked`, `onChange`, `indeterminate` (checkbox only), `value`, `disabled`, `error`

#### `Switch`
Binary toggle control. Visually distinct from Checkbox for setting-enabled scenarios.

Props: `checked`, `onChange`, `disabled`, `loading`, `label` (left/right placement), `hint`

#### `Spinner`
Loading indicator. Uses CSS animations only (no JS timer) for performance. Supports size variants and overlay mode.

Props: `size` (sm, md, lg), `label` (sr-only text for screen readers), `overlay` (semi-transparent backdrop)

#### `Icon`
SVG icon wrapper with automatic sizing and color inheritance from text color.

Props: `name` (icon registry key), `size`, `color`, `title` (accessible label), `decorative` (marks as presentation-only for screen readers)

### Composites

#### `FormField`
Wraps an input primitive with label, error message, hint text, and required indicator. Orchestrates aria-describedby relationships between input and feedback elements.

Props: `label`, `required`, `error`, `hint`, `children` (the input), `layout` (vertical/horizontal), `tooltip`

#### `Card`
Surface container with optional header, footer, and action areas. Supports interactive and non-interactive variants.

Props: `title`, `subtitle`, `actions` (header actions), `footer`, `padding`, `variant` (elevated, outlined, flat), `interactive` (adds hover/click styles), `onClick`

#### `Dialog`
Modal dialog with focus trapping, escape-to-close, click-outside-to-close, and body scroll locking. Returns focus to trigger element on close.

Props: `open`, `onClose`, `title`, `description` (aria-describedby content), `size`, `closeOnOverlay`, `closeOnEscape`, `preventBodyScroll`, `children`

Sub-components: `Dialog.Header`, `Dialog.Body`, `Dialog.Footer`

#### `DataTable`
Tabular data display with sort, filter, pagination, column resizing, row selection, and sticky header support. Virtualized for large datasets.

Props: `columns`, `data`, `pageSize`, `sortable`, `filterable`, `selectable`, `onRowClick`, `loading`, `emptyState`, `errorState`

#### `Tabs`
Tabbed interface with keyboard navigation (arrow keys, Home, End). Supports dynamic tab addition/removal and lazy loading.

Props: `tabs` (array of {id, label, content, disabled, badge}), `activeTab`, `onChange`, `variant` (underline, pills, segmented), `lazy` (mount on first visit)

#### `Toast`
Transient notification with auto-dismiss, stacked positioning, and action button support.

Props: `message`, `variant` (success, error, warning, info), `action` ({label, onClick}), `duration`, `onDismiss`, `position`

#### `Tooltip`
Hover/focus tooltip with delay, placement, and arrow support. Uses a portal to avoid overflow clipping.

Props: `content`, `placement` (top, bottom, left, right, auto), `delay` (show/hide), `disabled`, `maxWidth`

#### `Accordion`
Collapsible content sections with optional multiple expansion. Supports animated open/close and nested accordions.

Props: `items` (array of {title, content, disabled}), `multiple`, `defaultExpanded`, `onChange`

#### `Breadcrumbs`
Navigation trail with truncation and collapse behavior for deep paths.

Props: `items` (array of {label, href, icon}), `maxItems` (enables collapse after N), `separator` (custom icon)

### Patterns

#### `SearchResults`
Combined search input, filter panel, results list, pagination, and result count. Manages URL search params for shareable URLs.

#### `Wizard`
Multi-step form with progress indicator, step validation, and navigation guards. Supports linear and non-linear step progression.

#### `NotificationCenter`
Dropdown panel showing user notifications with read/unread state, grouping, and mark-all-read action.

#### `DataFilterPanel`
Sidebar/overlay panel with filter controls, applied filter chips, and reset action. Composes from FormField primitives.

## Styling Approach

We use **Tailwind CSS v3** with a custom design token plugin for styling, combined with `clsx` for conditional class merging.

### Rationale

- **Utility-first** reduces CSS bloat and eliminates dead code via PurgeCSS
- **Design token integration** via Tailwind's `extend` theme configuration
- **Component-scoped variants** via Tailwind's arbitrary variant support
- **Zero runtime** — all styles are extracted at build time

### CSS Architecture

```
tailwind.config.js          # Token definitions, plugins, presets
└─ postcss.config.js         # PostCSS pipeline
    └─ src/styles/
        ├─ base.css           # Reset, global styles, font-face
        ├─ components.css     # Component-specific layer
        └─ utilities.css      # Custom utility classes
```

### Custom Variants

```css
/* Loading state variant */
@custom-variant loading (&[data-loading="true"]);

/* Validation state variants */
@custom-variant error (&[data-error="true"]);
@custom-variant success (&[data-success="true"]);
```

### Class Naming Convention

Components use a consistent pattern for conditional classes:

```typescript
// Within each component:
const classes = clsx(
  // Base styles (always applied)
  "base-class",
  // Variant styles
  variant === "primary" && "variant-primary",
  // Size styles
  size === "lg" && "size-lg",
  // State styles
  disabled && "opacity-50 cursor-not-allowed",
  // Custom className prop
  className
);
```

## Design Tokens

### Color Palette

```json
{
  "colors": {
    "neutral": {
      "50": "#fafafa",
      "100": "#f5f5f5",
      "200": "#e5e5e5",
      "300": "#d4d4d4",
      "400": "#a3a3a3",
      "500": "#737373",
      "600": "#525252",
      "700": "#404040",
      "800": "#262626",
      "900": "#171717",
      "950": "#0a0a0a"
    },
    "primary": {
      "50": "#eff6ff",
      "100": "#dbeafe",
      "200": "#bfdbfe",
      "300": "#93c5fd",
      "400": "#60a5fa",
      "500": "#3b82f6",
      "600": "#2563eb",
      "700": "#1d4ed8",
      "800": "#1e40af",
      "900": "#1e3a8a",
      "950": "#172554"
    },
    "success": { "50": "#f0fdf4", "500": "#22c55e", "600": "#16a34a", "700": "#15803d" },
    "warning": { "50": "#fffbeb", "500": "#f59e0b", "600": "#d97706", "700": "#b45309" },
    "error":   { "50": "#fef2f2", "500": "#ef4444", "600": "#dc2626", "700": "#b91c1c" },
    "info":    { "50": "#f0f9ff", "500": "#0ea5e9", "600": "#0284c7", "700": "#0369a1" }
  }
}
```

### Semantic Color Tokens

| Token | Light Value | Dark Value | Usage |
|-------|-------------|------------|-------|
| `color-bg-primary` | neutral-50 | neutral-950 | Page background |
| `color-bg-secondary` | neutral-100 | neutral-900 | Card, surface backgrounds |
| `color-bg-tertiary` | neutral-200 | neutral-800 | Hovered surfaces |
| `color-text-primary` | neutral-900 | neutral-50 | Primary text |
| `color-text-secondary` | neutral-500 | neutral-400 | Secondary text |
| `color-text-inverse` | neutral-50 | neutral-900 | Text on dark backgrounds |
| `color-border` | neutral-200 | neutral-700 | Default borders |
| `color-border-focus` | primary-500 | primary-400 | Focus ring color |
| `color-border-error` | error-500 | error-400 | Error state borders |

### Typography

```json
{
  "fontFamily": {
    "sans": ["Inter", "system-ui", "-apple-system", "sans-serif"],
    "mono": ["JetBrains Mono", "Fira Code", "monospace"]
  },
  "fontSize": {
    "xs": ["0.75rem", { "lineHeight": "1rem" }],
    "sm": ["0.875rem", { "lineHeight": "1.25rem" }],
    "base": ["1rem", { "lineHeight": "1.5rem" }],
    "lg": ["1.125rem", { "lineHeight": "1.75rem" }],
    "xl": ["1.25rem", { "lineHeight": "1.75rem" }],
    "2xl": ["1.5rem", { "lineHeight": "2rem" }],
    "3xl": ["1.875rem", { "lineHeight": "2.25rem" }],
    "4xl": ["2.25rem", { "lineHeight": "2.5rem" }],
    "5xl": ["3rem", { "lineHeight": "1.16" }]
  },
  "fontWeight": {
    "normal": 400,
    "medium": 500,
    "semibold": 600,
    "bold": 700
  }
}
```

### Spacing Scale

Based on a 4px grid (0.25rem increments):

| Token | Value | Rem |
|-------|-------|-----|
| `spacing-0` | 0 | 0 |
| `spacing-1` | 4px | 0.25rem |
| `spacing-2` | 8px | 0.5rem |
| `spacing-3` | 12px | 0.75rem |
| `spacing-4` | 16px | 1rem |
| `spacing-5` | 20px | 1.25rem |
| `spacing-6` | 24px | 1.5rem |
| `spacing-8` | 32px | 2rem |
| `spacing-10` | 40px | 2.5rem |
| `spacing-12` | 48px | 3rem |
| `spacing-16` | 64px | 4rem |
| `spacing-20` | 80px | 5rem |
| `spacing-24` | 96px | 6rem |

### Breakpoints

| Breakpoint | Min Width | Target |
|------------|-----------|--------|
| `sm` | 640px | Large phones, portrait tablets |
| `md` | 768px | Tablets, small laptops |
| `lg` | 1024px | Laptops, desktops |
| `xl` | 1280px | Wide desktops |
| `2xl` | 1536px | Ultra-wide displays |

### Shadows

| Token | Value | Usage |
|-------|-------|-------|
| `shadow-sm` | `0 1px 2px 0 rgb(0 0 0 / 0.05)` | Cards, subtle elevation |
| `shadow` | `0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)` | Default card shadow |
| `shadow-md` | `0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)` | Dropdowns, popovers |
| `shadow-lg` | `0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)` | Modals, dialogs |
| `shadow-xl` | `0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)` | Full-screen overlays |

### Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `rounded-sm` | 0.125rem | Checkbox, badge |
| `rounded` | 0.25rem | Input, button (sm) |
| `rounded-md` | 0.375rem | Button (default), card |
| `rounded-lg` | 0.5rem | Dialog, large card |
| `rounded-xl` | 0.75rem | Full-screen modal |
| `rounded-2xl` | 1rem | Feature cards |
| `rounded-full` | 9999px | Pill, avatar, badge |

## Accessibility Standards

### Compliance Target

WCAG 2.1 Level AA is the minimum standard. Level AAA is targeted for:
- Color contrast in text content
- Sign language for pre-recorded media
- Extended audio descriptions

### Implementation Requirements

1. **Focus Management**
   - Every interactive element must have a visible focus indicator (minimum 2px offset ring)
   - Focus order must follow DOM order (tabindex="-1" only for off-screen elements)
   - Modal dialogs must trap focus and restore on close
   - Skip-to-content link must be the first focusable element

2. **Color and Contrast**
   - Text-to-background contrast ratio: 4.5:1 minimum (AA), 7:1 target (AAA)
   - Non-text elements (icons, borders): 3:1 minimum
   - Do not rely solely on color to convey information
   - Support forced colors mode via `forced-color-adjust`

3. **Screen Reader Support**
   - All images must have `alt` text (empty `alt=""` for decorative)
   - ARIA landmarks used for page structure (banner, main, navigation, complementary, contentinfo)
   - Form inputs must have associated labels via `aria-labelledby` or `<label>`
   - Dynamic content changes announced via `aria-live` regions
   - Custom controls must have appropriate `role` and `aria-*` attributes

4. **Keyboard Navigation**
   - All functionality must be operable through keyboard
   - No keyboard traps — focus must be able to move away from any element
   - Custom keyboard shortcuts must be remappable and documented
   - Tab order follows logical reading order

5. **Motion and Animation**
   - Respect `prefers-reduced-motion` — disable or reduce all animations
   - No flashing content between 2-55 Hz (photosensitive epilepsy risk)
   - All motion must have a purpose (not purely decorative)

6. **Forms and Errors**
   - Error messages must be programmatically associated with their input
   - Form validation feedback must be announced to screen readers
   - Required fields must be indicated both visually and programmatically

### Testing Accessibility

```
Automated: axe-core in CI (blocking on violations, warning on best practices)
Manual:   Screen reader testing (VoiceOver, NVDA) per feature
          Keyboard-only testing per feature
          Zoom testing (200%, 400%)
          High contrast mode testing
```

## Responsive Design Strategy

### Approach: Mobile-First

All styles are mobile-first by default, with breakpoint-specific overrides applied via Tailwind's responsive prefixes (`sm:`, `md:`, `lg:`, `xl:`, `2xl:`).

### Layout Patterns

1. **Stack-to-Side**: On mobile, elements stack vertically. On desktop, they arrange side-by-side.
2. **Full-width to Contain**: Content is full-width on mobile, progressively constrained by max-width containers on larger screens.
3. **Bottom Sheet to Dialog**: Modals render as bottom sheets on mobile (full-screen or near-full-screen), as centered dialogs on desktop.
4. **Hamburger to Nav**: Navigation collapses to a hamburger menu on mobile, horizontal nav bar on desktop.
5. **Card Grid**: Cards go from single-column (mobile) to 2-column (tablet) to 3+ column (desktop).

### Breakpoint Usage Rules

- Do not introduce a breakpoint for a single component
- Breakpoints exist to serve layout, not individual component whims
- If a component needs a custom breakpoint value, reconsider the design
- Test at every breakpoint boundary (±1px) to ensure no gaps

### Content Strategy

- Text truncation at mobile sizes for secondary content
- Progressive disclosure: show essential content first, expand on interaction
- Touch targets minimum 44x44px on touch devices
- Horizontal scrolling is forbidden in viewport content areas

## State Management

### State Categories

Every data-driven component must handle the following states:

#### Loading

```typescript
// Pattern: Use skeleton placeholders, not spinners
<Card>
  <Card.Skeleton lines={3} />   // Mimics content shape
</Card>

// Exception: Actions use button-level spinners
<Button loading>Save</Button>

// Skeleton rules:
// - Match closest approximate dimensions of real content
// - Use neutral-200 background with shimmer animation
// - Never show skeletons for more than 10s without fallback
```

#### Empty

```typescript
<DataTable
  data={[]}
  emptyState={
    <EmptyState
      icon={<InboxIcon />}
      title="No results found"
      description="Try adjusting your search or filter criteria."
      action={<Button onClick={resetFilters}>Reset Filters</Button>}
    />
  }
/>
```

#### Error

```typescript
<ErrorBoundary fallback={ErrorFallback}>
  <DataTable ... />
</ErrorBoundary>

// Inline error state:
{error && (
  <InlineError
    message="Failed to load data"
    details={error.message}
    retry={refetch}
  />
)}
```

#### Success / Empty Data

Even on success, the data may be empty. This is distinct from the initial empty state (which implies no query has been made). Distinguish:
- **Initial state**: User hasn't searched yet — show guidance
- **Empty result**: Search returned zero results — suggest alternatives
- **Success with data**: Normal rendering

### Data Fetching State Machine

```
idle -> loading -> success (with data)
                 -> success (empty)
                 -> error -> loading (retry)
```

## Form Handling Patterns

### Architecture

Forms use React Hook Form for state management with Zod for schema validation.

```typescript
const schema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
});

type FormData = z.infer<typeof schema>;

function LoginForm() {
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: FormData) => {
    // Submit logic
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      <FormField label="Email" error={errors.email?.message}>
        <Input {...register("email")} type="email" autoComplete="email" />
      </FormField>
      <FormField label="Password" error={errors.password?.message}>
        <Input {...register("password")} type="password" autoComplete="current-password" />
      </FormField>
      <Button type="submit" loading={isSubmitting}>Sign In</Button>
    </form>
  );
}
```

### Form Conventions

1. **`noValidate`** on `<form>` — we control validation display
2. **`autoComplete`** on all inputs — required for password managers
3. **Error display**: Field-level errors shown below input, form-level errors shown above submit button
4. **Disabled submit**: Buttons are never disabled (users need to understand why). Show inline errors instead.
5. **Dirty tracking**: Warn before navigating away with unsaved changes
6. **Debounced validation**: On blur for field-level, on change for form-level only after first blur

## Animation and Transition Guidelines

### Principles

- **Purposeful**: Every animation must communicate something (hierarchy, state change, spatial relationship)
- **Subtle**: Duration 150-300ms for most interactions, 300-500ms for page transitions
- **Performant**: Use `transform` and `opacity` only (GPU-composited properties)
- **Accessible**: Respect `prefers-reduced-motion` — provide static equivalents

### Approved Durations

| Context | Duration | Easing |
|---------|----------|--------|
| Micro-interactions (hover, focus) | 150ms | ease-out |
| Element enter/exit (tooltip, dropdown) | 200ms | ease-out |
| Layout shifts (accordion, expand) | 250ms | ease-in-out |
| Page transitions | 300ms | ease-in-out |
| Overlay enter (modal) | 250ms | ease-out |
| Overlay exit | 200ms | ease-in |

### Animation Types

```css
/* Fade */
@keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }
@keyframes fade-out { from { opacity: 1; } to { opacity: 0; } }

/* Slide */
@keyframes slide-up { from { transform: translateY(8px); opacity: 0; } }
@keyframes slide-down { from { transform: translateY(-8px); opacity: 0; } }

/* Scale */
@keyframes scale-in { from { transform: scale(0.95); opacity: 0; } }

/* Shimmer (for skeletons) */
@keyframes shimmer { 0% { transform: translateX(-100%); } 100% { transform: translateX(100%); } }
```

## Testing UI Components

### Testing Strategy

| Test Type | Tool | Scope | When |
|-----------|------|-------|------|
| Unit | Vitest + Testing Library | Individual component logic | Every PR |
| Accessibility | jest-axe + axe-core | Automated a11y checks | Every PR |
| Visual | Chromatic / Percy | Visual regression | Every PR |
| Integration | Vitest + MSW | Component interaction flows | Feature branches |
| E2E | Playwright | Critical user journeys | Pre-release |

### Component Test Template

```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe } from 'jest-axe';

describe('Button', () => {
  it('renders with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
  });

  it('shows loading state and disables interaction', () => {
    render(<Button loading>Saving</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
    expect(screen.getByTestId('spinner')).toBeInTheDocument();
  });

  it('has no accessibility violations', async () => {
    const { container } = render(<Button>Accessible</Button>);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('calls onClick when clicked', async () => {
    const onClick = vi.fn();
    render(<Button onClick={onClick}>Click</Button>);
    await userEvent.click(screen.getByRole('button'));
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('does not call onClick when disabled', async () => {
    const onClick = vi.fn();
    render(<Button disabled onClick={onClick}>Click</Button>);
    await userEvent.click(screen.getByRole('button'));
    expect(onClick).not.toHaveBeenCalled();
  });
});
```

### Visual Regression Testing

All components have corresponding Storybook stories covering:
- Default state
- All variants
- All sizes
- Loading state
- Error state
- Disabled state
- Keyboard focus state
- Mobile viewport
- RTL layout
- High contrast mode

### Testing Checklist

- [ ] Renders without crashing
- [ ] Handles null/undefined props gracefully
- [ ] Displays loading state correctly
- [ ] Displays error state correctly
- [ ] Displays empty state correctly
- [ ] Keyboard navigation works
- [ ] Screen reader announces dynamic changes
- [ ] Focus management is correct (for modals, dropdowns)
- [ ] No color contrast violations
- [ ] Respects prefers-reduced-motion
- [ ] Touch targets are minimum 44x44px
- [ ] Works at all breakpoints (visual check)
