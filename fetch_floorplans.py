import os  
import sys
from selenium import webdriver  
from selenium.webdriver.common.keys import Keys  
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from login_with_duo import login_to_page

SEARCH_URL = "https://floorplans.mit.edu/SearchPDF.Asp"
LIST_URL = "https://floorplans.mit.edu/ListPDF.Asp?Bldg="
SCRIPT_LOCATION = os.path.abspath('')
DATA_FOLDER = os.path.join(SCRIPT_LOCATION, 'data/')

def get_building_list(driver):
    building_select = driver.find_element_by_name("Bldg")
    building_options = building_select.find_elements_by_tag_name("option")
    building_names = [building_option.get_attribute("value") for building_option in building_options]
    return building_names

def download_all_floorplans(driver):
    wait = WebDriverWait(driver, 10)
    building_names = get_building_list(driver)
    
    for building_name in building_names:
        driver.get(LIST_URL + building_name)
        
        wait.until(EC.visibility_of_element_located((By.ID, 'maincontent')))
        
        floor_links = driver.find_elements_by_xpath('//a[contains(@href,"/pdfs/")]')
        for floor_link in floor_links:
            floor_link.click()
        
def reorganize_floorplans():
    buildings = {}
    for filename in os.listdir(DATA_FOLDER):
        if filename.endswith(".pdf"):
            base_filename = os.path.splitext(filename)[0]
            building, floor = base_filename.split('_')
            if building in buildings:
                buildings[building].add(filename)
            else:
                buildings[building] = {filename}
    for building in buildings:
        building_folder = os.path.join(DATA_FOLDER, building+'/')
        os.mkdir(building_folder)
        for file in buildings[building]:
            current_path = os.path.join(DATA_FOLDER, file)
            new_path = os.path.join(building_folder, file)
            os.rename(current_path, new_path)
            
    
def fetch_floorplans():
    chrome_options = Options()  
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--ignore-urlfetcher-cert-requests")
    chrome_options.add_experimental_option("prefs", {
        "plugins.always_open_pdf_externally": True,
        "download.default_directory" : DATA_FOLDER,
        'profile.managed_auto_select_certificate_for_urls': ['{"pattern":"https://idp.mit.edu:446","filter":{"ISSUER":{"OU":"Client CA v1"}}}']
        })  
    
    driver = webdriver.Chrome(options=chrome_options)  
    login_to_page(driver, SEARCH_URL, EC.visibility_of_element_located((By.NAME, "Bldg")))
    download_all_floorplans(driver)
    reorganize_floorplans()
    driver.quit()

if __name__ == "__main__":
    fetch_floorplans()
