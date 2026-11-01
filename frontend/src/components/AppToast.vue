<script setup>
import {useToast} from '../composables/generic/useToast.js'

const {message} = useToast()
</script>

<template>
  <!-- transition tag fades in on v-if insert, delays v-if removal until fade-out ends -->
  <!-- toast name links it to the fade css -->
  <Transition name="toast">
    <div
      v-if="message"
      class="app-toast"
    >
      {{ message }}
    </div>
  </Transition>
</template>
