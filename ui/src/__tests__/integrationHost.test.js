import { describe, expect, it } from 'vitest'
import { sameIntegrationHost } from '../lib/integrationHost'

describe('sameIntegrationHost', () => {
  it('ignores case, trailing slash and default ports', () => {
    expect(sameIntegrationHost('https://CONTROLLER.lan:443/', 'https://controller.lan')).toBe(true)
    expect(sameIntegrationHost('http://pi.hole:80', 'http://pi.hole')).toBe(true)
  })

  it('adds the default scheme to bare hosts', () => {
    expect(sameIntegrationHost('controller.lan', 'https://controller.lan')).toBe(true)
    expect(sameIntegrationHost('pi.hole', 'http://pi.hole', { defaultScheme: 'http' })).toBe(true)
  })

  it('treats /admin as part of the Pi-hole URL only when asked', () => {
    expect(sameIntegrationHost('http://pi.hole/admin', 'http://pi.hole', { stripAdminPath: true })).toBe(true)
    expect(sameIntegrationHost('http://pi.hole/admin', 'http://pi.hole')).toBe(false)
  })

  it('detects real destination changes', () => {
    expect(sameIntegrationHost('https://a.lan', 'http://a.lan')).toBe(false)
    expect(sameIntegrationHost('https://a.lan:8443', 'https://a.lan')).toBe(false)
    expect(sameIntegrationHost('https://a.lan/proxy', 'https://a.lan')).toBe(false)
    expect(sameIntegrationHost('https://a.lan', 'https://b.lan')).toBe(false)
  })
})
