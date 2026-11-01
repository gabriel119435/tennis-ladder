import {createApp} from 'vue'
import './style.css'
import App from './App.vue'
import router from './router/index.js'
import {i18n} from './i18n.js'
import {clickOutside} from './directives/clickOutside.js'
import {setSessionLostHandler} from './api/request.js'
import {store} from './store.js'

// session gone: forget the user so the guard allows /login, then go there
setSessionLostHandler(async () => {
    store.user = null
    await router.push('/login')
})

createApp(App)
    .use(router)
    .use(i18n)
    // used as v-click-outside in templates, vue adds the v- prefix
    .directive('click-outside', clickOutside)
    .mount('#app')
