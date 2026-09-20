/**
 * Component tests for the AbuseIPDB kill-switch panel.
 * Covers: renders current state, toggling off calls the API, and the toggle
 * is disabled (cannot enable) when no API key is configured.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'

const mockFetch = vi.fn()
const mockUpdate = vi.fn()

vi.mock('../api', () => ({
  fetchAbuseIPDBSettings: (...a) => mockFetch(...a),
  updateAbuseIPDBSettings: (...a) => mockUpdate(...a),
}))

import SettingsAbuseIPDB from '../components/SettingsAbuseIPDB'

beforeEach(() => {
  vi.clearAllMocks()
})

describe('SettingsAbuseIPDB', () => {
  it('renders enabled/active state after load', async () => {
    mockFetch.mockResolvedValue({ enabled: true, configured: true, active: true })
    render(<SettingsAbuseIPDB />)
    expect(await screen.findByRole('button', { name: /enabled/i })).toBeInTheDocument()
    expect(screen.getByText(/Active/)).toBeInTheDocument()
  })

  it('toggling off calls updateAbuseIPDBSettings({enabled:false})', async () => {
    mockFetch.mockResolvedValue({ enabled: true, configured: true, active: true })
    mockUpdate.mockResolvedValue({ enabled: false, configured: true, active: false })
    render(<SettingsAbuseIPDB />)
    const btn = await screen.findByRole('button', { name: /enabled/i })
    fireEvent.click(btn)
    await waitFor(() => expect(mockUpdate).toHaveBeenCalledWith({ enabled: false }))
    expect(await screen.findByRole('button', { name: /disabled/i })).toBeInTheDocument()
  })

  it('cannot enable when not configured (no API key)', async () => {
    mockFetch.mockResolvedValue({ enabled: false, configured: false, active: false })
    render(<SettingsAbuseIPDB />)
    const btn = await screen.findByRole('button', { name: /disabled/i })
    expect(btn).toBeDisabled()
    fireEvent.click(btn)
    expect(mockUpdate).not.toHaveBeenCalled()
    expect(screen.getByText(/ABUSEIPDB_API_KEY/)).toBeInTheDocument()
  })
})
