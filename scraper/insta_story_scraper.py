############################################################################################
#                                  Author: Anas AHOUZI                                     #
#                               File Name: insta_story_scraper.py                          #
#                           Creation Date: January 11, 2021                                #
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
import os, time


################################################################################
#                                  Main Code                                   #
################################################################################

# Asking the client for the username or hashtag he wants to scrap
account = input(colored("\n[INFO]: Please type the username you want to scrap stories from: ", "yellow"))
story_link = "https://www.instagram.com/stories/{}/".format(account)
login_page = "https://www.instagram.com/accounts/login/"
project_direc = os.getcwd()[:-8]

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

# Accept the website cookies
driver.find_element_by_xpath("/html/body/div[4]/div/div/button[1]").click()

# Login with a random account since we can't scrap stories without being logged
driver.find_element_by_name("username").send_keys("testtest7530")
driver.find_element_by_name("password").send_keys("testtest753")
driver.find_element_by_xpath("//*[@id='loginForm']/div/div[3]/button/div").click()
time.sleep(6)
print(colored("\n[SUCCESS]: Logged into the website. \n", "green"))

# Have access to the story link
driver.get(story_link)
time.sleep(2)

# Check if there are any stories for the last 24h, if so start scraping all stories
if driver.current_url != story_link:
    print(colored("\n[ERROR]: No stories are available for the last 24h. \n", "red"))
else:
    rows = []
    print(colored("\n[SUCCESS]: Got into the story link. \n", "green"))
    driver.find_element_by_xpath("/html/body/div[1]/section/div[1]/div/section/div/div[1]/div/div/div/div[3]/button").click()
    time.sleep(3)
    while driver.current_url != "https://www.instagram.com/":
        # Collect the link to the video content of the story if it exists, otherwise take the image link
        is_video = True
        try:
            content_link = driver.find_element_by_xpath("//*[@id='react-root']/section/div[1]/div/section"
                                                        "/div/div[1]/div/div/video/source").get_attribute("src")
        except NoSuchElementException:
            content_link = driver.find_element_by_xpath("//*[@id='react-root']/section/div[1]/div/"
                                                        "section/div/div[1]/div/div/img").get_attribute("src")
            is_video = False

        # Get the link of the story
        insta_link = driver.current_url
        # Get the date of the story
        date = driver.find_element_by_xpath("//*[@id='react-root']/section/div[1]/div/"
                                            "section/div/header/div[2]/div[1]/div/div/"
                                            "div/time").get_attribute("datetime")
        # Append all collected information into a row
        rows.append(
            {
                'Instagram URL': insta_link,
                'Content URL': content_link,
                'Date': date,
                'is_video': is_video
            }
        )
        # Click on the next button
        driver.find_element_by_xpath("//*[@id='react-root']/section/div[1]/div/section/div/button[2]").click()
        time.sleep(3)

    # Save scrapped data into a dataframe
    df = pd.DataFrame(rows)
    df.to_pickle(os.path.join(project_direc, "collected_data/stories_{}.pkl".format(account)))
    print(colored("\n[SUCCESS]: Scrapped all stories for the last 24h. \n", "green"))




