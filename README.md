# BingR-Bot

Personal automation project for experimenting with browser automation, persistent Microsoft Edge profiles, Playwright, Docker, and a future Go keyword service.

The main bot is written in Python and uses Playwright to run local desktop and mobile search flows with a dedicated browser profile.

## Project status

- Python bot running with Playwright.
- Dedicated Edge profile stored in `.edge-playwright-profile/`.
- Desktop and mobile execution modes.
- Go keyword API planned under `api/`.
- Docker support in progress.

## Repository structure

```text
.
├── rewards_bot.py          # Main Python automation script
├── pyproject.toml          # Python project metadata and dependencies
├── uv.lock                 # Locked Python dependencies
├── api/                    # Go microservice work in progress
├── Driver_Notes/           # Microsoft Edge WebDriver notes and licenses
└── .vscode/                # Editor configuration
```

## Requirements

- Python version compatible with `pyproject.toml`
- `uv`
- Microsoft Edge
- Playwright

Install dependencies:

```bash
uv sync
```

Run the bot:

```bash
uv run rewards_bot.py
```

## Execution Modes

By default, the bot runs in **headless** mode (in the background without opening a browser window):

```bash
uv run rewards_bot.py
```

If you need to inspect the browser interactions or log in manually, run it with the flag:

```bash
HEADLESS=false uv run rewards_bot.py
```

## Automation & Background Execution

# Linux (systemd User Service)
1. Copy the example service file to your systemd user directory:
   ```bash
   cp rewards-bot.service.example ~/.config/systemd/user/rewards-bot.service
   ```

2. Edit WorkingDirectory in the file to point to your repository root.

3. Enable and start the daily timer (e.g., at 14:30):

  ```bash
  systemctl --user daemon-reload
  systemctl --user enable --now rewards-bot.timer
  ```

# Windows & MacOS

For Windows and macOS, run the bot directly via terminal as Execution Modes says, or configure your system's scheduler (Task Scheduler on Windows / launchd or cron on macOS):

## Browser profile

The bot uses a dedicated Edge user data directory by default:

```text
.edge-playwright-profile/
```

This keeps automation state separate from the real system Edge profile. The directory may contain cookies, session data, cache, and other local browser files, so it must not be committed.

You can override the profile path with:

```bash
EDGE_USER_DATA_DIR=/path/to/profile uv run rewards_bot.py
```

## Environment variables

```env
EDGE_USER_DATA_DIR=.edge-playwright-profile
EDGE_CHANNEL=msedge
PLAYWRIGHT_LAUNCH_TIMEOUT_MS=30000
PLAYWRIGHT_NAVIGATION_TIMEOUT_MS=30000
```

## Keyword API roadmap

The `api/` directory is intended to become a small Go microservice that collects keywords from public sources, starting with Wikimedia, and exposes them over HTTP for the Python bot.

Planned endpoint:

```http
GET /keywords?limit=31
```

Example response:

```json
{
  "keywords": [
    "python",
    "linux",
    "microsoft edge"
  ]
}
```

## Git hygiene

Do not commit generated files, credentials, browser profiles, local evidence, or logs.

Typical ignored paths:

```gitignore
.venv/
__pycache__/
.env
.edge-playwright-profile/
edge_profile/
edge_profile_root/
evidencias/
*.png
*.log
```
