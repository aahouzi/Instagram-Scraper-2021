############################################################################################
#                                  Author: Anas AHOUZI                                     #
#                               File Name: story_scraper.py                                #
#                           Creation Date: January 11, 2020                                #
#                         Source Language: Python                                          #
#           Repository: https://github.com/aahouzi/Instagram-Scraper-2021.git              #
#                              --- Code Description ---                                    #
#                     Implementation of an Instagram story scraper                         #
############################################################################################


################################################################################
#                                   Packages                                   #
################################################################################
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
import pandas as pd
from termcolor import colored
import time


################################################################################
#                                  Main Code                                   #
################################################################################

# Asking the client for the username or hashtag he wants to scrap
account = input(colored("\n[INFO]: Please enter the username or hashtag you want to scrap stories from: ", "yellow"))
story_link = "https://www.instagram.com/stories/{}/".format(account)
login_page = "https://www.instagram.com/accounts/login/"

# Specify Chrome driver options
options = webdriver.ChromeOptions()
options.add_argument("--window-size=1920,1080")
options.add_argument('--ignore-certificate-errors')
options.add_argument('--allow-running-insecure-content')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
options.add_argument('--headless')

driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
driver.get(login_page)
time.sleep(4)

# Accept cookies & take a screenshot of the welcome page
cookies = driver.find_element_by_xpath("/html/body/div[2]/div/div/div/div[2]/button[1]").click()
driver.get_screenshot_as_file("welcome_page.png")

# Connect with an instagram account since we can't scrap stories without being logged
username = driver.find_element_by_name("username")
password = driver.find_element_by_name("password")
username.send_keys("testtest7530")
password.send_keys("testtest753")
driver.find_element_by_xpath("//*[@id='loginForm']/div/div[3]/button/div").click()
time.sleep(6)

print(colored("\n[SUCCESS]: Logged into the website. \n", "green"))

# Have access to the story link
driver.get(story_link)
time.sleep(3)
print(colored("\n[SUCCESS]: Got into the story link. \n", "green"))

# Click on the start button to see all stories
start = driver.find_element_by_xpath("//*[@id='react-root']/section/div[1]/div/section/div/div[1]/div/div/button").click()
rows = []
while driver.current_url != "https://www.instagram.com/":
    # Collect the link to the video content of the story if it exists, otherwise take the image link
    try:
        content_link = driver.find_element_by_xpath("//*[@id='react-root']/section/div[1]/div/section"
                                                    "/div/div[1]/div/div/video/source").get_attribute("src")
    except NoSuchElementException:
        print(colored("\n[INFO]: Didn't find the video link, we get the image. \n", "yellow"))
        content_link = driver.find_element_by_xpath("//*[@id='react-root']/section/div[1]/div/"
                                                    "section/div/div[1]/div/div/img").get_attribute("src")

    print(content_link)
    # Get the instagram link of the story
    insta_link = driver.current_url
    # Get the date at which the story was published
    date = driver.find_element_by_xpath("//*[@id='react-root']/section/div[1]/div/"
                                        "section/div/header/div[2]/div[1]/div/div/div/time").get_attribute("datetime")
    # Append all collected information into a row
    rows.append(
        {
            'Instagram URL': insta_link,
            'Content URL': content_link,
            'Date': date
        }
    )
    time.sleep(2)
    # Click on the next button
    driver.find_element_by_xpath("//*[@id='react-root']/section/div[1]/div/section/div/button[2]").click()

df = pd.DataFrame(rows)
df.to_pickle("collected_data/stories.pkl")
print(colored("\n[SUCCESS]: Scrapped all stories for the last 24h. \n", "green"))




