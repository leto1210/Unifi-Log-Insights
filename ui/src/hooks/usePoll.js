import { useEffect, useRef } from 'react'

// Run `fn` every `delayMs` while `enabled`. The next tick is scheduled only
// after the previous call settles, so a slow API never stacks overlapping
// requests (setInterval would). Ticks are skipped while the tab is hidden.
// The latest `fn` is always used, so callers need not memoize it.
export default function usePoll(fn, delayMs, enabled = true) {
  const fnRef = useRef(fn)
  fnRef.current = fn

  useEffect(() => {
    if (!enabled) return
    let cancelled = false
    let timer
    const tick = async () => {
      if (!document.hidden) {
        try { await fnRef.current() } catch { /* caller handles its own errors */ }
      }
      if (!cancelled) timer = setTimeout(tick, delayMs)
    }
    timer = setTimeout(tick, delayMs)
    return () => { cancelled = true; clearTimeout(timer) }
  }, [enabled, delayMs])
}
