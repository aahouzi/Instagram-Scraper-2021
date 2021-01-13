# Scrap Instagram content & stories | 2021 version.
Enseirb-Matmeca, Bordeaux INP | [Anas AHOUZI](https://www.linkedin.com/in/anas-ahouzi-6aab0b155/)
***

## :monocle_face: Description
- This project enables the user to scrap all content and feed of a public instagram account, as well as the stories anonymously given the username
 or hashtag of the account.</br>

- In 2021, Instagram made it even more difficult to scrap data from its graphql API. Even though there are many open-source projects that enables you to
 scrap content from Instagram, many of those projects don't work anymore or work partially, and get you only a small portion of the data you need.
 
- In this project, I used a **new technique** based on **the har file**. This file contains all the GET requests sent by Instagram to its graphql API,
and by getting access to this file we can capture all the precious json files containing all the data we need to scrape.


## :rocket: Repository Structure
The repository contains the following files & directories:
- **scraper/insta_feed_scrapper.py:** The code used for scraping content from a user/hashtag public page.
- **scraper/story_scrapper.py:** Code for scrapping stories from a user public page.
- **collected_data:** It contains the collected feed & stories in pkl format (The data collected in the demo).
- **data_analysis.ipynb:** It contains some data analysis for the scraped **nike page** feed.

## :scroll: Scraping process

- Before executing the code, the user needs to get **browsermob-proxy-2.1.4** from [here](https://bmp.lightbody.net/) and put it in the project directory
. This proxy will help us get access to the har file during the execution with Selenium.

- **Scraping stories** is an easy task, since we don't need to analyze graphql responses or get the har file, we only access to Instagram and get every story using
their XPath with selenium.

- **For scraping content**, the user is asked to enter the username or hashtag he wants to scrap, then the program gets access
to the username page. However, sometimes Instagram blocks the direct access to public pages, and asks the user to log in. In this case, the program types
some random user account that was created for scraping purposes. After getting access to the page we want to scrape, **Selenium** executes a Javascript
code that enables to keep scrolling down until all the content is loaded. After this step, we analyze the resulting har file in order to extract all
graphql responses, in a json format. Finally, we loop through every response to get all the informations we need. Here's a small demo of scraping
 **nike** page feed:
 

![](https://j.gifs.com/k8YDNX.gif)




---
## :mailbox_closed: Contact
For any information, feedback or questions, please [contact me][anas-email]










[anas-email]: mailto:ahouzi2000@hotmail.fr