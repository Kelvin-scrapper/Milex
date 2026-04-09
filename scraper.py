"""
SIPRI Military Expenditure Scraper
====================================
Dataset : MILEX
Source  : https://www.sipri.org/databases/milex
Output  : downloads/SIPRI-Milex-data-*.xlsx  (raw SIPRI workbook)
Usage   : python scraper.py
"""

import os
import re
import subprocess
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DATASET_CODE  = "MILEX"
OUTPUT_PREFIX = "MILEX"
OUTPUT_DIR    = "downloads"
URL           = "https://www.sipri.org/databases/milex"
TIMEOUT       = 30


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _get_chrome_major_version() -> int | None:
    """Detect the installed Chrome major version from the Windows registry."""
    commands = [
        r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version',
        r'reg query "HKLM\SOFTWARE\Google\Chrome\BLBeacon" /v version',
        r'powershell -command "(Get-Item \"C:\Program Files\Google\Chrome\Application\chrome.exe\").VersionInfo.FileVersion"',
        r'powershell -command "(Get-Item \"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe\").VersionInfo.FileVersion"',
    ]
    for cmd in commands:
        try:
            out = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode()
            m = re.search(r'(\d+)\.\d+\.\d+\.\d+', out)
            if m:
                return int(m.group(1))
        except Exception:
            continue
    return None


def _dismiss_popup(driver) -> None:
    """Attempt to close the SIPRI donate popup if present."""
    try:
        driver.execute_script("""
            var popup = document.querySelector('.sipri-2016-donatepopup-modal');
            if (popup) { popup.style.display = 'none'; popup.remove(); }
        """)
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
        time.sleep(1)
        for sel in ['.sipri-2016-donatepopup-modal .close', '.modal-close',
                    '.popup-close', '[data-dismiss="modal"]']:
            try:
                el = driver.find_element(By.CSS_SELECTOR, sel)
                if el.is_displayed():
                    el.click()
                    time.sleep(1)
                    break
            except NoSuchElementException:
                continue
    except Exception:
        pass


def _parse_value(raw) -> float | None:
    """Strip commas/symbols and return float, or None if unparseable."""
    try:
        return float(str(raw).replace(',', '').strip())
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Fetch
# ---------------------------------------------------------------------------

def _fetch_sipri_excel() -> str | None:
    """
    Opens the SIPRI milex page with an undetected Chrome driver,
    locates the Excel download link, and saves the file to OUTPUT_DIR.
    Returns the path to the downloaded file, or None on failure.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    download_dir = os.path.abspath(OUTPUT_DIR)

    options = uc.ChromeOptions()
    options.add_experimental_option("prefs", {
        "download.default_directory":   download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade":   True,
        "safebrowsing.enabled":         True,
    })
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = None
    try:
        print("Initializing Chrome driver...")
        chrome_version = _get_chrome_major_version()
        if chrome_version:
            print(f"Detected Chrome version: {chrome_version}")
            driver = uc.Chrome(options=options, version_main=chrome_version)
        else:
            print("Chrome version not detected — using auto-detection")
            driver = uc.Chrome(options=options)

        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        print(f"Navigating to {URL} ...")
        driver.get(URL)
        WebDriverWait(driver, TIMEOUT)
        time.sleep(3)

        _dismiss_popup(driver)

        # Find the Excel download link
        download_url = None
        for sel in ['//a[contains(@href, ".xlsx")]', '//a[contains(@href, ".xls")]',
                    'a[href*=".xlsx"]', 'a[href*=".xls"]']:
            try:
                el = (driver.find_element(By.XPATH, sel) if sel.startswith('//')
                      else driver.find_element(By.CSS_SELECTOR, sel))
                href = el.get_attribute('href')
                if href:
                    download_url = href
                    break
            except NoSuchElementException:
                continue

        if not download_url:
            print("[WARN] Excel download link not found on page")
            return None

        print(f"Downloading: {download_url}")
        driver.get(download_url)
        time.sleep(10)

        # Return the most recently modified xlsx in the downloads folder
        xlsx_files = [
            os.path.join(download_dir, f) for f in os.listdir(download_dir)
            if f.endswith(('.xlsx', '.xls')) and not f.startswith('~')
        ]
        if xlsx_files:
            latest = max(xlsx_files, key=os.path.getmtime)
            print(f"Downloaded: {latest}")
            return latest

        print("[WARN] No Excel file found in downloads folder")
        return None

    except Exception as e:
        url = driver.current_url if driver else "driver not initialized"
        print(f"[ERROR] {e}")
        print(f"Current URL: {url}")
        return None

    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


# ---------------------------------------------------------------------------
# Scrape orchestrator
# ---------------------------------------------------------------------------

def scrape() -> str | None:
    """Run the full download pipeline. Returns path to downloaded file."""
    print(f"\n{'='*50}")
    print(f"SIPRI Military Expenditure Scraper — {DATASET_CODE}")
    print(f"{'='*50}")
    return _fetch_sipri_excel()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    """Entry point. Supports --all flag (reserved for future backfill)."""
    result = scrape()
    if result:
        print(f"\nScrape complete: {result}")
    else:
        print("\n[ERROR] Scrape failed — check logs above")


if __name__ == "__main__":
    main()
