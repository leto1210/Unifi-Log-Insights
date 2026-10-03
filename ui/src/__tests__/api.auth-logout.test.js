import { afterEach, expect, it, vi } from 'vitest'
import { authLogout } from '../api'

afterEach(() => vi.unstubAllGlobals())

it('treats an expired session as signed out', async () => {
  vi.stubGlobal('fetch', vi.fn(() => Promise.resolve({ status: 401, ok: false, json: () => Promise.resolve({ detail: 'expired' }) })))
  await expect(authLogout()).resolves.toEqual({ detail: 'expired' })
})

it('rejects a server error so the UI can offer a retry', async () => {
  vi.stubGlobal('fetch', vi.fn(() => Promise.resolve({ status: 500, ok: false, json: () => Promise.resolve({ detail: 'Server unavailable' }) })))
  await expect(authLogout()).rejects.toThrow('Server unavailable')
})
