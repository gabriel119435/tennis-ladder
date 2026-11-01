// typed score cell -> int only when every character is a digit, ex: '6' -> 6, '12' -> 12
export function toScore(text) {
    return /^\d+$/.test(text) ? Number(text) : text
}
