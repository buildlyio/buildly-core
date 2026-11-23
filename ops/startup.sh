#!/usr/bin/env bash
# ops/startup.sh — unified lifecycle script for buildly-core (the Buildly standard: see
# ops/standards/ai-engineering-standard.md). Native by default; --docker uses the existing
# docker-compose.yml at the repo root (unchanged — this script only wraps it).
#
# Native mode needs Postgres reachable at $DATABASE_HOST:$DATABASE_PORT already (the
# existing scripts/run-standalone-dev.sh doesn't start one for you); --docker mode starts
# its own postgres_buildly container via docker-compose.yml.
#
# Usage: ops/startup.sh <start|stop|restart|status|logs|help> [--docker]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8080}"
PID_FILE="$REPO_ROOT/.run/service.pid"
LOG_FILE="$REPO_ROOT/.run/service.log"
HEALTH_URL="${HEALTH_URL:-http://127.0.0.1:$PORT/health_check/}"

log_info()  { echo "[INFO]  $*"; }
log_ok()    { echo "[OK]    $*"; }
log_warn()  { echo "[WARN]  $*"; }
log_error() { echo "[ERROR] $*" >&2; }

running() { [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; }

start_native() {
  if running; then
    log_ok "Already running (PID $(cat "$PID_FILE"))."
    return
  fi
  mkdir -p "$REPO_ROOT/.run"
  log_info "Starting buildly-core (native) — requires Postgres at \$DATABASE_HOST:\$DATABASE_PORT..."
  cd "$REPO_ROOT"
  nohup bash scripts/run-standalone-dev.sh > "$LOG_FILE" 2>&1 &
  echo $! > "$PID_FILE"
  sleep 2
  if running; then
    log_ok "Started (PID $(cat "$PID_FILE")) — http://$HOST:$PORT"
  else
    log_error "Failed to start — see $LOG_FILE"
    rm -f "$PID_FILE"
    exit 1
  fi
}

stop_native() {
  if running; then
    kill "$(cat "$PID_FILE")" 2>/dev/null || true
    for _ in $(seq 1 15); do running || break; sleep 1; done
    kill -9 "$(cat "$PID_FILE")" 2>/dev/null || true
    rm -f "$PID_FILE"
    log_ok "Stopped."
  else
    log_info "Not running."
  fi
}

compose() {
  if docker compose version &>/dev/null; then
    docker compose -f "$REPO_ROOT/docker-compose.yml" "$@"
  else
    docker-compose -f "$REPO_ROOT/docker-compose.yml" "$@"
  fi
}

start_docker() { log_info "Starting via docker-compose.yml..."; compose up --build -d; log_ok "Started."; }
stop_docker()  { compose down 2>/dev/null || true; log_ok "Stopped."; }

DOCKER=0
ARGS=()
for a in "$@"; do
  [[ "$a" == "--docker" ]] && DOCKER=1 || ARGS+=("$a")
done
CMD="${ARGS[0]:-help}"

case "$CMD" in
  start)   [[ "$DOCKER" == 1 ]] && start_docker || start_native ;;
  stop)    [[ "$DOCKER" == 1 ]] && stop_docker || stop_native ;;
  restart)
    if [[ "$DOCKER" == 1 ]]; then
      "$0" stop --docker || true
      "$0" start --docker
    else
      "$0" stop || true
      "$0" start
    fi ;;
  status)
    if running; then
      log_ok "Running (PID $(cat "$PID_FILE")) — http://$HOST:$PORT"
    else
      log_info "Not running (or started via --docker; check: docker compose -f docker-compose.yml ps)."
    fi
    curl -fsS "$HEALTH_URL" >/dev/null 2>&1 && log_ok "Health check passed." \
      || log_warn "Health check did not respond at $HEALTH_URL" ;;
  logs)    tail -n 50 -f "$LOG_FILE" ;;
  help|*)
    cat <<USAGE
Usage: ops/startup.sh <start|stop|restart|status|logs|help> [--docker]

  start     Start buildly-core (native: scripts/run-standalone-dev.sh)
  stop      Stop it
  restart   Stop then start
  status    Is it running? Also probes \$HEALTH_URL (/health_check/)
  logs      Follow the native-mode service log
  --docker  Use the existing docker-compose.yml (includes its own Postgres)
USAGE
    ;;
esac
