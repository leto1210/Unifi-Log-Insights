import { beforeEach, describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'

vi.mock('../api', () => ({
  fetchConfig: vi.fn(() => Promise.resolve({ setup_complete: false, wan_interfaces: [], interface_labels: {}, vpn_networks: {} })),
  fetchHealth: vi.fn(() => Promise.resolve({ status: 'ok' })),
  fetchLatestRelease: vi.fn(() => Promise.resolve(null)),
  fetchInterfaces: vi.fn(() => Promise.resolve({ interfaces: [] })),
  fetchUiSettings: vi.fn(() => Promise.resolve({})),
  updateUiSettings: vi.fn(() => Promise.resolve({})),
  fetchUniFiSettings: vi.fn(() => Promise.resolve({})),
  fetchAuthStatus: vi.fn(),
  fetchAuthMe: vi.fn(),
  authSetup: vi.fn(() => Promise.resolve({ success: true, username: 'admin' })),
  authLogin: vi.fn(() => Promise.resolve({ success: true, username: 'admin' })),
  authLogout: vi.fn(() => Promise.resolve({})),
  setAuthExpiredHandler: vi.fn(),
}))
vi.mock('../utils', () => ({ loadInterfaceLabels: vi.fn() }))
vi.mock('../vpnUtils', () => ({ isVpnInterface: vi.fn(() => false) }))
vi.mock('../components/LogStream', () => ({ default: () => <div>Log stream</div> }))
vi.mock('../components/SetupWizard', () => ({ default: () => <div>Setup wizard</div> }))
vi.mock('../components/SettingsOverlay', () => ({ default: () => <div>Settings</div> }))
vi.mock('../components/Dashboard', () => ({ default: () => <div />, DashboardSkeleton: () => <div /> }))
vi.mock('../components/ThreatMap', () => ({ default: () => <div />, ThreatMapSkeleton: () => <div /> }))
vi.mock('../components/FlowView', () => ({ default: () => <div /> }))

import App from '../App'
import { authLogout, authSetup, fetchAuthMe, fetchAuthStatus, fetchConfig } from '../api'

beforeEach(() => {
  vi.clearAllMocks()
  sessionStorage.clear()
  localStorage.clear()
  fetchAuthMe.mockResolvedValue({ authenticated: true, user_id: 1, username: 'admin' })
  fetchConfig.mockResolvedValue({ setup_complete: false, wan_interfaces: [], interface_labels: {}, vpn_networks: {} })
})

describe('authentication UI gates', () => {
  it('creates the first administrator before loading the setup wizard', async () => {
    fetchAuthStatus.mockResolvedValue({ auth_enabled_effective: true, has_users: false, has_admin: false, setup_complete: false, is_https: true, proxy_trusted: true })
    render(<App />)

    await screen.findByText('Create the first administrator')
    expect(fetchConfig).not.toHaveBeenCalled()
    fireEvent.change(screen.getByLabelText('Username'), { target: { value: 'admin' } })
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'secret123' } })
    fireEvent.change(screen.getByLabelText('Confirm password'), { target: { value: 'secret123' } })
    fireEvent.change(screen.getByLabelText('Setup token'), { target: { value: 'operator-token' } })
    fireEvent.click(screen.getByRole('button', { name: 'Create administrator' }))

    await waitFor(() => expect(authSetup).toHaveBeenCalledWith('admin', 'secret123', 'operator-token'))
    await screen.findByText('Setup wizard')
  })

  it('keeps enrollment open when the setup token is rejected', async () => {
    fetchAuthStatus.mockResolvedValue({ auth_enabled_effective: true, has_users: false, has_admin: false, setup_complete: false, is_https: true, proxy_trusted: true })
    authSetup.mockRejectedValueOnce(new Error('Invalid setup token'))
    render(<App />)

    await screen.findByText('Create the first administrator')
    fireEvent.change(screen.getByLabelText('Username'), { target: { value: 'admin' } })
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'secret123' } })
    fireEvent.change(screen.getByLabelText('Confirm password'), { target: { value: 'secret123' } })
    fireEvent.change(screen.getByLabelText('Setup token'), { target: { value: 'wrong-token' } })
    fireEvent.click(screen.getByRole('button', { name: 'Create administrator' }))

    await screen.findByText('Invalid setup token')
    expect(fetchConfig).not.toHaveBeenCalled()
    expect(screen.queryByText('Setup wizard')).not.toBeInTheDocument()
  })

  it('keeps the wizard available when authentication is disabled', async () => {
    fetchAuthStatus.mockResolvedValue({ auth_enabled_effective: false, has_admin: false, setup_complete: false })
    render(<App />)
    await screen.findByText('Setup wizard')
    expect(authSetup).not.toHaveBeenCalled()
  })

  it('shows the regular login when users exist without an active administrator', async () => {
    fetchAuthStatus.mockResolvedValue({ auth_enabled_effective: true, has_users: true, has_admin: false, setup_complete: true, is_https: true, proxy_trusted: true })
    fetchAuthMe.mockRejectedValue(new Error('No session'))
    render(<App />)
    await screen.findByText('Login to your account')
    expect(screen.queryByText('Create the first administrator')).not.toBeInTheDocument()
    expect(screen.queryByText('Administrator recovery required')).not.toBeInTheDocument()
    expect(fetchConfig).not.toHaveBeenCalled()
  })

  it('shows a retry after failed logout and clears session data only after success', async () => {
    fetchAuthStatus.mockResolvedValue({ auth_enabled_effective: true, has_users: true, has_admin: true, setup_complete: true, is_https: true, proxy_trusted: true })
    fetchConfig.mockResolvedValue({ setup_complete: true, wan_interfaces: [], interface_labels: {}, vpn_networks: {} })
    authLogout.mockRejectedValueOnce(new Error('Server unavailable')).mockResolvedValueOnce({})
    render(<App />)

    const button = await screen.findByTitle('Sign Out')
    sessionStorage.setItem('dashboard:v1:overview:24h', 'private data')
    sessionStorage.setItem('unifi-log-insight:time-range', '7d')
    fireEvent.click(button)
    await screen.findByText('Server unavailable')
    expect(sessionStorage.getItem('dashboard:v1:overview:24h')).toBe('private data')
    fireEvent.click(screen.getByTitle('Retry Sign Out'))
    await screen.findByText('Login to your account')
    expect(sessionStorage.getItem('dashboard:v1:overview:24h')).toBeNull()
    expect(sessionStorage.getItem('unifi-log-insight:time-range')).toBe('7d')
  })

  it('drops cached data before showing a different signed-in user', async () => {
    fetchAuthStatus.mockResolvedValue({ auth_enabled_effective: true, has_users: true, has_admin: true, setup_complete: true, is_https: true, proxy_trusted: true })
    fetchAuthMe.mockRejectedValueOnce(new Error('No session')).mockResolvedValueOnce({ authenticated: true, user_id: 2, username: 'new-admin' })
    fetchConfig.mockResolvedValue({ setup_complete: true, wan_interfaces: [], interface_labels: {}, vpn_networks: {} })
    sessionStorage.setItem('uli_identity', '1')
    sessionStorage.setItem('dashboard:v1:overview:24h', 'previous account data')
    render(<App />)
    await screen.findByText('Login to your account')
    fireEvent.change(screen.getByLabelText('Username'), { target: { value: 'new-admin' } })
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'secret123' } })
    fireEvent.click(screen.getByRole('button', { name: 'Sign in' }))
    await screen.findByText('Log stream')
    expect(sessionStorage.getItem('dashboard:v1:overview:24h')).toBeNull()
    expect(sessionStorage.getItem('uli_identity')).toBe('2')
  })
})
