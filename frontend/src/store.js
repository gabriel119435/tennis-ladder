import {reactive} from 'vue'

export const store = reactive({
    // {id: 1, username: 'admin name', is_default: false} or null if logged out
    user: null,
    // true once getMe() succeeds
    sessionLoaded: false,
})
