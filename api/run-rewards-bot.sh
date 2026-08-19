#!/bin/sh
set -eu

if [ -f /run/rewards_bot_env ]; then
    . /run/rewards_bot_env
fi

cd /app
exec python -u /app/rewards_bot.py
