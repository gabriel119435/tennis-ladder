// v-click-outside="fn": calls fn on any click outside the element
// Map<element, fn>, one entry per element using the directive
const handlers = new Map()

// one listener for the whole page, added once on import, checks every element in the map on each click
document.addEventListener('click', (e) => {
    handlers.forEach((handler, domElement) => {
        if (!domElement.contains(e.target)) handler()
    })
})

// vue calls these on each element using it: mounted adds its entry, updated refreshes fn, unmounted removes it
// binding.value is fn, the function written in the template
export const clickOutside = {
    mounted(domElement, binding) {
        handlers.set(domElement, binding.value)
    },
    updated(domElement, binding) {
        handlers.set(domElement, binding.value)
    },
    unmounted(domElement) {
        handlers.delete(domElement)
    },
}
