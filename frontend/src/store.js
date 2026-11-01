import {reactive} from 'vue'

export const store = reactive({
    // {id: 1, username: 'admin name'} or null if logged out
    user: null,
    // true once getMe() succeeds
    sessionLoaded: false,
})
