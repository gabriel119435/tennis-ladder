<script setup>
import {computed, nextTick, ref} from 'vue'
import {useI18n} from 'vue-i18n'

// custom select: a trigger button opens a list of option buttons, the picked value goes to the parent's v-model
const props = defineProps({
  // [{value: 3, label: 'text shown'}], [] while the parent's list is still loading
  options: {type: Array, default: () => []},
  // shown while nothing is picked
  placeholder: {type: String, default: ''},
  // last list entry that empties the pick instead of being an option
  clearLabel: {type: String, default: ''},
})

// the parent's v-model, undefined while nothing is picked
const model = defineModel({type: Number})

const {t} = useI18n()

// whether the option list is visible
const open = ref(false)
// list opens above the trigger when it doesn't fit below
const up = ref(false)
// keyboard and hover highlighted entry, an index into entries
const highlighted = ref(0)

// root (wraps the trigger) and list (the open options) are measured for the flip
// vue fills each one with its element from the same named ref="..." in the template
const root = ref()
const list = ref()

// undefined while nothing is picked, shows the placeholder
const selected = computed(() => props.options.find((o) => o.value === model.value))

// trigger text: the picked option's label or the placeholder
const shown = computed(() => (selected.value ? selected.value.label : props.placeholder))

// every label the trigger can show, stacked to size it to the widest
const labels = computed(() => [props.placeholder, ...props.options.map((o) => o.label)])

// options plus the clear entry at the end, its undefined value empties the pick
const entries = computed(() =>
  props.clearLabel ? [...props.options, {value: undefined, label: props.clearLabel}] : props.options,
)

async function show() {
  open.value = true
  // starts on the picked option, the first one while nothing is picked
  highlighted.value = Math.max(0, props.options.indexOf(selected.value))
  // the list exists only after the next render, then its height can be measured
  await nextTick()

  // flips when the list doesn't fit below the trigger and there's more room above
  // getBoundingClientRect: the trigger's position in px from the window's top edge
  const trigger = root.value.getBoundingClientRect()
  // innerHeight: visible window height in px
  const freeSpaceBelowTrigger = window.innerHeight - trigger.bottom
  // offsetHeight: the list's rendered height in px, padding and border included
  up.value = list.value.offsetHeight > freeSpaceBelowTrigger && trigger.top > freeSpaceBelowTrigger
}

function close() {
  open.value = false
}

function pick(value) {
  model.value = value
  close()
}

// enter and space on the focused trigger fire a native click, its @click opens or closes the list
// while closed, down opens, while open, up and down move the highlight wrapping at the ends, enter picks, esc closes
function onKeydown(e) {
  if (!open.value) {
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      show()
    }
    return
  }

  if (e.key === 'Escape') {
    close()
    return
  }

  // empty list: nothing to move to or pick
  if (!entries.value.length) return

  if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
    // stops the page from scrolling with the arrows
    e.preventDefault()
    const step = e.key === 'ArrowDown' ? 1 : -1
    highlighted.value = (highlighted.value + step + entries.value.length) % entries.value.length
  } else if (e.key === 'Enter') {
    // stops the native trigger click, it would reopen the list
    e.preventDefault()
    pick(entries.value[highlighted.value].value)
  }
}

// tab away: focus moved to an element outside the select, close the list
// null target is a mouse click, left to v-click-outside so a click on an option still picks it
function onFocusOut(e) {
  if (e.relatedTarget && !e.currentTarget.contains(e.relatedTarget)) close()
}
</script>

<template>
  <div
    ref="root"
    v-click-outside="close"
    class="app-select"
    @focusout="onFocusOut"
    @keydown="onKeydown"
  >
    <button
      :class="{open}"
      class="app-select-trigger"
      type="button"
      @click="open ? close() : show()"
    >
      <span
        :class="{'app-select-placeholder': !selected}"
        class="toggle-button"
      >
        <!-- one span per label, only the shown one visible -->
        <span
          v-for="(label, i) in labels"
          :key="i"
          :class="{hidden: label !== shown}"
          >{{ label }}</span
        >
      </span>
      <span class="app-select-arrow">&#9662;</span>
    </button>
    <div
      v-if="open"
      ref="list"
      :class="{up}"
      class="app-select-list"
    >
      <!-- no entries: one disabled entry says so, nothing to pick -->
      <button
        v-if="!entries.length"
        class="app-select-option"
        disabled
        type="button"
      >
        {{ t('select.empty') }}
      </button>
      <!-- tabindex -1: tab skips the options, focus stays on the trigger -->
      <button
        v-for="(entry, i) in entries"
        :key="i"
        :class="{active: i === highlighted}"
        class="app-select-option"
        tabindex="-1"
        type="button"
        @click="pick(entry.value)"
        @mouseenter="highlighted = i"
      >
        {{ entry.label }}
      </button>
    </div>
  </div>
</template>
