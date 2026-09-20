import SettingsPihole from './SettingsPihole'
import SettingsAdguard from './SettingsAdguard'
import SettingsAbuseIPDB from './SettingsAbuseIPDB'

export default function SettingsIntegrations() {
  return (
    <div className="space-y-10">
      <SettingsPihole />
      <hr className="border-gray-800" />
      <SettingsAdguard />
      <hr className="border-gray-800" />
      <SettingsAbuseIPDB />
    </div>
  )
}
