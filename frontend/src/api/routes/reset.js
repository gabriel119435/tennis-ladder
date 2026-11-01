import {request} from '../request.js'

export async function resetAccount() {
    return request('/api/reset', {method: 'POST'})
}
