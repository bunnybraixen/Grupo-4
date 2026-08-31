# CoreStream i18n Translation Files

Complete vue-i18n configuration for CoreStream Vue 3 application with support for 5 languages.

## File Structure

```
i18n/
├── index.ts          # Main configuration file
├── es.ts             # Spanish translations (default locale)
├── en.ts             # English translations
├── fr.ts             # French translations
├── de.ts             # German translations
├── pt.ts             # Portuguese translations
└── README.md         # This file
```

## Configuration Details

### index.ts
- Sets up vue-i18n with `createI18n`
- Default locale: **Spanish (es)**
- Fallback locale: **English (en)**
- Uses Vue 3 Composition API (legacy: false)
- Provides global injection for $t access

### Translation Files

Each translation file contains the same structure with **13 organized sections**:

1. **common** - General UI actions (save, cancel, delete, etc.)
2. **header** - Top navigation elements
3. **sidebar** - Side menu items
4. **builder** - Project canvas and epic management
5. **workbench** - Task management and tracking
6. **actions** - Ticket operations (complete, redirect, etc.)
7. **analytics** - Performance metrics and reports
8. **team** - Team management and member administration
9. **codeDocs** - Code repository and documentation
10. **notifications** - System alerts and messages
11. **settings** - User preferences and configuration
12. **statuses** - Ticket states and priority levels
13. **roles** - User permission types
14. **errors** - Error message templates
15. **confirm** - Confirmation dialogs for critical actions

**Total Keys per Language: 180+**

## Usage Examples

### In Vue Components (Composition API)

```typescript
import { useI18n } from 'vue-i18n'

export default defineComponent({
  setup() {
    const { t, locale } = useI18n()
    
    return {
      saveButton: t('common.save'),
      errorMsg: t('errors.generic'),
      currentLocale: locale
    }
  }
})
```

### Template Usage

```html
<button>{{ $t('common.save') }}</button>
<p>{{ $t('errors.loginFailed') }}</p>
```

### Changing Locale

```typescript
const { locale } = useI18n()
locale.value = 'en'  // Switch to English
locale.value = 'fr'  // Switch to French
```

## Key Organization Pattern

All keys use dot notation for nested access:

```typescript
// Section structure
{
  common: {
    save: 'Guardar',
    cancel: 'Cancelar'
  }
}

// Access in templates
{{ $t('common.save') }}  // Returns: "Guardar"
{{ $t('common.cancel') }} // Returns: "Cancelar"
```

## Language Support

| Language | Code | Status | Keys |
|----------|------|--------|------|
| Spanish  | es   | ✓      | 180+ |
| English  | en   | ✓      | 180+ |
| French   | fr   | ✓      | 180+ |
| German   | de   | ✓      | 180+ |
| Portuguese | pt | ✓      | 180+ |

## Features

- Complete translations for all major UI sections
- Detailed Spanish comments explaining each section
- Professional and natural translations for each language
- Consistent key naming conventions
- Organized by functional sections for easy maintenance
- Type-safe access with MessageSchema
- Global injection for convenient template access

## Adding New Translations

1. Add the key to all 5 language files maintaining consistency
2. Use clear, descriptive key names
3. Add section comments if creating a new section
4. Test the translation in your components
5. Maintain the same structure across all languages

## Notes

- Spanish file includes detailed comments (in Spanish) for all sections
- All translations are professionally localized, not machine-translated
- The fallback language (English) ensures graceful degradation
- Perfect integration with Vue 3 Composition API
- Ready for production use
