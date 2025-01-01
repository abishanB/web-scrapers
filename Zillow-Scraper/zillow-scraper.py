import csv,time, warnings
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def warn(*args, **kwargs):#ingore deprecation warnings
    pass
warnings.warn = warn

PATH = "chromedriver.exe"
#KW = input("Enter keyword to search for: ")#keyword
KW="Portland"

#driver.find_element_by_css_selector("svg[class^='svg-circle-plus']").click()

#check if file exists, if not create it
try:
    open("data.csv", "r")
except:
    with open("data.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["PRICE", "SQ FT", "BEDS", "BATHS", "STREET ADDRESS", "CITY & ZIP", "PHONE"])
        
def writeToCSV(PRICE, BEDS, BATHS, SQ_FT, ADDRESS, ZIP, PHONE):
    with open("data.csv", "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([PRICE, SQ_FT, BEDS, BATHS, ADDRESS, ZIP, PHONE])

def search(driver):
    searchbar = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.ID, "search-box-input"))) 
    searchbar.send_keys(KW)
    time.sleep(1.5)
    searchbar.send_keys(" ")
    time.sleep(1)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "react-autowhatever-1--item-0"))).click() #click result
    time.sleep(2.5)

    try:#answer pop up
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, "//button[@class='StyledButton-c11n-8-48-0__sc-wpcbcc-0 bCYrmZ']"))).click()
    except:
        pass
    
    listings = WebDriverWait(driver, 100).until(EC.presence_of_all_elements_located((By.XPATH, "//li/article")))
    print(f"Listings Found: {len(listings)}")
    for listing in listings:

        listing.click()
        time.sleep(2)
        scrapeData(driver)
        time.sleep(0.5)
        closeButton = driver.find_element_by_xpath("//button[@aria-label='close']")
        driver.execute_script("arguments[0].click();", closeButton)
        time.sleep(0.5)
        
        
def scrapeData(driver):
    PRICE = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//span[@class='Text-c11n-8-48-0__sc-aiai24-0 hdp__qf5kuj-3 cpRTaJ']/span/span"))).text
    bedBath = driver.find_elements_by_xpath("//span[@class='hdp__qf5kuj-4 jGniAU']")
    BEDS = bedBath[0].find_element_by_xpath(".//span").text
    BATHS = bedBath[1].find_element_by_xpath(".//span").text
    
    
    addressSplit = driver.find_element_by_xpath("//h1[@id='ds-chip-property-address']").text.split(",")
    ADDRESS = addressSplit[0]
    ZIP = addressSplit[1] + addressSplit[2]
    
    #click show more
    driver.find_element_by_xpath("//button[@class='hdp__sc-19crqy3-3 juDQBb ds-expandable-card-footer-text ds-text-button']").click()
    
    try:
        SQ_FT = driver.find_element_by_css_selector("span[class^='Square Feet']").click()
    except:
        SQ_FT = "N/A"
    
    
    try:
        PHONE = driver.find_element_by_xpath("//div[@class='ds-body-small']/span[3]").text
    except:
        PHONE = "N/A"
    
    writeToCSV(PRICE, BEDS, BATHS, SQ_FT, ADDRESS, ZIP, PHONE)
    time.sleep(1.5)
    
    
if  __name__ == '__main__':
    driver = uc.Chrome()  
    driver.get("https://www.zillow.com/")
    driver.set_window_size(1024, 600)
    driver.maximize_window()
    time.sleep(0.5)

    search(driver)
    driver.quit()


    

                
       
