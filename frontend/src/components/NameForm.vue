<script setup>
import {NAME_MAX_LENGTH} from '../constants.js'

defineProps({
  // button text, ex: 'create'
  label: {type: String, required: true},
  // shown while the input is empty
  placeholder: {type: String, default: ''},
  // from the parent's useButtonLock(), disables the button while a submit runs
  locked: {type: Boolean, default: false},
})

const emit = defineEmits(['submit'])

// the parent's v-model, kept by the parent so a failed submit keeps the typed text
const model = defineModel({type: String})
</script>

<template>
  <form
    class="name-form"
    @submit.prevent="emit('submit')"
  >
    <input
      v-model="model"
      :maxlength="NAME_MAX_LENGTH"
      :placeholder="placeholder"
      type="text"
    />
    <button
      :disabled="locked"
      class="btn-primary"
      type="submit"
    >
      {{ label }}
    </button>
  </form>
</template>

<style scoped>
.name-form {
  display: flex;
  flex-direction: row;
  justify-content: center;
  gap: var(--space-3);
}
</style>
