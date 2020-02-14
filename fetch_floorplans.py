import os  
import sys
from selenium import webdriver  
from selenium.webdriver.common.keys import Keys  
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DUO_PATH = "/Users/georgiashay/Documents/Software/duo-cli"
sys.path.append(DUO_PATH)
from duo_gen import generate_next_token

SEARCH_URL = "https://floorplans.mit.edu/SearchPDF.Asp"
LIST_URL = "https://floorplans.mit.edu/ListPDF.Asp?Bldg="
SCRIPT_LOCATION = os.path.abspath('')
DATA_FOLDER = os.path.join(SCRIPT_LOCATION, 'data/')

class AnyEC:
    """ Use with WebDriverWait to combine expected_conditions
        in an OR.
    """
    def __init__(self, *args):
        self.ecs = args
    def __call__(self, driver):
        for fn in self.ecs:
            try:
                result = fn(driver)
                if result:
                    return result
            except:
                pass
        return False

def login_to_page(driver, page, wait_until):
    wait = WebDriverWait(driver, 10)
    driver.get(page)
    
    wait.until(AnyEC(wait_until, EC.element_to_be_clickable((By.ID, "Select"))))
    
    if driver.current_url == page:
        return
    
    # Click login continue button when it appears
    wait.until(EC.element_to_be_clickable((By.ID, "Select"))).click()
    
    # Click login by certificate button when it appears
    wait.until(EC.element_to_be_clickable((By.NAME, "login_certificate"))).click()

    # Jump into iframe for entering passcode
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'duo_iframe')))
    
    # Choose passcode duo authentication method
    passcode_button = driver.find_element_by_id("passcode")
    passcode_button.click()
    
    # Get passcode input
    passcode_input = driver.find_element_by_name("passcode")
    
    # Generate next passcode and input it
    next_password = generate_next_token()
    passcode_input.send_keys(next_password)
    
    # Submit the passcode to duo
    passcode_button.click()
    
    # Wait until logged in
    wait.until(wait_until)

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