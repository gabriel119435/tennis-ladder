export function useStaleGuard() {
    let latest = 0

    function start() {
        const current = ++latest
        return () => current === latest
    }

    // answers can arrive out of order, isLatest() from start() is true only while no newer call started
    // const isLatest = start(), then after await: if (!isLatest()) return
    return {start}
}
