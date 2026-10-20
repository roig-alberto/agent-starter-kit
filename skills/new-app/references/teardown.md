# Teardown of a scratch or verification app

1. Run `docker compose --profile prod down -v`.
2. Remove the port-registry row and the tunnel row.
3. Delete the Cloudflare Access policy and the DNS hostname.
4. Run `rm -rf ~/projects/<app>`. The secrets live in the repo's `./secrets/`, so they go with it.
