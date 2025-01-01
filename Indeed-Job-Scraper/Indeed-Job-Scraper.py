import csv
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common import keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

PATH = "chromedriver.exe"
#driver.find_element_by_css_selector("svg[class^='svg-circle-plus']").click()s
def warn(*args, **kwargs):#ingore deprecation warnings
    pass
import warnings

warnings.warn = warn

        
def writeToCSV(JOB, COMPANY, RATING, LOCATION, PAY, URL, DESCRIPTION, KEYWORD):
    with open(f"{KEYWORD}.csv", "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([JOB, COMPANY, RATING, LOCATION, PAY, DESCRIPTION, URL])

def search(driver, KEYWORD, city):#HomeCardContainer selectedHomeCard
    searchbar = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "text-input-what"))) 
    searchbar.send_keys(KEYWORD)
    
    citySearch = driver.find_element_by_id("text-input-where")
    citySearch.send_keys(Keys.CONTROL, 'a')
    citySearch.send_keys(Keys.DELETE)
    citySearch.send_keys(city)
    
    searchbar.send_keys(Keys.RETURN)
    time.sleep(3)
    try:
        WebDriverWait(driver, 2).until(EC.presence_of_all_elements_located((By.XPATH, "//button[@class='popover-x-button-close icl-CloseButton']"))).click()
    except:
        pass
    
    #pages
    pages = len(WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, "//ul[@class='pagination-list']/li"))))
    print(f"Total Pages: {pages-1}")
    for page in range(pages-1):
        if page != 0:#dont do anything on first page
            
            next_page = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, f"//ul[@class='pagination-list']/li[{page+1}]")))
            driver.execute_script("arguments[0].scrollIntoView();", next_page)
            next_page.click()
            time.sleep(0.5)
            
            try:#close popup
                WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Close']"))).click()
                time.sleep(0.5)
            except:
                pass
            
        listings = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//a[@data-hiring-event]")))
        print(len(listings))
        for listing in listings:
            driver.execute_script("arguments[0].scrollIntoView();", listing)
            listing.click()
            time.sleep(0.25)
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="jobsearch-JobComponent-embeddedHeader"]')))
            scrapeData(driver, listing, KEYWORD)
            time.sleep(0.5)
            
def scrapeData(driver, job_listing, KEYWORD):#//*[@class="statsValue"]
    job_details = driver.find_element_by_xpath('//div[@class="jobsearch-JobComponent-embeddedHeader"]')
    try:
        job_url = job_listing.get_attribute("href")
    except:
        job_url = "N/A"
    
    try:
        job_name = job_listing.find_element_by_xpath(".//span[@title]").get_attribute("title")
    except:
        job_name = "N/A"
    
    try:
        company_Name = job_details.find_element_by_xpath('.//a[@href]').text
    except:
        pass
        
    try:
        rating = job_listing.find_element_by_xpath(".//span[@class='ratingNumber']/span").text
    except:
        rating= "N/A"
        
    try:
        location = job_listing.find_element_by_xpath(".//div[@class='companyLocation']").text
    except:
        location = "N/A"
        
    try:
        desc = job_listing.find_element_by_xpath(".//li").text
    except:
        desc = "N/A"
        
    try:
        pay = job_listing.find_element_by_xpath(".//span[@class='salary-snippet']").text
    except:
        pay = "N/A"
    
    writeToCSV(job_name, company_Name, rating, location, pay, job_url, desc, KEYWORD)

def main():
    #KW = input("Enter a keyword to search for\n")
    #SEARCH_CITY = input("Enter a city/area to search in\n")
    KW = "Accountant"
    SEARCH_CITY = "Toronto"
    #check if file exists, if not create it
    try:
        open(f"{KW}.csv", "r")
    except:
        with open(f"{KW}.csv", "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["JOB", "COMPANY", "RATING", "LOCATION", "PAY", "DESCRIPTION", "JOB URL"])
            
    options_chrome = Options()
    driver = webdriver.Chrome(PATH, options=options_chrome)     
    driver.get("https://indeed.com/")
    driver.set_window_size(1024, 600)
    driver.maximize_window()
    time.sleep(0.5)
    search(driver, KW, SEARCH_CITY)
    driver.quit()

    

                
       
main()
input("done")  
