<script lang="ts">
import { defineComponent, h } from 'vue'

const getIconSymbol = (name?: string) => {
  const n = (name || '').toLowerCase()
  if (n.includes('ticket')) return '🎫'
  if (n.includes('refresh') || n.includes('loading') || n.includes('sync')) return '🔄'
  if (n.includes('alert') || n.includes('warning')) return '⚠️'
  if (n.includes('filter')) return '🔍'
  if (n.includes('inbox')) return '📥'
  if (n.includes('plus') || n.includes('add')) return '➕'
  if (n.includes('check')) return '✓'
  if (n.includes('close') || n.includes('cancel')) return '✕'
  if (n.includes('magnify') || n.includes('search')) return '🔍'
  if (n.includes('user') || n.includes('account')) return '👤'
  if (n.includes('clock') || n.includes('time')) return '⏰'
  if (n.includes('folder')) return '📁'
  return '📌'
}

export const Icon = defineComponent({
  name: 'Icon',
  props: {
    icon: {
      type: String,
      default: ''
    }
  },
  // `class` no se declara como prop: Vue la hereda al <span> raíz (fallthrough)
  // y así acepta string, array u objeto como cualquier componente.
  setup(props) {
    return () => h('span', { class: 'inline-flex items-center justify-center' }, getIconSymbol(props.icon))
  }
})

export default Icon
</script>
