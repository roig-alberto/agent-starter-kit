# Teardown of a scratch or verification app

1. Run `docker compose --profile prod down -v`.
2. Remove the port-registry row.
3. Remove the app's machine from the Tailscale admin console (the `tailscale_state` volume goes with `down -v`).
4. Run `rm -rf ~/projects/<app>`. The secrets live in the repo's `./secrets/`, so they go with it.
