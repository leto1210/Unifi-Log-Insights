/**
 * sessionStorage cache with TTL — shared across Dashboard, FlowView, etc.
 *
 * Keys are namespaced by prefix + version + a caller-supplied discriminator
 * (e.g. serialized filters). Data expires after CACHE_TTL_MS.
 */

const CACHE_VERSION = 'v1'
const CACHE_TTL_MS = 10 * 60 * 1000 // 10 minutes
const PRIVATE_PREFIXES = ['dashboard:', 'ip-pairs:', 'sankey:', 'zone-matrix:']

export { CACHE_TTL_MS }

export function cacheKey(prefix, discriminator) {
  return `${prefix}:${CACHE_VERSION}:${discriminator}`
}

export function readCache(prefix, discriminator) {
  try {
    const raw = sessionStorage.getItem(cacheKey(prefix, discriminator))
    if (!raw) return null
    const { fetchedAt, data } = JSON.parse(raw)
    if (Date.now() - fetchedAt > CACHE_TTL_MS) return null
    return data
  } catch (e) { console.warn('Cache read failed:', e); return null }
}

export function writeCache(prefix, discriminator, data) {
  try {
    sessionStorage.setItem(cacheKey(prefix, discriminator), JSON.stringify({ fetchedAt: Date.now(), data }))
  } catch (e) { console.warn('Cache write failed:', e) }
}

export function clearSessionCache() {
  try {
    for (const key of Object.keys(sessionStorage)) {
      if (PRIVATE_PREFIXES.some(prefix => key.startsWith(prefix))) sessionStorage.removeItem(key)
    }
    sessionStorage.removeItem('flowview_filters')
  } catch (e) { console.warn('Cache clear failed:', e) }
}
