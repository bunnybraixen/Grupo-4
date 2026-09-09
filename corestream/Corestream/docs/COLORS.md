# CoreStream — Guía de Colores y Estilos

> Basado en el Brand Guide de **Alloxentric** (Nov 2020).  
> Stack frontend: **Vue 3 + Tailwind CSS**.

---

## 🎨 Paleta Principal

### Lime (Color Corporativo — Primario)
| Uso | Hex | CSS Variable sugerida |
|-----|-----|-----------------------|
| Full / 100% | `#ADEA4B` | `--color-lime` |
| 90% | `#B5EC5D` | `--color-lime-90` |
| 80% | `#BDEE6F` | `--color-lime-80` |
| 70% | `#C6F081` | `--color-lime-70` |
| 60% | `#CEF293` | `--color-lime-60` |
| 50% | `#D6F4A5` | `--color-lime-50` |
| 40% | `#DEF7B7` | `--color-lime-40` |
| 30% | `#E6F9C9` | `--color-lime-30` |
| 20% | `#EFFBDB` | `--color-lime-20` |
| 10% | `#F7FDED` | `--color-lime-10` |

> **Pantone:** P 7487C  
> **CMYK:** C35 M0 Y89 K0

---

### Teal (Color Secundario)
| Uso | Hex | CSS Variable sugerida |
|-----|-----|-----------------------|
| Full / 100% | `#06B7B2` | `--color-teal` |
| 90% | `#1FBEBA` | `--color-teal-90` |
| 80% | `#38C5C1` | `--color-teal-80` |
| 70% | `#51CDC9` | `--color-teal-70` |
| 60% | `#6AD4D1` | `--color-teal-60` |
| 50% | `#82DBD8` | `--color-teal-50` |
| 40% | `#9BE2E0` | `--color-teal-40` |
| 30% | `#B4E9E8` | `--color-teal-30` |
| 20% | `#CDF1F0` | `--color-teal-20` |
| 10% | `#E6F8F7` | `--color-teal-10` |

> **Pantone:** P 3262C  
> **CMYK:** C74 M2 Y36 K0

---

### Dark Teal / Darker Teal (Variantes oscuras)
| Nombre | Hex | CSS Variable sugerida |
|--------|-----|-----------------------|
| Dark Teal | `#046B74` | `--color-dark-teal` |
| Darker Teal | `#049A95` | `--color-darker-teal` |

---

### Dark Gray (Fondo / Neutro)
| Uso | Hex | CSS Variable sugerida |
|-----|-----|-----------------------|
| Full / 100% | `#142730` | `--color-dark-gray` |
| 90% | `#2B3D45` | `--color-dark-gray-90` |
| 80% | `#435259` | `--color-dark-gray-80` |
| 70% | `#5A686E` | `--color-dark-gray-70` |
| 60% | `#727D83` | `--color-dark-gray-60` |
| 50% | `#899397` | `--color-dark-gray-50` |
| 40% | `#A1A9AC` | `--color-dark-gray-40` |
| 30% | `#B8BEC1` | `--color-dark-gray-30` |
| 20% | `#D0D4D6` | `--color-dark-gray-20` |
| 10% | `#E7E9EA` | `--color-dark-gray-10` |

> **Pantone:** P 5395  
> **CMYK:** C87 M69 Y57 K64

---

## 🌡️ Colores de Acento

| Nombre | Hex | Uso sugerido |
|--------|-----|--------------|
| Warm 1 (Magenta) | `#C1108B` | Alertas, badges críticos |
| Warm 2 (Rosa) | `#D07AB8` | Estados secundarios warm |
| Warm 3 (Rosa claro) | `#E8B4DA` | Fondos suaves warm |
| Cold 1 (Azul fuerte) | `#1106C6` | Links, acciones primarias cold |
| Cold 2 (Azul medio) | `#2058D8` | Botones secondary cold |
| Cold 3 (Azul claro) | `#82A6F7` | Indicadores, tags cold |

> ⚠️ Usar acentos con moderación — el Lime y Teal son los dominantes de la marca.

---

## 🖊️ Tipografía

| Contexto | Fuente | Peso (font-weight) |
|----------|--------|--------------------|
| Print & Digital | **Domus** *(Adobe Font)* | 200 (body) / 200–600 (títulos) |
| Web | **Nunito** *(Google Font)* | Light, Regular, Light Bold, Regular Bold |
| Microsoft / Office | **Calibri** *(MS Font)* | Light, Regular, Semibold |

```css
/* Importar en tu proyecto Vue */
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700&display=swap');

body {
  font-family: 'Nunito', sans-serif;
  font-weight: 300; /* Light — body */
}
```

---

## 🖼️ Reglas de Uso del Logo

| Versión del logo | Fondos permitidos |
|-----------------|-------------------|
| **Negro** | Blanco, Lime full, Teal 10–30%, Dark Gray 10–20% |
| **Blanco** | Negro, Teal full, Lime 10–30%, Dark Gray 40–100% |
| **Full Color / Teal** | Solo blanco |
| **Lime** | Solo blanco |

> ❌ No usar el logo con transparencia.  
> ❌ No usar negro sobre fondos oscuros.  
> ❌ No usar blanco sobre fondos claros.

---

## 🧩 Tokens CSS sugeridos para Tailwind (tailwind.config.js)

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        lime: {
          DEFAULT: '#ADEA4B',
          90: '#B5EC5D',
          80: '#BDEE6F',
          70: '#C6F081',
          60: '#CEF293',
          50: '#D6F4A5',
          40: '#DEF7B7',
          30: '#E6F9C9',
          20: '#EFFBDB',
          10: '#F7FDED',
        },
        teal: {
          DEFAULT: '#06B7B2',
          90: '#1FBEBA',
          80: '#38C5C1',
          70: '#51CDC9',
          60: '#6AD4D1',
          50: '#82DBD8',
          40: '#9BE2E0',
          30: '#B4E9E8',
          20: '#CDF1F0',
          10: '#E6F8F7',
          dark: '#046B74',
          darker: '#049A95',
        },
        'dark-gray': {
          DEFAULT: '#142730',
          90: '#2B3D45',
          80: '#435259',
          70: '#5A686E',
          60: '#727D83',
          50: '#899397',
          40: '#A1A9AC',
          30: '#B8BEC1',
          20: '#D0D4D6',
          10: '#E7E9EA',
        },
        accent: {
          'warm-1': '#C1108B',
          'warm-2': '#D07AB8',
          'warm-3': '#E8B4DA',
          'cold-1': '#1106C6',
          'cold-2': '#2058D8',
          'cold-3': '#82A6F7',
        },
      },
      fontFamily: {
        sans: ['Nunito', 'Calibri', 'sans-serif'],
      },
    },
  },
}
```

---

## 💡 Combinaciones recomendadas para CoreStream UI

| Elemento | Fondo | Texto / Ícono |
|----------|-------|---------------|
| Header / Navbar | `dark-gray` (`#142730`) | `lime` (`#ADEA4B`) o blanco |
| Sidebar | `dark-gray-90` (`#2B3D45`) | `teal-30` (`#B4E9E8`) |
| Botón primario | `lime` (`#ADEA4B`) | `dark-gray` (`#142730`) |
| Botón secundario | `teal` (`#06B7B2`) | Blanco |
| Badges / Tags | `teal-20` (`#CDF1F0`) | `teal-dark` (`#046B74`) |
| Alertas / Urgente | `accent-warm-1` (`#C1108B`) | Blanco |
| Cards | `dark-gray-80` (`#435259`) | `dark-gray-10` (`#E7E9EA`) |
| Fondo de página | `dark-gray` (`#142730`) | — |
| Links | `teal` (`#06B7B2`) | — |
| Estado activo | `lime-70` (`#C6F081`) | `dark-gray` (`#142730`) |

---

*Fuente: Alloxentric Quick Style Guide — Nov 2020*