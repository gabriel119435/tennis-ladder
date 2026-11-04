<script setup>
import {useToast} from '../composables/generic/useToast.js'

const {message} = useToast()
</script>

<template>
  <!-- transition tag fades in on v-if insert, delays v-if removal until fade-out ends -->
  <Transition name="toast">
    <div
      v-if="message"
      class="app-toast"
    >
      {{ message }}
    </div>
  </Transition>
</template>

<style scoped>
.app-toast {
  position: fixed;
  bottom: var(--space-5);
  /* horizontal centering */
  left: var(--center);
  transform: translateX(var(--center-neg));
  padding: var(--space-4) var(--space-5);
  border-radius: var(--border-radius-1);
  font-size: var(--font-1);
  color: var(--color-fg-inverse);
  background: var(--color-toast-bg-danger);
  width: max-content;
  /* vw = viewport width = visible browser area. 100vw = its full width */
  max-width: calc(100vw - var(--space-4) * 2);
  /* in front of all other content */
  z-index: var(--z-index-0);
}

/* name="toast" on Transition: vue adds toast-enter-* on fading in, toast-leave-* on fading out */
.toast-enter-active,
.toast-leave-active {
  transition: opacity var(--duration-1);
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
}
</style>
