# Operations

`ops/startup.sh` is the one place that knows how to run buildly-core, per the Buildly
standard (`ops/standards/ai-engineering-standard.md`). It wraps the scripts that already
existed here rather than replacing them:

```
ops/startup.sh <start|stop|restart|status|logs|help> [--docker]
```

- **start** (native) — runs `scripts/run-standalone-dev.sh` in the background. Requires
  Postgres already reachable at `$DATABASE_HOST:$DATABASE_PORT` — this script doesn't start
  one for you.
- **start --docker** — runs the existing `docker-compose.yml` at the repo root, which
  includes its own `postgres_buildly` container. Nothing in `docker-compose.yml` changed.
- **stop / restart / status / logs** — same contract either way; `status` probes
  `/health_check/` (django-health-check, already wired in `core/urls.py`).

## What's unchanged

`scripts/*.sh`, `Dockerfile`, and `docker-compose.yml` are exactly as they were —
`ops/startup.sh` only wraps them so this repo is discoverable by
[Buildly Launchpad](../../launchpad) (which looks for `ops/startup.sh` + a health endpoint)
and consistent with every other Buildly repo's lifecycle contract.

## Not in this change

This repo's four existing CI workflows (`demo-build.yml`, `dev-build.yml`,
`prod-build.yml`, `unit_test.yml`) aren't touched here — folding an integration-test job
that exercises `ops/startup.sh` into one of them is a good follow-up, but a more careful
one than this change, since some of those are reportedly currently failing.
