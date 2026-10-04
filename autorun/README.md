# autorun/ — boot-time automation

This folder contains **only the boot automation**. No bot logic lives here: the
bash script just prepares the environment and launches `rewards_bot.py`.

## Files

| File | Purpose |
| --- | --- |
| `autorun.sh` | Launcher. Runs the bot, installs/removes the boot hook, reports status. |
| `rewards-bot-autorun.service` | systemd user service template (`@@REPO_DIR@@` is replaced on install). |
| `install.sh` | Shortcut: installs and enables the boot-time startup. |
| `uninstall.sh` | Shortcut: removes the boot-time startup. |

## What happens on boot

1. systemd starts `rewards-bot-autorun.service` (`default.target` unit).
2. The service invokes `autorun/autorun.sh`.
3. The script loads the repository `.env`, takes a lock to prevent duplicate
   instances, and runs the bot with `uv run` (or the interpreter set in
   `PYTHON_BIN`).
4. `rewards_bot.py` is already a daemon: if today's cycle has not run yet it
   executes immediately; otherwise it waits for `thistime` in
   `rewards_bot.py`.

## Install

```bash
cd /path/to/repo/autorun
./install.sh                 # install + enable (does not start it yet)
systemctl --user start rewards-bot-autorun.service
```

Verify:

```bash
systemctl --user status rewards-bot-autorun.service
journalctl --user -u rewards-bot-autorun.service -f
./autorun.sh --status
```

## Commands

```bash
./autorun.sh              # run the bot in the foreground (what the service uses)
./autorun.sh --status     # process + service status
./autorun.sh --stop       # stop the running instance
./autorun.sh --install    # install the boot-time startup
./autorun.sh --uninstall  # remove it
```

## Uninstall

```bash
./uninstall.sh
```

## Notes

- Without a user systemd, `--install` falls back to an **XDG autostart** entry
  (`~/.config/autostart/`), which runs when you log in.
- To start without a logged-in session: `sudo loginctl enable-linger "$USER"`.
  Already enabled on this machine (`Linger=yes`).
- `HEADLESS=false` requires a display; the installer copies `DISPLAY` or
  `WAYLAND_DISPLAY` from the current environment into the service.
- Bot logs go to `journalctl`. The repository `logs/` folder only holds
  `autorun.pid`.
