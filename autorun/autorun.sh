#!/usr/bin/env bash
#
# autorun.sh - Boot-time launcher for the Bing Rewards Bot.
#
# This script holds no bot logic: its only job is to prepare the environment
# and execute rewards_bot.py. The bot is already a daemon that runs the daily
# cycle (see `thistime` in rewards_bot.py).
#
# Usage:
#   ./autorun.sh              # run the bot in the foreground (service mode)
#   ./autorun.sh --status     # report whether an instance is already running
#   ./autorun.sh --stop       # stop the running instance
#   ./autorun.sh --install    # install and enable the boot-time service
#   ./autorun.sh --uninstall  # disable and remove the boot-time service
#
set -euo pipefail

# --- Paths --------------------------------------------------------------------
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
BOT_SCRIPT="${REPO_DIR}/rewards_bot.py"
ENV_FILE="${REPO_DIR}/.env"
LOG_DIR="${REPO_DIR}/logs"
LOCK_FILE="${REPO_DIR}/.autorun.lock"
PID_FILE="${LOG_DIR}/autorun.pid"
SERVICE_NAME="rewards-bot-autorun.service"
SERVICE_TEMPLATE="${SCRIPT_DIR}/rewards-bot-autorun.service"
USER_SERVICE_DIR="${HOME}/.config/systemd/user"

PYTHON_BIN="${PYTHON_BIN:-}"

log() {
    printf '[autorun] %s\n' "$*"
}

die() {
    printf '[autorun][ERROR] %s\n' "$*" >&2
    exit 1
}

# --- Optional .env loading -----------------------------------------------------
load_env() {
    [[ -f "${ENV_FILE}" ]] || return 0

    local line
    while IFS= read -r line || [[ -n "${line}" ]]; do
        line="${line#"${line%%[![:space:]]*}"}"           # trim left
        [[ -z "${line}" || "${line}" =~ ^[[:space:]]*# ]] && continue
        [[ "${line}" != *=* ]] && continue

        local key="${line%%=*}"
        local value="${line#*=}"
        key="${key%"${key##*[![:space:]]}"}"             # trim right
        value="${value#\"}"; value="${value%\"}"
        value="${value#\'}"; value="${value%\'}"

        [[ "${key}" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]] || continue
        export "${key}=${value}"
    done < "${ENV_FILE}"

    log "loaded variables from ${ENV_FILE}."
}

# --- Interpreter selection -----------------------------------------------------
select_runner() {
    if [[ -n "${PYTHON_BIN}" ]]; then
        echo "${PYTHON_BIN}"
        return 0
    fi

    if command -v uv >/dev/null 2>&1; then
        echo "uv run --project ${REPO_DIR}"
        return 0
    fi

    if [[ -x "${REPO_DIR}/.venv/bin/python" ]]; then
        echo "${REPO_DIR}/.venv/bin/python"
        return 0
    fi

    die "neither uv nor .venv found; install dependencies with 'uv sync' or set PYTHON_BIN."
}

# --- Single instance guard ------------------------------------------------------
acquire_lock() {
    exec 9>"${LOCK_FILE}"
    if ! flock -n 9; then
        die "an instance of the bot is already running (lock: ${LOCK_FILE})."
    fi
    echo $$ >&9 || true
}

run_bot() {
    [[ -f "${BOT_SCRIPT}" ]] || die "bot not found at ${BOT_SCRIPT}."

    mkdir -p "${LOG_DIR}"
    load_env
    acquire_lock
    echo $$ > "${PID_FILE}"

    local runner
    runner="$(select_runner)"

    log "repository: ${REPO_DIR}"
    log "launching: ${runner} ${BOT_SCRIPT}"

    cd "${REPO_DIR}"

    # shellcheck disable=SC2086
    PYTHONUNBUFFERED=1 exec ${runner} "${BOT_SCRIPT}" "$@"
}

# --- Boot service installation --------------------------------------------------
install_autostart_entry() {
    # Fallback for machines without a user systemd: XDG autostart entry.
    local autostart_dir="${HOME}/.config/autostart"
    mkdir -p "${autostart_dir}"

    cat > "${autostart_dir}/${SERVICE_NAME%.service}.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Bing Rewards Bot
Comment=Run the Bing Rewards bot on login
Exec=${SCRIPT_DIR}/autorun.sh
Path=${REPO_DIR}
Terminal=false
X-GNOME-Autostart-enabled=true
EOF

    log "installed XDG autostart fallback: ${autostart_dir}/${SERVICE_NAME%.service}.desktop"
}

install_service() {
    [[ -f "${SERVICE_TEMPLATE}" ]] || die "missing template ${SERVICE_TEMPLATE}."

    if ! command -v systemctl >/dev/null 2>&1 || ! systemctl --user daemon-reload >/dev/null 2>&1; then
        log "user systemd unavailable, falling back to XDG autostart."
        install_autostart_entry
        return 0
    fi

    mkdir -p "${USER_SERVICE_DIR}"
    sed "s|@@REPO_DIR@@|${REPO_DIR}|g" "${SERVICE_TEMPLATE}" \
        > "${USER_SERVICE_DIR}/${SERVICE_NAME}"

    # The bot runs headless, but HEADLESS=false needs a display.
    if [[ -n "${WAYLAND_DISPLAY:-}" ]]; then
        sed -i "s|^Environment=DISPLAY=.*|Environment=WAYLAND_DISPLAY=${WAYLAND_DISPLAY}|" \
            "${USER_SERVICE_DIR}/${SERVICE_NAME}"
    elif [[ -n "${DISPLAY:-}" ]]; then
        sed -i "s|^Environment=DISPLAY=.*|Environment=DISPLAY=${DISPLAY}|" \
            "${USER_SERVICE_DIR}/${SERVICE_NAME}"
    fi

    systemctl --user daemon-reload
    systemctl --user enable "${SERVICE_NAME}"

    log "service installed: ${USER_SERVICE_DIR}/${SERVICE_NAME}"
    log "start it now with: systemctl --user start ${SERVICE_NAME}"
    log "follow the log with: journalctl --user -u ${SERVICE_NAME} -f"
}

uninstall_service() {
    if command -v systemctl >/dev/null 2>&1; then
        systemctl --user disable --now "${SERVICE_NAME}" 2>/dev/null || true
        systemctl --user daemon-reload 2>/dev/null || true
    fi
    rm -f "${USER_SERVICE_DIR}/${SERVICE_NAME}"
    rm -f "${HOME}/.config/autostart/${SERVICE_NAME%.service}.desktop"
    log "service removed."
}

show_status() {
    if pgrep -f "python.*rewards_bot.py" >/dev/null 2>&1; then
        log "the bot is running (pgrep match)."
    else
        log "the bot is not running."
    fi

    if systemctl --user is-enabled --quiet "${SERVICE_NAME}" 2>/dev/null; then
        log "boot service: enabled"
    else
        log "boot service: not enabled"
    fi
}

stop_bot() {
    if command -v systemctl >/dev/null 2>&1 && systemctl --user is-active --quiet "${SERVICE_NAME}" 2>/dev/null; then
        log "stopping service ${SERVICE_NAME}..."
        systemctl --user stop "${SERVICE_NAME}"
    else
        log "service is not active; killing leftover processes."
    fi

    pkill -f "python.*rewards_bot.py" 2>/dev/null || log "no bot processes were running."
    rm -f "${PID_FILE}"
    log "bot stopped."
}

case "${1:-}" in
    --install)   install_service ;;
    --uninstall) uninstall_service ;;
    --status)    show_status ;;
    --stop)      stop_bot ;;
    "")          run_bot ;;
    *)           die "unknown option: $1 (use --status|--stop|--install|--uninstall)" ;;
esac
