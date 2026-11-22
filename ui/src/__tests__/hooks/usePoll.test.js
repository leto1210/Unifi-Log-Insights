import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook } from '@testing-library/react'
import usePoll from '../../hooks/usePoll'

let hidden = false

beforeEach(() => {
  vi.useFakeTimers()
  hidden = false
  Object.defineProperty(document, 'hidden', { configurable: true, get: () => hidden })
})

afterEach(() => {
  vi.useRealTimers()
})

describe('usePoll', () => {
  it('never overlaps: the next tick waits for the previous call to settle', async () => {
    let release
    const fn = vi.fn(() => new Promise(r => { release = r }))
    renderHook(() => usePoll(fn, 5000, true))

    await vi.advanceTimersByTimeAsync(5000)
    expect(fn).toHaveBeenCalledTimes(1)

    // Slow response: setInterval would have fired 4 more requests by now
    await vi.advanceTimersByTimeAsync(20000)
    expect(fn).toHaveBeenCalledTimes(1)

    release()
    await vi.advanceTimersByTimeAsync(5000)
    expect(fn).toHaveBeenCalledTimes(2)
  })

  it('keeps polling after a rejected call', async () => {
    const fn = vi.fn().mockRejectedValue(new Error('500'))
    renderHook(() => usePoll(fn, 1000, true))

    await vi.advanceTimersByTimeAsync(3000)
    expect(fn).toHaveBeenCalledTimes(3)
  })

  it('skips ticks while the tab is hidden and resumes when visible', async () => {
    const fn = vi.fn().mockResolvedValue()
    renderHook(() => usePoll(fn, 1000, true))

    hidden = true
    await vi.advanceTimersByTimeAsync(5000)
    expect(fn).not.toHaveBeenCalled()

    hidden = false
    await vi.advanceTimersByTimeAsync(1000)
    expect(fn).toHaveBeenCalledTimes(1)
  })

  it('does nothing when disabled and stops on unmount', async () => {
    const fn = vi.fn().mockResolvedValue()
    const { rerender, unmount } = renderHook(({ on }) => usePoll(fn, 1000, on), {
      initialProps: { on: false },
    })
    await vi.advanceTimersByTimeAsync(3000)
    expect(fn).not.toHaveBeenCalled()

    rerender({ on: true })
    await vi.advanceTimersByTimeAsync(1000)
    expect(fn).toHaveBeenCalledTimes(1)

    unmount()
    await vi.advanceTimersByTimeAsync(5000)
    expect(fn).toHaveBeenCalledTimes(1)
  })

  it('always calls the latest callback', async () => {
    const first = vi.fn().mockResolvedValue()
    const second = vi.fn().mockResolvedValue()
    const { rerender } = renderHook(({ fn }) => usePoll(fn, 1000, true), {
      initialProps: { fn: first },
    })
    rerender({ fn: second })

    await vi.advanceTimersByTimeAsync(1000)
    expect(first).not.toHaveBeenCalled()
    expect(second).toHaveBeenCalledTimes(1)
  })
})
