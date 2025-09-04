import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os

def download_sipri_military_database():
    """
    Downloads the SIPRI Military Expenditure Database from sipri.org
    """
    # Setup undetected Chrome driver
    options = uc.ChromeOptions()
    
    # Set download directory (optional - customize as needed)
    download_dir = os.path.join(os.getcwd(), "downloads")
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    # Configure Chrome preferences for downloads
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)
    
    # Additional options for better compatibility
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = None
    
    try:
        # Initialize the driver
        print("Initializing Chrome driver...")
        driver = uc.Chrome(options=options, version_main=139)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Navigate to SIPRI homepage
        print("Navigating to SIPRI website...")
        driver.get("https://www.sipri.org/")
        
        # Wait for page to load
        wait = WebDriverWait(driver, 15)
        
        # Handle any popup modals that might appear
        try:
            print("Checking for popup modals...")
            time.sleep(3)
            
            # Try to hide popup with JavaScript
            try:
                driver.execute_script("""
                    var popup = document.querySelector('.sipri-2016-donatepopup-modal');
                    if (popup) {
                        popup.style.display = 'none';
                        popup.style.visibility = 'hidden';
                        popup.remove();
                    }
                """)
                print("Attempted to hide popup with JavaScript")
            except:
                pass
            
            # Try pressing ESC key to close popup
            try:
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                print("Pressed ESC key to close popup")
                time.sleep(1)
            except:
                pass
            
            # Look for common popup close buttons
            popup_selectors = [
                '.sipri-2016-donatepopup-modal .close',
                '.modal-close',
                '.popup-close',
                '[data-dismiss="modal"]',
                '.sipri-2016-donatepopup-modal'
            ]
            
            for selector in popup_selectors:
                try:
                    popup_element = driver.find_element(By.CSS_SELECTOR, selector)
                    if popup_element.is_displayed():
                        # Try clicking close button first
                        if 'close' in selector:
                            popup_element.click()
                            print("Clicked popup close button")
                        else:
                            # If it's the modal itself, try to hide it
                            driver.execute_script("arguments[0].style.display = 'none';", popup_element)
                            print("Hidden popup modal")
                        time.sleep(1)
                        break
                except NoSuchElementException:
                    continue
                except Exception as e:
                    print(f"Error handling popup element: {e}")
                    continue
            
        except Exception as e:
            print(f"No popup to close or error handling popup: {e}")
        
        # Find and click on "Databases" link
        print("Looking for Databases link...")
        databases_link = None
        
        # Try multiple approaches to find the databases link
        database_selectors = [
            'a[href="/databases"]',
            'a[href*="databases"]',
            '//a[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "databases")]',
            '//a[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "database")]'
        ]
        
        for selector in database_selectors:
            try:
                if selector.startswith('//'):
                    databases_link = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                else:
                    databases_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                if databases_link:
                    print(f"Found databases link using selector: {selector}")
                    break
            except TimeoutException:
                continue
        
        if databases_link:
            driver.execute_script("arguments[0].scrollIntoView(true);", databases_link)
            time.sleep(1)
            databases_link.click()
            print("Clicked on Databases link")
        else:
            print("Could not find Databases link, searching for any relevant navigation...")
            # Look for any navigation element that might lead to databases
            nav_links = driver.find_elements(By.TAG_NAME, "a")
            for link in nav_links:
                if any(keyword in link.text.lower() for keyword in ['data', 'research', 'resources']):
                    print(f"Trying navigation link: {link.text}")
                    link.click()
                    time.sleep(3)
                    break
            else:
                print("Could not find suitable navigation link")
                return
        
        # Wait for databases page to load
        time.sleep(3)
        
        # Scroll down to find the SIPRI Military Expenditure Database
        print("Scrolling to find SIPRI Military Expenditure Database...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(2)
        
        # Look for the Military Expenditure Database link
        try:
            # Try multiple selectors to find the link
            milex_selectors = [
                'a[href="/databases/milex"]',
                'a[href*="milex"]',
                '//a[contains(@href, "milex")]',
                '//a[contains(text(), "Military Expenditure Database")]'
            ]
            
            milex_link = None
            for selector in milex_selectors:
                try:
                    if selector.startswith('//'):
                        milex_link = driver.find_element(By.XPATH, selector)
                    else:
                        milex_link = driver.find_element(By.CSS_SELECTOR, selector)
                    if milex_link:
                        break
                except NoSuchElementException:
                    continue
            
            if not milex_link:
                # If direct link not found, try searching for text content
                milex_link = driver.find_element(By.XPATH, "//a[contains(text(), 'SIPRI Military Expenditure Database')]")
            
            print("Found Military Expenditure Database link")
            driver.execute_script("arguments[0].scrollIntoView(true);", milex_link)
            time.sleep(1)
            milex_link.click()
            print("Clicked on Military Expenditure Database link")
            
        except NoSuchElementException:
            print("Could not find Military Expenditure Database link, trying text-based search...")
            # Try searching for any link containing military expenditure related text
            try:
                military_keywords = [
                    "military expenditure",
                    "milex",
                    "defence expenditure", 
                    "defense expenditure",
                    "military spending"
                ]
                
                found_link = None
                for keyword in military_keywords:
                    try:
                        found_link = driver.find_element(By.XPATH, f"//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword}')]")
                        if found_link:
                            print(f"Found link using keyword: {keyword}")
                            break
                    except NoSuchElementException:
                        continue
                
                if found_link:
                    found_link.click()
                    print("Clicked on found military expenditure link")
                else:
                    print("Could not find any military expenditure related links")
                    return
                    
            except Exception as search_error:
                print(f"Error in text-based search: {search_error}")
                return
        
        # Wait for the milex page to load
        time.sleep(3)
        
        # Look for the Excel download link
        print("Looking for Excel download link...")
        
        # Try multiple approaches to find the download link
        download_selectors = [
            '//a[contains(@href, ".xlsx")]',
            '//a[contains(@href, ".xls")]',
            '//a[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "download") and contains(@href, "milex")]',
            '//a[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "excel")]',
            '//a[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "data")]',
            'a[href*=".xlsx"]',
            'a[href*=".xls"]'
        ]
        
        download_link = None
        for selector in download_selectors:
            try:
                if selector.startswith('//'):
                    download_link = driver.find_element(By.XPATH, selector)
                else:
                    download_link = driver.find_element(By.CSS_SELECTOR, selector)
                if download_link:
                    break
            except NoSuchElementException:
                continue
        
        if download_link:
            download_url = download_link.get_attribute('href')
            print(f"Found download link: {download_url}")
            
            # Try direct navigation to download the file
            try:
                print("Navigating directly to download URL...")
                driver.get(download_url)
                time.sleep(5)
                print("Direct download initiated.")
            except Exception as direct_error:
                print(f"Direct download failed: {direct_error}")
                # Fallback to JavaScript click to avoid popup interference
                try:
                    print("Trying JavaScript click...")
                    driver.execute_script("arguments[0].click();", download_link)
                    print("JavaScript click executed - file should start downloading...")
                    time.sleep(5)
                except Exception as js_error:
                    print(f"JavaScript click failed: {js_error}")
            
            print(f"Download should be complete. Check your downloads folder: {download_dir}")
            
        else:
            print("Could not find the Excel download link")
            # Print page source for debugging
            print("Page title:", driver.title)
            print("Current URL:", driver.current_url)
            
            # Look for any links containing file extensions or relevant keywords
            all_links = driver.find_elements(By.TAG_NAME, "a")
            potential_links = []
            
            for link in all_links:
                href = link.get_attribute('href') or ''
                text = link.text.lower()
                
                # Check for file extensions
                if any(ext in href.lower() for ext in ['.xlsx', '.xls', '.csv']):
                    potential_links.append(('file_extension', link, href))
                # Check for download-related text
                elif any(keyword in text for keyword in ['download', 'excel', 'data', 'file']):
                    potential_links.append(('download_text', link, href))
                # Check for military/expenditure related content
                elif any(keyword in text for keyword in ['military', 'expenditure', 'spending', 'defence', 'defense']):
                    potential_links.append(('military_related', link, href))
            
            if potential_links:
                print("Found potential download links:")
                # Prioritize by type: file extensions first, then download text, then military related
                potential_links.sort(key=lambda x: ['file_extension', 'download_text', 'military_related'].index(x[0]))
                
                for link_type, link, href in potential_links[:5]:
                    print(f"  [{link_type}] {link.text[:50]}... -> {href}")
                
                # Try the most promising link
                for link_type, link, href in potential_links:
                    if link_type == 'file_extension':  # Prioritize actual file links
                        try:
                            print(f"Attempting to download: {href}")
                            if href:
                                driver.get(href)
                                print("Direct download attempted via URL navigation")
                                time.sleep(5)
                                break
                            else:
                                driver.execute_script("arguments[0].click();", link)
                                print("Clicked potential download link via JavaScript")
                                time.sleep(5)
                                break
                        except Exception as click_error:
                            print(f"Error clicking link: {click_error}")
                            continue
            else:
                print("No potential download links found on the page")
        
    except TimeoutException:
        print("Timeout occurred while waiting for page elements")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print(f"Current URL: {driver.current_url if driver else 'Driver not initialized'}")
        
    finally:
        if driver:
            print("Closing browser...")
            try:
                time.sleep(2)  # Give time for any downloads to complete
                driver.quit()
            except Exception as quit_error:
                print(f"Error during driver cleanup: {quit_error}")
                # Force close if normal quit fails
                try:
                    driver.close()
                except:
                    pass

def main():
    """
    Main function to run the SIPRI database downloader
    """
    print("SIPRI Military Expenditure Database Downloader")
    print("=" * 50)
    
    try:
        download_sipri_military_database()
        print("\nScript completed. Please check your downloads folder for the Excel file.")
        
    except KeyboardInterrupt:
        print("\nScript interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")

if __name__ == "__main__":
    main()