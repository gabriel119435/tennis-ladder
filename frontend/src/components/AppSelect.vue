<script setup>
import {computed, nextTick, ref} from 'vue'
import {useI18n} from 'vue-i18n'

const props = defineProps({
  // [{value: 3, label: 'text shown'}], empty while loading
  options: {type: Array, default: () => []},
  placeholder: {type: String, default: ''},
  clearLabel: {type: String, default: ''},
})

const model = defineModel({type: Number})
const {t} = useI18n()

const open = ref(false)
// list opens above the trigger when it doesn't fit below
const up = ref(false)
// index of keyboard|hover highlighted entry
const highlighted = ref(0)

// select and list are measured for the flip. vue fills them with ref in template
const select = ref()
const list = ref()

const selected = computed(() => props.options.find((o) => o.value === model.value))
const shown = computed(() => (selected.value ? selected.value.label : props.placeholder))
const allLabels = computed(() => [props.placeholder, ...props.options.map((o) => o.label)])
const allOptions = computed(() =>
  props.clearLabel ? [...props.options, {value: undefined, label: props.clearLabel}] : props.options,
)

// opens above only when list doesn't fit below and above has more room
async function show() {
  open.value = true
  highlighted.value = Math.max(0, props.options.indexOf(selected.value))
  await nextTick()

  // getBoundingClientRect: position in px from top
  // innerHeight: visible window height in px
  // offsetHeight: rendered height in px
  const selectRect = select.value.getBoundingClientRect()
  const spaceBelowTrigger = window.innerHeight - selectRect.bottom
  up.value = list.value.offsetHeight > spaceBelowTrigger && selectRect.top > spaceBelowTrigger
}

function close() {
  open.value = false
}

function pick(value) {
  model.value = value
  close()
}

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

  if (!allOptions.value.length) return

  if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
    e.preventDefault()
    const step = e.key === 'ArrowDown' ? 1 : -1
    highlighted.value = (highlighted.value + step + allOptions.value.length) % allOptions.value.length
  } else if (e.key === 'Enter') {
    e.preventDefault()
    pick(allOptions.value[highlighted.value].value)
  }
}

// currentTarget: this element. relatedTarget: element getting focus
function onFocusOut(e) {
  if (e.relatedTarget && !e.currentTarget.contains(e.relatedTarget)) close()
}
</script>

<template>
  <div
    ref="select"
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
        <span
          v-for="(label, i) in allLabels"
          :key="i"
          :class="{hidden: label !== shown}"
          >{{ label }}</span
        >
      </span>
      <span>&#9662;</span>
    </button>
    <div
      v-if="open"
      ref="list"
      :class="{up}"
      class="app-select-list"
    >
      <button
        v-if="!allOptions.length"
        class="app-select-option"
        disabled
        type="button"
      >
        {{ t('select.empty') }}
      </button>
      <!-- tabindex -1: tab moves away from select, not within the list -->
      <button
        v-for="(entry, i) in allOptions"
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

<style scoped>
.app-select {
  /* relative: .app-select-list's reference point */
  position: relative;
  display: inline-block;
}

.app-select-trigger {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  background: var(--color-bg-2);
  border: var(--border-width) solid var(--color-b-1);
  color: inherit;
}

.app-select-trigger.open,
.app-select-trigger:hover {
  border-color: var(--color-b-2);
  box-shadow: var(--shadow);
}

/* .c1 > .c2: c2 directly inside c1 */
.toggle-button > .hidden {
  height: 0;
}

.app-select-placeholder {
  color: var(--color-fg-1);
}

.app-select-list {
  /* absolute: top and left measured from closest parent with position set, .app-select */
  position: absolute;
  top: calc(100% + var(--space-1));
  /* horizontal centering */
  left: var(--center);
  transform: translateX(var(--center-neg));
  min-width: 100%;
  width: max-content;
  max-width: calc(100vw - 2 * var(--space-2));
  background: var(--color-bg-2);
  border: var(--border-width) solid var(--color-b-1);
  border-radius: var(--border-radius-0);
  box-shadow: var(--shadow);
  z-index: var(--z-index-0);
  /* keeps rectangular highlights inside rounded list */
  overflow: hidden;
}

.app-select-list.up {
  top: auto;
  bottom: calc(100% + var(--space-1));
}

.app-select-option {
  display: block;
  width: 100%;
  background: transparent;
  color: inherit;
  border-radius: 0;
}

.app-select-option.active {
  background: var(--color-bg-3);
}
</style>
