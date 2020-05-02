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