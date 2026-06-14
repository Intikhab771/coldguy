---
name: Coldguy Brutalist System
colors:
  surface: '#f9f9f9'
  surface-dim: '#dadada'
  surface-bright: '#f9f9f9'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f3f4'
  surface-container: '#eeeeee'
  surface-container-high: '#e8e8e8'
  surface-container-highest: '#e2e2e2'
  on-surface: '#1a1c1c'
  on-surface-variant: '#5d3f3d'
  inverse-surface: '#2f3131'
  inverse-on-surface: '#f0f1f1'
  outline: '#916f6b'
  outline-variant: '#e6bdb9'
  surface-tint: '#c00019'
  primary: '#bb0018'
  on-primary: '#ffffff'
  primary-container: '#e1262c'
  on-primary-container: '#fffbff'
  inverse-primary: '#ffb3ad'
  secondary: '#5e6300'
  on-secondary: '#ffffff'
  secondary-container: '#e1ec3a'
  on-secondary-container: '#636900'
  tertiary: '#5c5c5c'
  on-tertiary: '#ffffff'
  tertiary-container: '#747474'
  on-tertiary-container: '#fcfcfc'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdad6'
  primary-fixed-dim: '#ffb3ad'
  on-primary-fixed: '#410003'
  on-primary-fixed-variant: '#930010'
  secondary-fixed: '#e1ec3a'
  secondary-fixed-dim: '#c5cf16'
  on-secondary-fixed: '#1b1d00'
  on-secondary-fixed-variant: '#464a00'
  tertiary-fixed: '#e2e2e2'
  tertiary-fixed-dim: '#c6c6c6'
  on-tertiary-fixed: '#1b1b1b'
  on-tertiary-fixed-variant: '#474747'
  background: '#f9f9f9'
  on-background: '#1a1c1c'
  surface-variant: '#e2e2e2'
typography:
  headline-xl:
    fontFamily: Anybody
    fontSize: 64px
    fontWeight: '900'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Anybody
    fontSize: 40px
    fontWeight: '800'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Anybody
    fontSize: 32px
    fontWeight: '800'
    lineHeight: '1.2'
  headline-md:
    fontFamily: Anybody
    fontSize: 24px
    fontWeight: '700'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Space Mono
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Space Mono
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  label-bold:
    fontFamily: Space Mono
    fontSize: 14px
    fontWeight: '700'
    lineHeight: '1.2'
  code-sm:
    fontFamily: Space Mono
    fontSize: 13px
    fontWeight: '400'
    lineHeight: '1.4'
spacing:
  unit: 4px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 40px
  stack-gap: 12px
  border-width: 3px
---

## Brand & Style

This design system embodies a **Hard Brutalist** aesthetic, specifically tailored for a platform that prioritizes raw efficiency and unapologetic directness. The personality is high-energy, functional, and "industrial-digital." It rejects the softness of modern SaaS trends in favor of high-contrast interfaces that command attention.

The target audience consists of outbound sales professionals and growth hackers who value speed and clarity over ornamentation. The emotional response is one of urgency and mechanical precision. The style utilizes heavy black borders, "neo-brutalist" hard shadows, and a saturated color palette to create a UI that feels physically constructed rather than digitally rendered.

## Colors

The palette is aggressive and high-contrast, designed to make information "pop" against a stark background.

- **Primary (#FF3E3E):** A deep, saturated red used for critical actions, urgency, and brand highlights.
- **Secondary (#F4FF4D):** A piercing bright yellow/neon used for high-visibility alerts, highlights, and secondary CTAs.
- **Tertiary (#000000):** Pure black, used for all borders, shadows, and primary text to ensure maximum legibility and structural definition.
- **Neutral (#FFFFFF):** Pure white for surface areas, providing the high-contrast base for the brutalist elements.

Avoid gradients or soft transitions. Use solid blocks of color separated by heavy strokes.

## Typography

The typography system relies on a "Variable/Monospace" pairing to reinforce the industrial vibe.

- **Headlines:** Use **Anybody** with ultra-bold weights (800-900). It should feel heavy and loud. For large display text, use tight letter spacing to increase the sense of density.
- **Body & Interface:** Use **Space Mono** for all functional text, including emails, data tables, and labels. The monospaced nature emphasizes the "cold" and "technical" aspect of automated emailing.
- **Formatting:** All-caps should be used for labels and secondary buttons to enhance the brutalist structure. Headlines should remain in sentence case but utilize heavy weights for impact.

## Layout & Spacing

The layout is built on a rigid, visible grid. Elements do not float; they are anchored by heavy borders and consistent gaps.

- **Grid:** Use a 12-column fluid grid for desktop with 24px gutters. Use a 4-column grid for mobile.
- **Visual Dividers:** Instead of whitespace alone, use 3px black horizontal and vertical rules to separate sections.
- **Padding:** Maintain generous internal padding within boxed elements (minimum 24px) to ensure that the heavy borders do not crowd the content.
- **Rhythm:** Use a 4px base unit. All spacing values should be multiples of 4 or 8 to maintain a "blocky" feel.

## Elevation & Depth

This design system rejects shadows with blur. Depth is communicated through **Hard Offset Shadows** and **Tonal Layering**.

- **Hard Shadows:** Use a solid black offset (e.g., `4px 4px 0px 0px #000000`). When an element is "pressed," the shadow should disappear, and the element should translate 4px down and to the right to simulate a physical button press.
- **Stark Outlines:** Every container must have a minimum 2px or 3px solid black border.
- **Layering:** Backgrounds are white, but interactive cards can use the Primary or Secondary colors as solid fills. There is no concept of "ambient" lighting; everything is flat or physically extruded.

## Shapes

The shape language is strictly **Sharp**. 

- **Corners:** Use 0px border-radius for all primary UI elements (buttons, inputs, cards, modals). This reinforces the "cold," "industrial" nature of the brand.
- **Exceptions:** Icons may contain curves, but they should be framed within square containers with heavy borders. 
- **Strokes:** Use consistent 3px strokes for all containers.

## Components

### Buttons
Buttons are solid blocks of color (Primary or Secondary) with a 3px black border and a 4px black hard shadow. Text is bold, uppercase Space Mono. On hover, the background color can shift to a slightly lighter version, but the border and shadow remain constant until clicked.

### Input Fields
Inputs are white boxes with 3px black borders. Placeholder text is in 50% opacity Space Mono. Focused states should have a Secondary (Yellow) background to highlight the active task.

### Cards
Cards use a white or light-grey background with a 3px black border and a 6px hard shadow. Titles inside cards are always bold and separated from content by a 2px horizontal line.

### Chips & Status Indicators
Chips are used for lead status (e.g., "Cold," "Hot," "Replied"). They use sharp corners, a 2px border, and high-contrast fills. "Hot" leads should be Primary Red; "Pending" should be Secondary Yellow.

### List Items
Lists are separated by 3px solid black lines. Hovering over a list item should trigger a "fill" animation where the background becomes Secondary Yellow, making the item highly visible for selection.

### Tooltips
Tooltips are strictly black boxes with white Space Mono text. No rounded corners, no transparency.