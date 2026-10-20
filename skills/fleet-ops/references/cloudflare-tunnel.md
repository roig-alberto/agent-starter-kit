# Public path runbook (template)

Fill this in for however your apps reach the internet or your devices: a Cloudflare tunnel with Access, Tailscale
serve, or a reverse proxy. Keep the steps you actually run, with their exact commands.

## Add an app

1. `<create the route: for a Cloudflare tunnel, the dashboard's Public Hostname, subdomain to service:port>`
2. `<protect it: an Access policy, the tailnet, or the proxy's auth>`
3. Point it at the container port on the compose network, never a host port.
4. Check: `<a command that proves the hostname reaches THIS app, for example the connector's log naming the hostname>`.

## PWA install behind an auth gate

An auth gate in front of the manifest, the service worker and the icons blocks installing the app on Android. Example:
"each hostname gets a scoped bypass for `/manifest.webmanifest`, `/sw.js` and the icons, nothing else."

## When it breaks

- `<the symptom>`: `<the cause and the fix>`. Example: "another app's hostname 502s since a redeploy: the connector
  joined the wrong tunnel because a shell variable overrode the token."
- `<the symptom>`: `<the cause and the fix>`. Example: "every hostname down, containers fine: an ISP outage."
