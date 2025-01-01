import csv, re, time, warnings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

PATH = "chromedriver.exe"

def warn(*args, **kwargs):#ingore deprecation warnings
    pass
warnings.warn = warn

with open("account.txt", "r") as file:#read account details
    data = file.read().replace(" ", "").strip()
    EMAIL, PASSWORD = data.split(":")
    
def writeToCSV(COMPANY, LOCATION, LOGO, INDUSTRY, DESCRIPTION, URL):
    try:
        with open(f"Companies.csv", "a", newline='') as f:
            writer = csv.writer(f)
            #writer.writerow([COMPANY, LOCATION, f"=IMAGE('{LOGO}')", LOGO, INDUSTRY, DESCRIPTION, URL])
            writer.writerow([COMPANY, LOCATION, f"=IMAGE('{LOGO}')", LOGO, INDUSTRY, URL])
    except (UnicodeDecodeError, UnicodeEncodeError):
        pass
        
def main(driver): #cycle through pages and open in new tab
    while True:
        company_results = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='display-flex']/span/span/a"))) 
    
        for company in company_results:
            driver.execute_script("arguments[0].scrollIntoView();",company)
            companyURL = company.get_attribute('href')#get link
            
            driver.execute_script("window.open('');")#open new window
            driver.switch_to.window(driver.window_handles[1])
            driver.get(f"{companyURL}about/")
            
            scrapeData(driver)
            
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Next']"))).click()
        except:
            break

def scrapeData(driver):#//*[@class="statsValue"]
    company_name = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//h1/span"))).text
    
    location = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='inline-block']/div"))).text
    
    industry = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='org-top-card-summary-info-list__info-item'][1]"))).text
    
    logo = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='org-top-card-primary-content__logo-container']/img"))).get_attribute('src')
    
    url = driver.current_url
    
    desc = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='ember-view']/section/p"))).text
    desc = desc.replace("\n", "").strip()
    desc = re.sub(r'^$\n', '', desc, flags=re.MULTILINE)#remove empty lines
    
    writeToCSV(company_name, location, logo, industry, desc, url)

def login(driver):
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'Sign in')]"))).click()#click sign in
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(EMAIL)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password"))).send_keys(PASSWORD)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(),'Sign in')]"))).click()
    
def start():
    #check if file exists, if not create it
    try:
        open(f"Companies.csv", "r")
    except:
        with open(f"Companies.csv", "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["COMPANY", "LOCATION", "LOGO", "LOGO URL", "INDUSTRY", "DESCRIPTION", "URL"])
    
    driver = webdriver.Chrome(PATH)     
    driver.get("https://www.linkedin.com/search/results/companies/?origin=GLOBAL_SEARCH_HEADER&sid=(0~")
    driver.set_window_size(1024, 600)
    driver.maximize_window()
    time.sleep(0.5)
    login(driver)
    
    main(driver)
    driver.quit()
 
start()
input("")  
