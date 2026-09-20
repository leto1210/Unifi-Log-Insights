import { useState, useEffect, useCallback } from 'react'
import { fetchAbuseIPDBSettings, updateAbuseIPDBSettings } from '../api'

// AbuseIPDB shield icon (inline SVG — no binary asset needed)
function AbuseIPDBIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M12 1L3 5v6c0 5.25 3.75 10.15 9 11.25C17.25 21.15 21 16.25 21 11V5L12 1zm-1 15l-4-4 1.41-1.41L11 13.17l5.59-5.59L18 9l-7 7z" />
    </svg>
  )
}

export default function SettingsAbuseIPDB() {
  const [settings, setSettings] = useState(null)
  const [toggling, setToggling] = useState(false)
  const [error, setError] = useState(null)
  const [loadError, setLoadError] = useState(null)

  const loadSettings = useCallback(async () => {
    try {
      const data = await fetchAbuseIPDBSettings()
      setSettings(data)
      setLoadError(null)
    } catch (e) {
      console.error('Failed to load AbuseIPDB settings:', e)
      setLoadError(e.message || 'Failed to load settings')
    }
  }, [])

  useEffect(() => { loadSettings() }, [loadSettings])

  async function handleToggle() {
    if (toggling || !settings) return
    // Cannot enable without an API key (env-only).
    if (!settings.enabled && !settings.configured) return
    setToggling(true)
    setError(null)
    const next = !settings.enabled
    try {
      const result = await updateAbuseIPDBSettings({ enabled: next })
      setSettings(result)
    } catch (e) {
      setError(e.message || 'Failed to update')
    } finally {
      setToggling(false)
    }
  }

  if (loadError) {
    return (
      <div className="text-sm text-red-400">
        Failed to load AbuseIPDB settings: {loadError}
        <button onClick={loadSettings} className="ml-2 text-teal-400 hover:text-teal-300">Retry</button>
      </div>
    )
  }
  if (!settings) {
    return <div className="text-sm text-gray-400">Loading AbuseIPDB settings...</div>
  }

  const active = settings.active
  const canToggle = settings.enabled || settings.configured

  return (
    <div className="space-y-8">
      <section>
        <h2 className="flex items-center gap-2 text-base font-semibold text-gray-300 mb-3 uppercase tracking-wider">
          <AbuseIPDBIcon className="w-5 h-5 text-teal-400" />
          AbuseIPDB
        </h2>

        {/* Status card */}
        <div className="rounded-lg border border-gray-700 bg-gray-950 px-4 py-3 mb-3">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-200">Threat intelligence enrichment</span>
            <span className={`flex items-center gap-1.5 text-sm leading-none ${
              active ? 'text-emerald-400' : 'text-gray-500'
            }`}>
              <span className={`w-1.5 h-1.5 rounded-full block ${
                active ? 'bg-emerald-400' : 'bg-gray-500'
              }`} />
              {active ? 'Active' : 'Inactive'}
            </span>
          </div>
          <div className="text-sm text-gray-500 mt-1">
            API key: {settings.configured ? 'configured' : 'not configured'}
          </div>
        </div>

        {/* Configuration */}
        <div className="rounded-lg border border-gray-700 bg-gray-950">
          <div className="p-5 space-y-5">
            {/* Enable/Disable toggle */}
            <div className="flex items-center justify-between">
              <div>
                <p className="text-base text-gray-200 font-medium">Enable AbuseIPDB</p>
                <p className="text-sm text-gray-500">
                  Look up threat scores for blocked firewall IPs. Disabling pauses all
                  outbound AbuseIPDB calls without removing the key.
                </p>
              </div>
              <button
                onClick={handleToggle}
                disabled={toggling || !canToggle}
                className={`px-3 py-1 rounded text-sm font-semibold border transition-colors ${
                  settings.enabled
                    ? 'bg-green-500/10 text-green-300 border-green-500/40'
                    : !canToggle
                      ? 'bg-black text-gray-600 border-gray-800 cursor-not-allowed'
                      : 'bg-black text-gray-400 border-gray-700'
                }`}
              >
                {settings.enabled ? 'Enabled' : 'Disabled'}
              </button>
            </div>

            {/* Not-configured hint */}
            {!settings.configured && (
              <div className="flex items-start gap-2 bg-yellow-500/10 border border-yellow-500/30 rounded px-3 py-2">
                <svg className="w-4 h-4 text-yellow-400 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 6a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 6zm0 9a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                </svg>
                <span className="text-sm text-yellow-200">
                  Set the <code className="text-yellow-100">ABUSEIPDB_API_KEY</code> environment
                  variable and restart to enable threat enrichment.
                </span>
              </div>
            )}

            {settings.enabled && !active && settings.configured && (
              <p className="text-sm text-gray-500">
                Enabled but currently inactive — check the container logs.
              </p>
            )}

            {error && <span className="text-sm text-red-400">{error}</span>}
          </div>
        </div>
      </section>
    </div>
  )
}
