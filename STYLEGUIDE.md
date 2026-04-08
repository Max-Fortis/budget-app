# Iceberg Style Guide
System Documentation / Version 01

Live reference: run the app and visit `/styleguide`

---

## 01. Color Palette

| Token | Hex | Use |
|---|---|---|
| `--color-primary` | `#AB2E15` | Alerts, active states, CTA buttons |
| `--color-ink` | `#1B1C18` | Body text, headings, dark UI |
| `--color-paper` | `#FBF9F2` | Page background, nav bars |
| `--color-surface` | `#F6F4EC` | Cards, panels |
| `--color-muted` | `#E4E2DC` | Progress bar tracks, secondary bg |
| `--color-accent` | `#326270` | Positive states, stable indicators |
| `--color-warning` | `#775A00` | Caution states, category labels |
| `--color-outline` | `#E1BFB8` | Borders, dividers, archived badges |
| `--color-input-bg` | `#F0EEE7` | Form inputs |

---

## 02. Typography

| Role | Font | Size | Weight | Tracking | Case |
|---|---|---|---|---|---|
| Display | Space Grotesk | 60px | 700 | -3px | — |
| Headline LG | Space Grotesk | 48px | 700 | -2.4px | UPPER |
| Headline MD | Space Grotesk | 30px | 700 | — | — |
| Heading | Space Grotesk | 20px | 700 | -0.5px | UPPER |
| Data / Mono | Space Grotesk | 18px | 500 | — | — |
| Label | Space Grotesk | 12px | 700 | 1.2px | UPPER |
| Meta / Caption | Space Grotesk | 10px | 400 | 2px | UPPER |
| Body | Inter | 14px | 400 | — | — |
| Body Italic | Inter | 14px | 400 italic | — | — |

**Google Fonts import:** `Space Grotesk` (300–700) + `Inter` (regular, italic, 500, 600, 700)

---

## 03. Buttons

| Class | Background | Text | Border | Use |
|---|---|---|---|---|
| `btn-primary` | `#AB2E15` | white | — | Main CTA |
| `btn-primary[disabled]` | `#AB2E15` at 50% | white 70% | — | Unavailable action |
| `btn-secondary` | `#E4E2DC` | ink | `rgba(27,28,24,0.1)` | Secondary action |
| `btn-outlined` | transparent | `#AB2E15` | `#AB2E15` | Destructive or alternate |
| `btn-ghost` | transparent | ink | — | Inline actions |
| `btn-underline` | transparent | `#326270` | bottom only | Links, download |
| `btn-dark` | `#FBF9F2` | ink | — | On dark card backgrounds |
| `btn-archive` | transparent | muted | dashed | Low-priority actions |

All buttons: `font-family: Space Grotesk`, `font-weight: 700`, `font-size: 12px`, `letter-spacing: 1.2px`, `text-transform: uppercase`

---

## 04. Status Badges

| Class | Background | Text | Use |
|---|---|---|---|
| `badge-critical` | `#AB2E15` | white | Over budget, errors |
| `badge-pending` | `#E4E2DC` | ink | In progress |
| `badge-internal` | `#326270` | white | Stable, informational |
| `badge-archived` | transparent | `#59413C` | Inactive, historical |
| `badge-active` | transparent | `#AB2E15` | Live status dot |

---

## 05. Progress Bars

| State | Fill Color | Threshold | Label |
|---|---|---|---|
| Stable | `#326270` | < 80% of limit | "Looking good" |
| Warning | `#775A00` | 80–95% of limit | "Almost at limit" |
| Critical | `#AB2E15` | > 95% of limit | "Over budget" |
| Paid | `#1B1C18` | 100% | "Paid for the month" |

Track background: `#E4E2DC` (thin bar) or `#FBF9F2` with border (tall bar)

---

## 06. Cards

| Class | Background | Border | Use |
|---|---|---|---|
| `card` | `#F6F4EC` | `1px rgba(27,28,24,0.1)` | Default content card |
| `card-dark` | `#1B1C18` | — | CTA blocks, emphasis |
| `card-alert` | `#F6F4EC` | left `4px #AB2E15` | AI suggestions, alerts |

Card padding: `25px`

---

## 07. Form Inputs

- Background: `#F0EEE7`
- Border: none (flat style)
- Padding: `13px 16px`
- Font: Space Grotesk Regular, 14px
- Placeholder: `rgba(89,65,60,0.3)`
- Focus: inset box-shadow `0 0 0 1px #AB2E15`
- Labels: Space Grotesk, 10px, 1px tracking, UPPERCASE, color `#59413C`

---

## 08. Spacing Scale

| Token | Value |
|---|---|
| `--space-1` | 4px |
| `--space-2` | 8px |
| `--space-3` | 12px |
| `--space-4` | 16px |
| `--space-6` | 24px |
| `--space-8` | 32px |
| `--space-10` | 40px |
| `--space-12` | 48px |

Section gaps: 40–48px. Card padding: 24–32px. Element gaps: 8–16px.

---

## 09. Navigation

**Top bar:** `#FBF9F2` bg · `1px solid rgba(27,28,24,0.2)` border-bottom · `64px` height · `24px` horizontal padding

**Bottom nav:** `#FBF9F2` bg · `1px solid rgba(27,28,24,0.2)` border-top · `80px` height

**Active tab:** `2px solid #AB2E15` top border · text `#AB2E15`

**Inactive tab:** text `rgba(27,28,24,0.5)`

---

## 10. CSS Variables (reference)

All tokens are defined in `templates/styleguide.html`. When applying to the main app, move these to the top of `static/style.css`:

```css
:root {
  --color-primary:   #AB2E15;
  --color-ink:       #1B1C18;
  --color-paper:     #FBF9F2;
  --color-surface:   #F6F4EC;
  --color-muted:     #E4E2DC;
  --color-accent:    #326270;
  --color-warning:   #775A00;
  --color-outline:   #E1BFB8;
  --color-input-bg:  #F0EEE7;

  --font-display: 'Space Grotesk', sans-serif;
  --font-body:    'Inter', sans-serif;

  --space-1:  4px;
  --space-2:  8px;
  --space-3:  12px;
  --space-4:  16px;
  --space-6:  24px;
  --space-8:  32px;
  --space-10: 40px;
  --space-12: 48px;
}
```
