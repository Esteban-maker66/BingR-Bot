import os
import time
import random
import schedule
from datetime import datetime
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILE_PATH = os.path.abspath(
    os.path.expanduser(
        os.getenv("EDGE_USER_DATA_DIR", os.path.join(BASE_DIR, ".edge-playwright-profile"))
    )
)

KEYWORDS_FILE = os.path.join(BASE_DIR, "words.txt")

EDGE_CHANNEL = os.getenv("EDGE_CHANNEL", "msedge")
LAUNCH_TIMEOUT_MS = int(os.getenv("PLAYWRIGHT_LAUNCH_TIMEOUT_MS", "30000"))
NAVIGATION_TIMEOUT_MS = int(os.getenv("PLAYWRIGHT_NAVIGATION_TIMEOUT_MS", "30000"))

SAMSUNG_A16_5G_CONF = {
    "user_agent": "Mozilla/5.0 (Linux; Android 16; SM-A166M/DS) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.122 Mobile Safari/537.36",
    "viewport": {"width": 360, "height": 780},
    "device_scale_factor": 3.0,
    "is_mobile": True,
    "has_touch": True,
}

DESKTOP_CONF = {
    "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36",
    "viewport": {"width": 1280, "height": 720},
    "device_scale_factor": 1.0,
    "is_mobile": False,
    "has_touch": False,
}

ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-popup-blocking",
]

HEADLESS_MODE = os.getenv("HEADLESS", "true").lower() in ("true", "1", "yes")

ROJO = "\033[31m"
VERDE = "\033[32m"
AMARILLO = "\033[33m"
AZUL = "\033[34m"
RESET = "\033[0m"

LAST_RUN_FILE = os.path.join(BASE_DIR, "last_run.txt")

def hasRunToday():
  if not os.path.exists(LAST_RUN_FILE):
    return False

  try:
    with open(LAST_RUN_FILE, "r") as f:
      last_date = f.read().strip()
      return last_date == datetime.now().strftime("%Y-%m-%d")
  except Exception:
    return False

def recordRunToday():
  try:
    with open(LAST_RUN_FILE, "w") as f:
      f.write(datetime.now().strftime("%Y-%m-%d"))
  except Exception as e:
    print(f"{AMARILLO}[!]: cannot save last_run.txt: {e}{RESET}")


# Hide browser automation indicators from web pages
def hideFootPrintBot(context):
    """Inject JavaScript for hiding the automation flags natively."""
    context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)


# Launch a persistent Edge browser context with the selected device settings
def launchEdgeContext(pw, device_conf):
    os.makedirs(PROFILE_PATH, exist_ok=True)
    print(f"{AZUL}[i] Edge user data dir: {PROFILE_PATH}{RESET}", flush=True)

    context = pw.chromium.launch_persistent_context(
        user_data_dir=PROFILE_PATH,
        channel=EDGE_CHANNEL,
        headless=HEADLESS_MODE,
        args=ARGS,
        ignore_default_args=["--enable-automation"],
        timeout=LAUNCH_TIMEOUT_MS,
        **device_conf
    )

    context.set_default_navigation_timeout(NAVIGATION_TIMEOUT_MS)
    context.set_default_timeout(NAVIGATION_TIMEOUT_MS)
    hideFootPrintBot(context)
    return context


# Remove stale Edge profile lock files before starting the browser
def cleanupProfileLock():
  """Removes stale Singleton locks before launching Edge to avoid ProcessSingleton errors."""
  lock_files = [
      os.path.join(PROFILE_PATH, "SingletonLock"),
      os.path.join(PROFILE_PATH, "SingletonCookie"),
      os.path.join(PROFILE_PATH, "SingletonSocket"),
  ]

  for lock_file in lock_files:
    if os.path.exists(lock_file):
      try:
        os.remove(lock_file)
      except OSError:
        pass
      

    # Enter a search term and submit it to Bing
def typeSearch(page, keyword):
    """Types keyword into search input & submit query."""
    search_select = "textarea[name='q'], input[name='q'], #sb_form_q"

    try:
        page.wait_for_selector(search_select, timeout=4000)
        search_input = page.locator(search_select).first

        search_input.fill("")

        search_input.type(keyword, delay=random.randint(80, 100))
        time.sleep(random.uniform(0.5, 0.7))

        search_input.press("Enter")
        page.wait_for_load_state("domcontentloaded")

    except Exception:
        search_URL = f"https://www.bing.com/search?q={quote_plus(keyword)}"
        page.goto(search_URL, wait_until="domcontentloaded")


# Return the first active page in the browser context
def activePage(context):
    if context.pages:
        page = context.pages[0]

    else:
        page = context.new_page()
    page.bring_to_front()

    return page


# Load non-empty search keywords while ignoring comment lines
def loadKeywords(file_path=KEYWORDS_FILE):
  """Loads search keywords from a text file, ignoring empty lines and comments."""
  if not os.path.exists(file_path):
    print(f"{ROJO}[ER]: Keywords file not found at: {file_path}{RESET}")
    return []

  with open(file_path, "r", encoding="utf-8") as f:

    keywords = [
        line.strip()
        for line in f
        if line.strip() and not line.strip().startswith("#")
    ]

  if not keywords:
    print(
        f"{ROJO}[ER]: Keywords file is empty or formatted incorrectly.{RESET}"
    )

  return keywords

KEYWORDS = loadKeywords()


# Open the Rewards dashboard & claim available points
def claimPoints(page, context):
  """Navigates to Rewards dashboard and targets the 'Ready to claim' component directly"""
  print(f"{VERDE}\n[+] Claiming accumulated points...{RESET}")

  try:
    print(f"{AZUL}[...]: Opening points panel.{RESET}")
    click_area = page.locator("div.b_clickarea").first

    if click_area.count() > 0:
      click_area.click(force=True)
      page.wait_for_timeout(1500)

    claim_container = page.locator("a.user-pointclaim-container").first
    target_url = None

    if claim_container.count() > 0:
      target_url = claim_container.get_attribute("href")

    if not target_url or "javascript" in target_url:
      target_url = "https://rewards.bing.com/"

    print(f"{AZUL}[i]: Navigating to Rewards URL: {target_url}{RESET}")

    dashboard_page = context.new_page()
    dashboard_page.goto(target_url, wait_until="domcontentloaded")
    dashboard_page.wait_for_timeout(3000)

    # Find the specific card containing the Ready to claim text
    print(f"{AZUL}[i]: Searching for 'Ready to claim' card...{RESET}")
    
    claim_card = (
        dashboard_page.locator('div[class*="p-paddingCardDefault"]')
        .filter(has_text="Ready to claim")
        .first
    )

    if claim_card.count() > 0 and claim_card.is_visible():
        print(f"{AZUL}[i]: 'Ready to claim' card found! Clicking...{RESET}")
        claim_card.click(force=True)
        dashboard_page.wait_for_timeout(2000)

    else:
        print(
            f"{AMARILLO}[!]: 'Ready to claim' card not visible or already"
            f" claimed.{RESET}"
        )

    # Click the final claim button inside the active modal or card
    print(f"{AZUL}[i]: Looking for final claim button...{RESET}")
    
    final_claim_btn = (
        dashboard_page.locator('button[class*="bg-bgCtrlBrandRest"]')
        .filter(has_text="Claim")
        .first
    )

    # Use a class-based fallback when button has no visible text
    if final_claim_btn.count() == 0:
        final_claim_btn = dashboard_page.locator(
            'button[class*="bg-bgCtrlBrandRest"][class*="min-h-sizeCtrlLgDefault"]'
        ).first

    if final_claim_btn.count() > 0 and final_claim_btn.is_visible():
        final_claim_btn.click(force=True)

        print(f"{VERDE}[+] Points claimed successfully!{RESET}")
        dashboard_page.wait_for_timeout(2500)

    else:
        print(
            f"{AMARILLO}[!]: Final claim button not active. Nothing to claim.{RESET}"
        )

    dashboard_page.close()

  except Exception as e:
    print(f"{ROJO}[ER]: Error claiming accumulated points at {e}{RESET}")



# Run the Bing search cycle (mobile device profile)
def execMobileSearch():
    print(f"\n{VERDE}(+) Starting Bing Rewards Bot (A16 5G Mobile mode)...{RESET}")

    with sync_playwright() as pw:
        context = launchEdgeContext(pw, SAMSUNG_A16_5G_CONF)
        page = activePage(context)

        try:
            print(f"{AZUL}[...] Connecting to Microsoft Bing.\n{RESET}")
            page.goto("https://www.bing.com", wait_until="domcontentloaded")
            time.sleep(random.uniform(3.85, 5.95))

            random.shuffle(KEYWORDS)
            MOBILEDAILYSEARCH = KEYWORDS[:1]

            for idx, keyword in enumerate(MOBILEDAILYSEARCH, 1):
                print(f"• ({idx}/{len(MOBILEDAILYSEARCH)}) Searching:\n'{keyword}...'")

                typeSearch(page, keyword)

                wait_time = random.uniform(4.35, 6.05)
                time.sleep(wait_time)

            print(f"\n{VERDE}[✓] Searching cycle has been completed succesfully.{RESET}")
            time.sleep(1)
            return True

        except Exception as e:
            print(f"\n{ROJO}[ER]: Error during Mobile bot execution at {e}{RESET}")
            return False

        finally:
            context.close()


# Run the Bing search cycle (desktop device profile)
def execDesktopSearch():
    print(f"\n{VERDE}(+) Starting Bing Rewards Bot (Desktop Mode)...{RESET}")

    with sync_playwright() as pw:
        context = launchEdgeContext(pw, DESKTOP_CONF)
        page = activePage(context)

        try:
            print(f"{AZUL}[...] Connecting to Microsoft Bing.{RESET}\n")
            page.goto("https://www.bing.com", wait_until="domcontentloaded")
            time.sleep(random.uniform(3.85, 5.95))

            random.shuffle(KEYWORDS)
            DAILYSEARCH = KEYWORDS[:1]

            for idx, keyword in enumerate(DAILYSEARCH, 1):
                print(f"• ({idx}/{len(DAILYSEARCH)}) Searching (Desktop):\n'{keyword}...'")

                typeSearch(page, keyword)

                wait_time = random.uniform(4.35, 6.05)
                time.sleep(wait_time)
                
            claimPoints(page, context)

            print(f"\n{VERDE}[✓] Desktop searching cycle has been completed successfully.{RESET}")
            time.sleep(1)
            return True


        except Exception as e:
            print(f"\n{ROJO}[ER]: Error during desktop bot execution at {e}{RESET}")
            return False

        finally:
            context.close()


def mainCron():
   print("Starting scheduled cron cycle...")
   try:  
        if not execDesktopSearch():
                return
            
        print(f"\n{AMARILLO}[$] Intermission: Profile switching in 2 seconds...{RESET}") # executions
        time.sleep(2)

        if not execMobileSearch():
            return

        recordRunToday()

   except Exception as e:
    print(f"{ROJO}[ER]: Error in mainCron: {e}{RESET}")

schedule.every().day.at("15:56").do(mainCron)
            
if __name__ == "__main__":
    print("[i] Rewards Daemon active. Waiting for scheduled tasks...")

    if not hasRunToday():
        print(
        f"{AMARILLO}[i] Task hasn't run today (boot after scheduled time)."
        f" Running now...{RESET}"
        )
        mainCron()
    
    while True:
        schedule.run_pending()
        time.sleep(60)