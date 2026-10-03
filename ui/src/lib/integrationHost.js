// Mirrors receiver/service/integration_urls.same_integration_destination:
// scheme, host (case-insensitive), effective port and base path decide
// whether two integration URLs point at the same destination.

function identity(raw, defaultScheme, stripAdminPath) {
  const value = (raw || '').trim()
  if (!value) return ''
  try {
    const url = new URL(/^https?:\/\//i.test(value) ? value : `${defaultScheme}://${value}`)
    let path = url.pathname.replace(/\/+$/, '')
    if (stripAdminPath) path = path.replace(/\/admin$/i, '')
    // URL#origin already drops default ports and lowercases scheme + host.
    return url.origin + path
  } catch {
    return value.replace(/\/+$/, '').toLowerCase()
  }
}

export function sameIntegrationHost(a, b, { defaultScheme = 'https', stripAdminPath = false } = {}) {
  return identity(a, defaultScheme, stripAdminPath) === identity(b, defaultScheme, stripAdminPath)
}
