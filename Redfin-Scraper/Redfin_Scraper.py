import csv, time, warnings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

PATH = "chromedriver.exe"

def warn(*args, **kwargs):#ingore deprecation warnings
    pass
warnings.warn = warn

#keyword to search for
KW = input("Please input what you want to search for: ")
#KW= "Houston"

#check if file exists, if not create it
try:
    open(f"{KW}.csv", "r")
except:
    with open(f"{KW}.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["PRICE", "SQ FT", "BEDS", "BATHS", "STREET ADDRESS", "CITY & ZIP", "PHONE"])
        
def writeToCSV(PRICE, BEDS, BATHS, SQ_FT, ADDRESS, ZIP, PHONE):
    with open(f"{KW}.csv", "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([PRICE, SQ_FT, BEDS, BATHS, ADDRESS, ZIP, PHONE])

def getListings(driver):
    time.sleep(2.5)#allow for page to load
    scrollHeight= driver.execute_script("return Math.max(document.body.scrollHeight, document.body.offsetHeight,\
        document.documentElement.scrollHeight, document.documentElement.offsetHeight);")#height/length of page
    scrollIncrement = 1600 
    for scrollCount in range(0,int(scrollHeight/scrollIncrement)):
        driver.execute_script(f"window.scrollTo(0, {scrollIncrement*(scrollCount+1)})")
        time.sleep(1)

    listings = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[class^='HomeCardContainer'][id][data-rf-test-id]")))
    print(f"Total Listings: {len(listings)}")
    driver.execute_script(f"window.scrollTo(0, {0})")#scroll back to top
    time.sleep(0.5)
    return listings
              
def scrapeData(driver):
    basicInfo = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//*[@class='statsValue']")))#block containing the main info
    PRICE = basicInfo[0].text
    BEDS = basicInfo[1].text
    BATHS = basicInfo[2].text
    SQ_FT = basicInfo[3].text
    
    ADDRESS = driver.find_element_by_xpath("//div[contains(@class,'street-address')]").text.replace(",","")
    
    ZIP = driver.find_element_by_xpath("//div[@class='dp-subtext']").text
    try:
        PHONE = driver.find_element_by_xpath("//span[@data-rf-test-name='phone-link']").text
    except:
        PHONE = "N/A"
    
    writeToCSV(PRICE, BEDS, BATHS, SQ_FT, ADDRESS, ZIP, PHONE)
    time.sleep(0.5)
    
def main():
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])#avoid random warnings
    driver = webdriver.Chrome(PATH, options=options)     
    driver.get("https://www.redfin.com/")
    driver.set_window_size(1024, 600)
    driver.maximize_window()
    time.sleep(0.5)
    searchbar = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "search-box-input")))#searchbar
    searchbar.send_keys(KW)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@data-rf-test-name='item-row-active']"))).click() #click top result
    
    listings = getListings(driver)

    for listing in listings:
        try:
            listing.find_element_by_xpath('.//p[contains(text(), "We have rentals too!")]')#avoid clicking on this listing(ad)
            continue
        except:
            pass
        listing.click()
        time.sleep(0.5)
        driver.switch_to.window(driver.window_handles[1])
        scrapeData(driver)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(0.5)    

main()
input("Press Enter To Continue")  

