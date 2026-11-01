import {createI18n} from 'vue-i18n'
import ptBr from './locales/pt-br.js'

export const i18n = createI18n({
    // false: components get t from useI18n()
    legacy: false,
    locale: 'pt-br',
    messages: {'pt-br': ptBr},
    // a missing key shows its last segment, ex: 'foo.bar' -> 'bar not found'
    missing: (locale, key) => `${key.split('.').at(-1)} not found`,
})
