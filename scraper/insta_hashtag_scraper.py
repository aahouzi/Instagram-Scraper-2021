############################################################################################
#                                  Author: Anas AHOUZI                                     #
#                               File Name: insta_hashtag_scraper.py                        #
#                           Creation Date: August 10, 2021                                 #
#                         Source Language: Python                                          #
#           Repository: https://github.com/aahouzi/Instagram-Scraper-2021.git              #
#                              --- Code Description ---                                    #
#          Implementation of an Instagram hashtag scraper based on GraphQL API             #
############################################################################################


################################################################################
#                                   Packages                                   #
################################################################################
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from datetime import datetime
from termcolor import colored
import pandas as pd
import time, json, os

################################################################################
#                                  Main Code                                   #
################################################################################


def process_hashtag_posts(hashtag, driver, posts=" "):
    """
    Extracts useful data starting from a hashtag
    :param hashtag: The hashtag to scrap.
    :param driver: Chrome driver.
    :param posts: URL to scrape.
    :return: A list of dicts.
    """
    # The link where to find data to scrap
    if posts.isspace():
        posts = "https://www.instagram.com/explore/tags/{}/?__a=1".format(hashtag[1:])

    # Make sure that we get into the GraphQL hashtag page
    while True:
        driver.get(posts)
        time.sleep(3)
        try:
            if driver.find_element_by_xpath("/html/body/pre"):
                print(colored("\n[SUCCESS]: Got into the GraphQL hashtag page. \n", "green"))
                break
        except NoSuchElementException:
            pass

        try:
            if driver.find_element_by_name("username"):
                print(colored("\n[INFO]: Failed to access directly, now trying to access from"
                              " the login page to which we were redirected. \n", "yellow"))

                # Connect with an instagram account
                user, mdp = input(colored("\n[INFO]: Please type a username and its password seperated by one space"
                                          " for login: ", "yellow")).split()
                driver.find_element_by_name("username").send_keys(user)
                driver.find_element_by_name("password").send_keys(mdp)
                driver.find_element_by_xpath("//*[@id='loginForm']/div/div[3]/button/div").click()
                time.sleep(10)
                print(colored("\n[SUCCESS]: Logged into the website. \n", "green"))

                # Retry accessing the GraphQL hashtag page
                while True:
                    driver.get(posts)
                    time.sleep(3)
                    try:
                        if driver.find_element_by_xpath("/html/body/pre"):
                            print(colored("\n[SUCCESS]: Got into the hashtag page. \n", "green"))
                            break
                    except NoSuchElementException:
                        pass

                break
        except NoSuchElementException:
            pass

    # Load json data into a python dict
    data = json.loads(driver.find_element_by_xpath("/html/body/pre").text)

    # Print the total number of posts
    if posts == "https://www.instagram.com/explore/tags/{}/?__a=1".format(hashtag[1:]):
        num_post = data['graphql']['hashtag']['edge_hashtag_to_media']['count']
        print(colored("\n[INFO]: Number of Instagram posts: {}. \n".format(num_post), "yellow"))

    # Here, we extract useful infos about the hashtag
    rows = []
    has_next_page = data['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['has_next_page']
    max_id = data['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']
    all_edges = data['graphql']['hashtag']['edge_hashtag_to_media']['edges']
    for i in all_edges:
        # Get various informations about the post
        url_insta = 'https://www.instagram.com/p/' + i['node']['shortcode']
        date_val = datetime.fromtimestamp(i['node']['taken_at_timestamp']).strftime("%d/%m/%Y %H:%M:%S")
        num_comments = i['node']['edge_media_to_comment']['count']
        num_like = i['node']['edge_media_preview_like']['count']

        # Get the image URL, and number of views if it's a video
        feed_url = i['node']['display_url']
        is_video = i['node']['is_video']
        if is_video:
            num_views = i['node']['video_view_count']
        else:
            num_views = 0

        # Get the publication description
        caption = ""
        if i['node']['edge_media_to_caption']:
            for k in i['node']['edge_media_to_caption']['edges']:
                caption += k['node']['text']

        # Append all collected information into a row
        rows.append(
            {
                'Instagram URL': url_insta,
                'Date': date_val,
                'Description': caption,
                'Video': is_video,
                'Number of comments': num_comments,
                'Number of likes': num_like,
                'Number of views': num_views,
                'Content URL': feed_url,
            }
        )

    print(colored("\n[SUCCESS]: Scrapped {} posts. \n".format(len(rows)), "green"))

    if has_next_page:
        posts = "https://www.instagram.com/explore/tags/{}/?__a=1&max_id={}".format(hashtag[1:], max_id)
        return rows + process_hashtag_posts(hashtag, driver, posts=posts)
    else:
        return rows


# Ask the user to type the #hashtag he wants to scrap from
account = input(colored("\n[INFO]: Please enter the #hashtag you want to scrap from: ", "yellow"))
main_url = "https://www.instagram.com/explore/tags/{}/".format(account[1:])
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
print(colored("\n[INFO]: Start scraping the hashtag link .. \n", "yellow"))

# Make sure that we get into the welcome page
start_scrap = time.time()
L = process_hashtag_posts(account, driver)
duration_scrap = round(time.time()-start_scrap, 2)
print(colored("\n[SUCCESS]: Finished scrapping {} posts, it took {}s. \n".format(len(L), duration_scrap), "green"))

# Save scrapped data into a dataframe
df = pd.DataFrame(L)
df.to_pickle(os.path.join(project_direc, "collected_data/hashtag_{}.pkl".format(account)))









