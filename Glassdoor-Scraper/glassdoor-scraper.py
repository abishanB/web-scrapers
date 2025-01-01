import csv, math, time, warnings
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

print("Glassdoor Review Scraper")
print("------------------------------------------")
PATH = "chromedriver.exe"

def warn(*args, **kwargs):#ingore deprecation warnings
    pass
warnings.warn = warn

try:
    open(f"data.csv", "r")
except:
    with open(f"data.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Page","Review", "Overall Rating",
        "Work/Balance Rating", "Culture Rating", "Diversity Rating", "Career Opportunities Rating", "Benifits Rating", "Management Rating",
        "Employment Status", "Title", "Date & Role", "Recommend To Friend", "CEO Approval", "Business Outlook", "Pros", "Cons"])

def writeToCSV(PAGE, REVIEWNUM,RATING,
             WORK_RATING, CULTURE_RATING, DIVERSITY_RATING, OPPORTUNITIES_RATING, BENIFITS_RATING, MANAGEMENT_RATING,
              EMPLOYMENT_STATUS, TITLE, DATE_ROLE, RECCOMMEND, APPROVAL, BUSINESS_OUTLOOK, PROS, CONS):

    try:
        with open(f"data.csv", "a", newline='') as f:
            writer = csv.writer(f)
            writer.writerow([PAGE, REVIEWNUM, RATING,
                WORK_RATING, CULTURE_RATING, DIVERSITY_RATING, OPPORTUNITIES_RATING, BENIFITS_RATING, MANAGEMENT_RATING,
                EMPLOYMENT_STATUS, TITLE, DATE_ROLE, RECCOMMEND, APPROVAL, BUSINESS_OUTLOOK, PROS, CONS])
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass

def scrapeRecommends(recommend):#reccomend, ceo approval, buissness outlook
    if recommend.find_element_by_xpath('.//span/*/*').tag_name == "circle":#tag name corresponds to icon 
        return "Neutral"
    if recommend.find_element_by_xpath('.//span/*/*').tag_name == "rect":
        return "Orange"
    if recommend.find_element_by_xpath('.//span/*/*').tag_name == "path":
        if recommend.find_element_by_xpath('.//span/*/*').get_attribute("d")=="M8.835 17.64l-3.959-3.545a1.19 1.19 0 010-1.735 1.326 1.326 0 011.816 0l3.058 2.677 7.558-8.678a1.326 1.326 0 011.816 0 1.19 1.19 0 010 1.736l-8.474 9.546c-.501.479-1.314.479-1.815 0z":
            #checkmark
            return "Check"
        else:
            #red X
            return "X"

def scrapeRatings(driver, review):#worklife, culture, career, benifits and management ratings
    dropdown = review.find_element_by_xpath(".//div/div/div/div/div/div/span[2]")
    hover = ActionChains(driver).move_to_element(dropdown)#hover dropdown
    hover.perform()
    
    otherRatings = review.find_elements_by_xpath(".//aside/div/div/ul/li/div[@class]")

    #each element has a unique class name corresponding to the star rating
    ratingEncodeDict = {"css-s88v13 e1hd5jg10" : 5,
                        "css-1nuumx7 e1hd5jg10" : 4,
                        "css-vl2edp e1hd5jg10" : 3,
                        "css-18v8tui e1hd5jg10" : 2,
                        "css-xd4dom e1hd5jg10" : 1}
    workLife_balance = "N/A"
    culture_values = "N/A"
    diversity_inclusion = "N/A"
    career_opportunities = "N/A"
    benifits="N/A"
    management="N/A"

    try:
        workLife_balance = ratingEncodeDict[otherRatings[0].get_attribute("class")]
        culture_values = ratingEncodeDict[otherRatings[1].get_attribute("class")]
        diversity_inclusion = ratingEncodeDict[otherRatings[2].get_attribute("class")]
        career_opportunities = ratingEncodeDict[otherRatings[3].get_attribute("class")]
        benifits = ratingEncodeDict[otherRatings[4].get_attribute("class")]
        management = ratingEncodeDict[otherRatings[5].get_attribute("class")]   
    except (IndexError, KeyError):#some dropdowns have less than 6 ratings
        pass
    return workLife_balance, culture_values, diversity_inclusion, career_opportunities, benifits, management

def scrape(driver, page):
    reviews = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//li[@id][@data-brandviews]")))
    
    for review in reviews:
        try:
            driver.execute_script("arguments[0].scrollIntoView();", review)
            scrollPos = driver.execute_script('return window.pageYOffset;')
            driver.execute_script(f"window.scrollTo(0, {scrollPos-100});")#scroll up so dropdown is visible
            time.sleep(0.6)

            try: #click continue reading to expand review
                review.find_element_by_xpath("//div[contains(text(), 'Continue reading')]").click()
            except: pass#some reviews dont have continue reading
            time.sleep(0.6)

            driver.execute_script("arguments[0].scrollIntoView();", review)
            scrollPos = driver.execute_script('return window.pageYOffset;')
            driver.execute_script(f"window.scrollTo(0, {scrollPos-100});")#scroll up again because clicking continue reading changes scroll pos
            time.sleep(0.6)

            try:
                date_role = review.find_element_by_xpath('.//span[contains(@class,"authorJobTitle")]').text
            except:
                date_role = "N/A"

            overall_rating = review.find_element_by_xpath('.//span[contains(@class,"ratingNumber")]').text
            employment_status = review.find_element_by_xpath("//li[@id][@data-brandviews]/div/div/div/div/span").text
            title = review.find_element_by_xpath('.//a[@class="reviewLink"]').text
            pros = review.find_element_by_xpath('.//span[@data-test="pros"]').text
            cons = review.find_element_by_xpath('.//span[@data-test="cons"]').text

            recommends = review.find_elements_by_xpath('.//div[contains(@class,"reviewBodyCell ")]/div')#3 recommend stats
            recommend= scrapeRecommends(recommends[0])
            ceo_approval = scrapeRecommends(recommends[1])
            business_outlook = scrapeRecommends(recommends[2])

            work_balance_rating, culture_rating, diversity_rating, career_rating, benifits_rating, management_rating = scrapeRatings(driver, review)
            
            writeToCSV(page, reviews.index(review), overall_rating,
            work_balance_rating, culture_rating, diversity_rating, career_rating, benifits_rating, management_rating,
            employment_status, title, date_role,recommend,ceo_approval, business_outlook, pros, cons)
        except:
            
            writeToCSV("N/A","N/A","N/A","N/A","N/A",
            "N/A","N/A","N/A","N/A","N/A",
            "N/A","N/A","N/A","N/A","N/A")

def login(driver):#login to glassdoor
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@name='username']"))).send_keys(EMAIL)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@name='password']"))).send_keys(PASSWORD)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@name='password']"))).send_keys(Keys.RETURN)

def main(URL):
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])#avoid random warnings
    driver = webdriver.Chrome(PATH, options=options)    
    driver.get(URL) 
    driver.set_window_size(1024, 600)
    driver.maximize_window()
    
    time.sleep(0.5)
    TOTALREVIEWS = int(driver.find_element_by_xpath('//div[@class="paginationFooter"]').text.split()[-2].replace(",",""))#total reviews
    PAGES = math.ceil(TOTALREVIEWS/10)#10 reviews per page, round up to next number
    print(f"Total Reviews: {TOTALREVIEWS}")
    print(f"Pages: {PAGES}")
    
    driver.find_element_by_xpath("//div[contains(text(), 'Continue reading')]").click()#clicking continue reading brings up login
    time.sleep(1)
    login(driver)
    time.sleep(5)
    
    for page in range(PAGES):#go through each page
        if page != 0:#dont click on first page(landing page)
            driver.find_element_by_xpath(f'//a[contains(@data-test,"pagination-link")][contains(text(), "{page+1}")]').click()
            time.sleep(5)
        scrape(driver, page+1)


    input("\nFinished. Press Enter To Exit")

with open("account.txt", "r") as f:
    EMAIL, PASSWORD = f.read().split(":")

url = input("Enter url to reviews page: ")

main(url)
