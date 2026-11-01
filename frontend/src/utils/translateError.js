import {i18n} from '../i18n.js'
import {LIMIT_PARAMS} from '../constants.js'

// error code to its locale text, LIMIT_PARAMS fills slots like {word_max}
// unknown codes show "{code} not found"
export function translateError(code) {
    return i18n.global.t(`backend_errors.${code}`, LIMIT_PARAMS)
}
