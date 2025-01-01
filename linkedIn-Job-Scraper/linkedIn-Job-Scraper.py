import csv,re,time, warnings
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common import keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

PATH = "chromedriver.exe"
cService = webdriver.ChromeService(executable_path='chromedriver.exe')

def warn(*args, **kwargs):#ingore deprecation warnings
    pass
warnings.warn = warn
        
def writeToCSV(JOB, COMPANY, LOCATION, PAY, JOB_LEVEL, EMPLOYMENT_TYPE, DESCRIPTION, URL, KEYWORD, LOGO):
    try:
        with open(f"{KEYWORD}.csv", "a", newline='') as f:
            writer = csv.writer(f)
            #writer.writerow([JOB, COMPANY, LOCATION, PAY, JOB_LEVEL, EMPLOYMENT_TYPE, DESCRIPTION, LOGO, URL])
            writer.writerow([JOB, COMPANY, LOCATION, PAY, JOB_LEVEL, EMPLOYMENT_TYPE, LOGO, URL])
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
               
def search(driver, KEYWORD, city):#HomeCardContainer selectedHomeCard
    searchbar = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search job titles or companies']"))) 
    searchbar.send_keys(KEYWORD)
    
    citySearch = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Location']")))
    citySearch.send_keys(Keys.CONTROL, 'a')
    citySearch.send_keys(Keys.DELETE)
    citySearch.send_keys(city)
    
    searchbar.send_keys(Keys.RETURN)
    time.sleep(0.5)
    try:
        WebDriverWait(driver, 1.5).until(EC.presence_of_element_located((By.XPATH, "//button[@class='popover-x-button-close icl-CloseButton']"))).click()
    except:
        pass
    time.sleep(2)
    listings = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@data-search-id]")))
    print(f"Total Job Listings: {len(listings)}")
    
    for listing in listings:
        listing.click()
        time.sleep(1)

        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//button[contains(text(),'Save')]")))
        time.sleep(1.5)
        
        scrapeData(driver, listing, KEYWORD)
        time.sleep(0.5)
           
def scrapeData(driver, job_listing, KEYWORD):#//*[@class="statsValue"]
    try:
        job_url = job_listing.find_element_by_xpath(".//a").get_attribute("href")#job site link if apply link not available
    except:
        job_url = "N/A"
    
    try:
        job_name = driver.find_element_by_xpath("//h2[contains(@class,'top-card-layout__title')]").text
    except:
        job_name = "N/A"
    
    try:
        company_Name = driver.find_element_by_xpath("//a[@data-tracking-control-name='public_jobs_topcard-org-name']").text
    except:
        company_Name = "N/A"
    
    try:
        logo = job_listing.find_element_by_xpath(".//img").get_attribute("src")
    except:
        logo = "N/A"
    
    try:
        location = driver.find_element_by_xpath("//span[@class='topcard__flavor topcard__flavor--bullet']").text
    except:
        location = "N/A"
        
    try:
        pay = driver.find_element_by_xpath("//div[@class='salary compensation__salary']").text
    except:
        pay = "N/A"
    
    try:
        job_level = driver.find_element_by_xpath("//ul[@class='description__job-criteria-list']/li[1]/span").text
    except:
        job_level = "N/A"
    
    try:
        employment_type = driver.find_element_by_xpath("//ul[@class='description__job-criteria-list']/li[2]/span").text
    except:
        employment_type = "N/A"
    
    try:
        desc = driver.find_element_by_xpath("//section[@class='show-more-less-html']/div").text
    except:
        desc= "N/A"
    desc = re.sub(r'^$\n', '', desc, flags=re.MULTILINE)    #remove empty lines
    
    writeToCSV(job_name, company_Name, location, pay, job_level, employment_type, desc,job_url, KEYWORD, logo)
    
def main():
    KW = input("Enter a keyword to search for: ")
    CITY= input("Enter a city/area to search in: ")
    #KW = "software engineer"
    #CITY= "ottawa"
    #check if file exists, if not create it
    try:
        open(f"{KW}.csv", "r")
    except:
        with open(f"{KW}.csv", "w", newline='') as f:
            writer = csv.writer(f)
            #writer.writerow(["JOB", "COMPANY", "LOCATION", "PAY", "JOB LEVEL", "EMPLOYMENT TYPE", "DESCRIPTION", "LOGO", "JOB URL"])
            writer.writerow(["JOB", "COMPANY", "LOCATION", "PAY", "JOB LEVEL", "EMPLOYMENT TYPE", "LOGO", "JOB URL"])
    driver = webdriver.Chrome(service = cService)  
    driver.get("https://ca.indeed.com/")
    driver.set_window_size(1024, 600)
    driver.maximize_window()
    time.sleep(0.5)
    search(driver, KW, CITY)
    driver.quit()

main()
input("")  
