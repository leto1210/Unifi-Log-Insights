import { act, render } from '@testing-library/react'
import { beforeEach, expect, it, vi } from 'vitest'
import Dashboard from '../components/Dashboard'
import { fetchStatsOverview } from '../api'
import { cacheKey } from '../lib/sessionCache'

vi.mock('../api', () => ({
  fetchStatsOverview: vi.fn(),
  fetchStatsCharts: vi.fn(() => new Promise(() => {})),
  fetchStatsTables: vi.fn(() => new Promise(() => {})),
}))

beforeEach(() => {
  vi.clearAllMocks()
  sessionStorage.clear()
})

it('does not cache a dashboard response received after unmount', async () => {
  let resolveOverview
  fetchStatsOverview.mockReturnValue(new Promise(resolve => { resolveOverview = resolve }))

  const { unmount } = render(<Dashboard />)
  expect(fetchStatsOverview).toHaveBeenCalled()
  unmount()

  await act(async () => { resolveOverview({ total: 42 }) })
  expect(sessionStorage.getItem(cacheKey('dashboard', 'overview:24h'))).toBeNull()
})
