<template>
  <component
    :is="resolved"
    :size="size"
    :class="iconClass"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  Folder, Database, Monitor, Link, Home, Shield, Globe, Code,
  Server, Cloud, Zap, Box, Package, Settings, Users, Star,
  Heart, Bell, Lock, Key, Cpu, Briefcase, Layers, Rocket,
  GitBranch, Terminal
} from 'lucide-vue-next'

const ICONS: Record<string, object> = {
  Folder, Database, Monitor, Link, Home, Shield, Globe, Code,
  Server, Cloud, Zap, Box, Package, Settings, Users, Star,
  Heart, Bell, Lock, Key, Cpu, Briefcase, Layers, Rocket,
  GitBranch, Terminal
}

const props = withDefaults(defineProps<{
  icon?: string
  size?: number
  iconClass?: string
}>(), {
  icon: '',
  size: 20,
  iconClass: ''
})

const resolved = computed(() => ICONS[props.icon] ?? Folder)
</script>
