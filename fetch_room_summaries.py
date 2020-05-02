import os  
import sys
from selenium import webdriver  
from selenium.webdriver.common.keys import Keys  
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from login_with_duo import login_to_page

SCRIPT_LOCATION = os.path.abspath('')
DATA_FOLDER = os.path.join(SCRIPT_LOCATION, 'rooms/')

LIST_URL="https://floorplans.mit.edu/cgi-bin-db-mit/wdbmitscript.asp?Report=ibrl&Item=MIT"
HOME_URL="https://floorplans.mit.edu/mit-room.html"
ROOM_URL="https://floorplans.mit.edu/cgi-bin-db-mit/wdbmitscript.asp?report=brl&item="

chrome_options = Options()  
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--ignore-urlfetcher-cert-requests")
chrome_options.add_experimental_option("prefs", {
    "plugins.always_open_pdf_externally": True,
    "download.default_directory" : DATA_FOLDER,
    'profile.managed_auto_select_certificate_for_urls': ['{"pattern":"https://idp.mit.edu:446","filter":{"ISSUER":{"OU":"Client CA v1"}}}']
    })  


def get_building_list(driver):
    menu = driver.find_element_by_tag_name("menu")
    building_selects = menu.find_elements_by_tag_name("a")
    building_names = [building_select.get_attribute("text").strip() for building_select in building_selects]
    return building_names


def download_texts(driver):
    original_url = driver.current_url
    
    wait = WebDriverWait(driver, 3)
    building_names = get_building_list(driver)
    
    for building_name in building_names:
        driver.get(ROOM_URL + building_name)
        
        try:
            wait.until(EC.visibility_of_element_located((By.TAG_NAME, 'pre')))
        except TimeoutException:
            print("Could not get information for " + building_name)
            continue
        
        text_tag = driver.find_element_by_tag_name("pre")
        text = text_tag.text
        
        with open(os.path.join(DATA_FOLDER, building_name + '.txt'), 'w+') as f:
            f.write(text)
    
    driver.get(original_url)
    
    
def get_room_use_texts():
    driver = webdriver.Chrome(options=chrome_options)  
    home_page_condition = EC.visibility_of_element_located((By.CLASS_NAME, "paddingLogo"))
    login_to_page(driver, HOME_URL, home_page_condition)
    
    driver.get(LIST_URL)
    wait = WebDriverWait(driver, 10)
    room_summary_condition = EC.visibility_of_element_located((By.TAG_NAME, "menu"))
    wait.until(room_summary_condition)
    
    download_texts(driver)
    
    driver.quit()
    
if __name__ == "__main__":
    get_room_use_texts()