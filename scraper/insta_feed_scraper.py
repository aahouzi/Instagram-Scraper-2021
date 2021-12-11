############################################################################################
#                                  Author: Anas AHOUZI                                     #
#                               File Name: insta_feed_scraper.py                           #
#                           Creation Date: January 11, 2021                                #
#                         Source Language: Python                                          #
#           Repository: https://github.com/aahouzi/Instagram-Scraper-2021.git              #
#                              --- Code Description ---                                    #
#          Implementation of an Instagram content scraper using the har file               #
############################################################################################


################################################################################
#                                   Packages                                   #
################################################################################
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from browsermobproxy import Server
from selenium import webdriver
from datetime import datetime
from termcolor import colored
import pandas as pd
import time, json, os


################################################################################
#                                  Main Code                                   #
################################################################################
def scroll_down(driver, sec=1, timeout=60):
    """
    This function enables Chrome driver to keep scrolling down until all the content
    is loaded.
    :param driver: Chrome driver.
    :param sec: Time to wait between two scrolls (depends on ur internet connection).
    :param timeout: Timeout for which we stop scrolling.
    :return:
    """
    # Get scroll height.
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to the bottom.
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load the page.
        duree = 0
        while last_height == driver.execute_script("return document.body.scrollHeight"):
            time.sleep(sec)
            duree += sec
            if duree >= timeout:
                break

        # Calculate new scroll height and compare with last scroll height.
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            break

        last_height = new_height


def process_first_posts(account, driver):
    """
    Extracts user data from the 12 first posts, since their json structure is
    different from the rest of graphql responses.
    :param account: The username or hashtag.
    :param driver: Chrome driver.
    :return: A list of dicts.
    """
    # The link where to find data about 12 first posts
    posts = "https://www.instagram.com/{}/?__a=1".format(account)

    # Get access to the link
    driver.get(posts)
    time.sleep(3)

    data = json.loads(driver.find_element_by_xpath("/html/body/pre").text)

    # Print the total number of posts
    num_post = data['graphql']['user']['edge_owner_to_timeline_media']['count']
    print(colored("\n[INFO]: Number of Instagram posts: {}. \n".format(num_post), "yellow"))

    # Here, we process publications or feeds content
    sample = []
    all_edges = data['graphql']['user']['edge_owner_to_timeline_media']['edges']
    for i in all_edges:
        # Get various informations about the post
        url_insta = 'https://www.instagram.com/p/' + i['node']['shortcode']
        date_val = datetime.fromtimestamp(i['node']['taken_at_timestamp']).strftime("%d/%m/%Y %H:%M:%S")
        num_comments = i['node']['edge_media_to_comment']['count']
        num_like = i['node']['edge_media_preview_like']['count']

        # First, we check the case where we might have many images/videos content in the same publication
        feed_url = {}
        video_is = {}
        views_num = {}
        if 'edge_sidecar_to_children' in i['node']:
            many_content = 1
            # Loop through all images/videos of the publication
            for t in i['node']['edge_sidecar_to_children']['edges']:
                if t['node']['is_video']:
                    feed_url[t['node']['id']] = t['node']['video_url']
                    views_num[t['node']['id']] = t['node']['video_view_count']
                else:
                    feed_url[t['node']['id']] = t['node']['display_url']
                    views_num[t['node']['id']] = 0

                video_is[t['node']['id']] = t['node']['is_video']

        else:
            many_content = 0
            video_is[i['node']['id']] = i['node']['is_video']
            if video_is[i['node']['id']]:
                feed_url[i['node']['id']] = i['node']['video_url']
                views_num[i['node']['id']] = i['node']['video_view_count']
            else:
                feed_url[i['node']['id']] = i['node']['display_url']
                views_num[i['node']['id']] = 0

        # Get the publication description
        caption = ""
        if i['node']['edge_media_to_caption']:
            for k in i['node']['edge_media_to_caption']['edges']:
                caption += k['node']['text']

        # Append all collected information into a row
        sample.append(
            {
                'Instagram URL': url_insta,
                'Date': date_val,
                'Multi content': many_content,
                'Description': caption,
                'Video': video_is,
                'Number of comments': num_comments,
                'Number of likes': num_like,
                'Number of views': views_num,
                'Content URL': feed_url,
            }
        )

    print(colored("\n[SUCCESS]: Scrapped {} first posts. \n".format(len(sample)), "green"))
    return sample


def process_graphql_response(url, driver):
    """
    Extracts user data from graphql responses.
    :param url: The url of a graphql response.
    :param driver: Chrome driver.
    :return: A list of dicts.
    """
    while True:
        driver.get(url)
        time.sleep(2)
        driver.get_screenshot_as_file("json.png")
        try:
            data = json.loads(driver.find_element_by_xpath("/html/body/pre").text)
            break
        except NoSuchElementException:
            print(colored("\n[INFO]: Failed extracting a graphQl response, now trying to access from "
                          "the login page to which we were redirected. \n", "yellow"))

            # Connect with an instagram account
            user, mdp = input(colored("\n[INFO]: In order to carry on scraping, type a username"
                                      " and its password seperated by one space: ", "yellow")).split()
            driver.find_element_by_name("username").send_keys(user)
            driver.find_element_by_name("password").send_keys(mdp)
            driver.find_element_by_xpath("//*[@id='loginForm']/div/div[3]/button/div").click()
            time.sleep(4)
            print(colored("\n[INFO]: Logged into the website. \n", "yellow"))

    rows = []
    # Handling the case of the first graphql response, that doesn't contain any info
    if 'viewer' in data['data']:
        return rows

    # Here, we process publications or feeds content
    edges = data['data']['user']['edge_owner_to_timeline_media']['edges']
    for edge in edges:
        # Get various informations about the post
        insta_url = 'https://www.instagram.com/p/' + edge['node']['shortcode']
        date = datetime.fromtimestamp(edge['node']['taken_at_timestamp']).strftime("%d/%m/%Y %H:%M:%S")
        num_comm = edge['node']['edge_media_to_comment']['count']
        num_likes = edge['node']['edge_media_preview_like']['count']

        # First, we check the case where we might have many images/videos content in the same publication
        content_url = {}
        is_video = {}
        num_views = {}
        if 'edge_sidecar_to_children' in edge['node']:
            multi_content = 1
            # Loop through all images/videos of the publication
            for t in edge['node']['edge_sidecar_to_children']['edges']:
                if t['node']['is_video']:
                    content_url[t['node']['id']] = t['node']['video_url']
                    num_views[t['node']['id']] = t['node']['video_view_count']
                else:
                    content_url[t['node']['id']] = t['node']['display_url']
                    num_views[t['node']['id']] = 0

                is_video[t['node']['id']] = t['node']['is_video']

        else:
            multi_content = 0
            is_video[edge['node']['id']] = edge['node']['is_video']
            if is_video[edge['node']['id']]:
                content_url[edge['node']['id']] = edge['node']['video_url']
                num_views[edge['node']['id']] = edge['node']['video_view_count']
            else:
                content_url[edge['node']['id']] = edge['node']['display_url']
                num_views[edge['node']['id']] = 0

        # Get the publication description
        description = ""
        if edge['node']['edge_media_to_caption']:
            for k in edge['node']['edge_media_to_caption']['edges']:
                description += k['node']['text']

        # Append all collected information into a row
        rows.append(
            {
                'Instagram URL': insta_url,
                'Date': date,
                'Multi content': multi_content,
                'Description': description,
                'Video': is_video,
                'Number of comments': num_comm,
                'Number of likes': num_likes,
                'Number of views': num_views,
                'Content URL': content_url,
            }
        )

    print(colored("\n[SUCCESS]: Scrapped {} posts.".format(len(rows)), "green"))

    return rows


# Asking the client for the username or hashtag he wants to scrap
account = input(colored("\n[INFO]: Please enter the username you want to scrap from: ", "yellow"))
login_url = "https://www.instagram.com/accounts/login/"
main_url = "https://www.instagram.com/{}/".format(account)
project_direc = os.getcwd()[:-8]

# Configure the browsermob-proxy settings

# Here, specify the full path to ur browsermob proxy
proxy_path = os.path.join(project_direc, "browsermob-proxy-2.1.4/bin/browsermob-proxy")
server = Server(proxy_path, options={"port": 8000})
server.start()
proxy = server.create_proxy()

# Specify Chrome driver options
options = webdriver.ChromeOptions()
options.add_argument("--proxy-server={}".format(proxy.proxy))
options.add_argument("--window-size=1920,1080")
options.add_argument('--ignore-certificate-errors')
options.add_argument('--allow-running-insecure-content')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
options.add_argument('--headless')
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

failure = 0
while True:
    try:
        if not failure:
            print(colored("\n[INFO]: Getting access to the user website .. \n", "yellow"))

            # Make sure that we got into the welcome page
            while True:
                driver.get(login_url)
                time.sleep(3)
                try:
                    if driver.find_element_by_name("username"):
                        raise Exception("Instagram redirected us to a login page")
                except NoSuchElementException:
                    pass

        elif failure == 200:
            print(colored("\n[INFO]: Failed to access directly, now trying to access from"
                          " the login page to which we were redirected. \n", "yellow"))

            # Accept website cookies
            try:
                driver.find_element_by_xpath("/html/body/div[4]/div/div/button[1]").click()
            except NoSuchElementException:
                pass

            # Connect with an instagram account
            user, mdp = input(colored("\n[INFO]: Please type a username and its password seperated by one space"
                                      " for login: ", "yellow")).split()
            driver.find_element_by_name("username").send_keys(user)
            driver.find_element_by_name("password").send_keys(mdp)
            driver.find_element_by_xpath("//*[@id='loginForm']/div/div[3]/button/div").click()
            time.sleep(10)
            print(colored("\n[SUCCESS]: Logged into the website. \n", "green"))

            # Make sure that we get into the welcome page
            while True:
                driver.get(main_url)
                time.sleep(3)
                try:
                    if driver.find_element_by_xpath("/html/body/div[1]/div/div/section/main/div/header/section/div[1]/h2"):
                        print(colored("\n[SUCCESS]: Got into the user page. \n", "green"))
                        break
                except NoSuchElementException:
                    pass

            # Take a screenshot of the welcome page
            driver.get_screenshot_as_file("welcome_page.png")

        # Scroll to the bottom of the page to get all the content
        print(colored("\n[INFO]: Start scrolling to the bottom of the page to get all the content. \n", "yellow"))
        proxy.new_har("new_har", options={'captureHeaders': False})

        # There are some instagram pages that don't load content as u scroll, and u need first to click on a button
        # to start loading content
        time.sleep(4)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        start_scroll = time.time()
        try:
            driver.find_element_by_xpath("/html/body/div[1]/section/main/div/div[3]/div[1]/div/button").click()
            scroll_down(driver)
        except NoSuchElementException:
            scroll_down(driver)

        duration_scroll = round(time.time()-start_scroll, 2)
        print(colored("\n[SUCCESS]: Finished scrolling, it took {}s. \n".format(duration_scroll), "green"))

        # Get all the links for graphql responses from the har file
        entries = proxy.har["log"]["entries"]
        graphql_url = []
        for d in entries:
            if len(d["request"]["queryString"]) != 0 and d["request"]["queryString"][0]["name"] == "query_hash":
                graphql_url.append(d["request"]["url"])

        print(colored("\n[INFO]: {} graphql responses were extracted. \n".format(len(graphql_url)), "yellow"))

        # Process the first 12 posts independantly, since their json structure is different from graphql responses
        rows = process_first_posts(account, driver)

        # Extract all the precious json files containing all the data we need from graphql responses
        start_scrap = time.time()
        for url in graphql_url:
            rows += process_graphql_response(url, driver)

        duration_scrap = round(time.time()-start_scrap, 2)
        print(colored("\n[SUCCESS]: Finished scrapping {} posts, it took {}s. \n".format(len(rows), duration_scrap), "green"))
        df = pd.DataFrame(rows)
        df.to_pickle(os.path.join(project_direc, "collected_data/feed_{}.pkl".format(account)))
        break

    except Exception as e:
        print(colored("\n[ERROR]: {}\n".format(e), "red"))
        if e.args[0] == 'Instagram redirected us to a login page':
            failure = 200
        else:
            break





