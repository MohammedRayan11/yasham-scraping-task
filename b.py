from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# Set up the driver
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)

# Go to search page
driver.get("https://search.earth911.com/")
time.sleep(3)

# Fill search form
driver.find_element(By.ID, "what").send_keys("Electronics")
driver.find_element(By.ID, "where").send_keys("10001")
driver.find_element(By.ID, "submit-location-search").click()

# Wait for results
wait.until(EC.presence_of_element_located((By.CLASS_NAME, "result-item")))
time.sleep(2)

# Set radius to 100 miles
try:
    radius_dropdown = Select(driver.find_element(By.XPATH, "//select[@onchange]"))
    radius_dropdown.select_by_value("100")
    time.sleep(3)  # wait for results to reload
except Exception as e:
    print("Could not set radius:", e)

# Scrape first 3 results
data = []

for i in range(3):
    # Refresh program links after each navigation
    links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[href*="/program/"]')))

    # Store name and link
    # Store name and link
    facility_divs = driver.find_elements(By.CLASS_NAME, "result-item")

    try:
        program_name = facility_divs[i].find_element(By.CLASS_NAME, "title").text.strip().split('+')[0].strip()
    except:
        program_name = "N/A"

    try:
        program_link = links[i].get_attribute("href")
    except:
        program_link = "N/A"



    # Extract container div before clicking
    facility_divs = driver.find_elements(By.CLASS_NAME, "result-item")
    try:
        address = facility_divs[i].find_element(By.CLASS_NAME, "contact").text.strip().replace("\n", ", ")
    except:
        address = "N/A"

    try:
        materials = facility_divs[i].find_element(By.CLASS_NAME, "result-materials").text.strip()
    except:
        materials = "N/A"

    # Click to go into program detail page
    links[i].click()
    time.sleep(2)

    # Get updated date
    try:
        updated = driver.find_element(By.CSS_SELECTOR, "span.last-verified").text.replace("Updated", "").strip()
    except:
        updated = "N/A"

    # Add result to list
    data.append({
        "business_name": program_name,
        "street_address": address,
        "materials_accepted": materials,
        "last_update_date": updated,
        "detail_page_url": program_link
    })

    # Go back to result list
    try:
        back_link = driver.find_element(By.LINK_TEXT, "Back")
        back_link.click()
    except:
        driver.back()
    time.sleep(2)

# Save to CSV
df = pd.DataFrame(data)
df.to_csv("earth911_facilities_full.csv", index=False)
print("✅ Scraping complete. Data saved to 'earth911_facilities_full.csv'.")

driver.quit()
