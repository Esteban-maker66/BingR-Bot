#!/bin/sh
set -eu

: "${CRON_SCHEDULE:=15 14 * * *}"
: "${RUN_ON_START:=true}"
: "${TZ:=America/Santo_Domingo}"

if [ -f "/usr/share/zoneinfo/$TZ" ]; then
    ln -snf "/usr/share/zoneinfo/$TZ" /etc/localtime
    echo "$TZ" > /etc/timezone
fi

python - <<'PY'
import os
import shlex

keys = ("BING_USER", "BING_PASS", "EDGE_DRIVER_PATH", "EVIDENCIAS_DIR", "TZ")
with open("/run/rewards_bot_env", "w", encoding="utf-8") as env_file:
    for key in keys:
        value = os.environ.get(key)
        if value is not None:
            env_file.write(f"export {key}={shlex.quote(value)}\n")
PY
chmod 600 /run/rewards_bot_env

cat > /etc/cron.d/rewards-bot <<EOF
SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
$CRON_SCHEDULE root /usr/local/bin/run-rewards-bot >> /proc/1/fd/1 2>> /proc/1/fd/2
EOF
chmod 0644 /etc/cron.d/rewards-bot

if [ "$RUN_ON_START" = "true" ]; then
    /usr/local/bin/run-rewards-bot &
fi

exec cron -f
