import { beforeEach, describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import UniFiConnectionForm from '../components/UniFiConnectionForm'
import SettingsPihole from '../components/SettingsPihole'
import { fetchPiholeSettings, testUniFiConnection } from '../api'

vi.mock('../api', () => ({
  testUniFiConnection: vi.fn(() => Promise.resolve({ success: true, controller_name: 'UniFi' })),
  fetchPiholeSettings: vi.fn(() => Promise.resolve({ host: 'https://old.local', enabled: true, password_set: true, poll_interval: 60, enrichment: 'both' })),
  updatePiholeSettings: vi.fn(() => Promise.resolve({ success: true })),
  testPiholeConnection: vi.fn(() => Promise.resolve({ success: true })),
}))

beforeEach(() => vi.clearAllMocks())

describe('destination-bound credentials', () => {
  it('requires a new UniFi API key after a host change', async () => {
    render(<UniFiConnectionForm savedHost="https://old.local" savedApiKey onSuccess={vi.fn()} />)
    fireEvent.change(screen.getByPlaceholderText('https://192.168.1.1 or https://unifi.local'), { target: { value: 'https://new.local' } })
    expect(screen.getByText(/Enter new credentials before testing/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Test & Connect' })).toBeDisabled()
    fireEvent.change(screen.getByPlaceholderText('Enter your UniFi API key'), { target: { value: 'new-key' } })
    fireEvent.click(screen.getByRole('button', { name: 'Test & Connect' }))
    await waitFor(() => expect(testUniFiConnection).toHaveBeenCalledWith(expect.objectContaining({ host: 'https://new.local', api_key: 'new-key' })))
    expect(testUniFiConnection.mock.calls[0][0].use_saved_key).toBeUndefined()
  })

  it('blocks an environment UniFi key when the host no longer matches UNIFI_HOST', () => {
    const props = { envApiKey: true, envHost: 'https://old.local', savedHost: 'https://old.local', onSuccess: vi.fn() }
    const { rerender } = render(<UniFiConnectionForm {...props} />)
    rerender(<UniFiConnectionForm {...props} envHost="https://new.local" />)
    expect(screen.getByText(/API key is bound to UNIFI_HOST/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Test & Connect' })).toBeDisabled()
  })

  it('requires a new Pi-hole password after a host change', async () => {
    render(<SettingsPihole />)
    await waitFor(() => expect(fetchPiholeSettings).toHaveBeenCalled())
    fireEvent.change(screen.getByPlaceholderText('http://10.10.10.229:60080'), { target: { value: 'https://new.local' } })
    expect(screen.getByText(/saved password is tied to the previous host/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Test Connection' })).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Save' })).toBeDisabled()
    fireEvent.change(screen.getByPlaceholderText('Password for the new Pi-hole host'), { target: { value: 'new-secret' } })
    expect(screen.getByRole('button', { name: 'Test Connection' })).toBeEnabled()
  })
})
