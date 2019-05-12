from splinter import Browser
from bs4 import BeautifulSoup
import time
import pandas as pd
import requests


def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    exec_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **exec_path, headless=False)


def scrape():

    # ----Mars News---

    # start browser
    browser = init_browser()

    # set and visit url
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)

    time.sleep(1)

    # Scrape page into Soup
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")

    mars_news = {}
    # Collect Nasa latest News Title with corresponding Paragraph Text
    mars_news["news_titles"] = soup.find(
        "div", class_="content_title"
    ).next_element.get_text()
    mars_news["news_p"] = soup.find("div", class_="article_teaser_body").get_text()

    # print("mars_news" + str(mars_news))

    # # ----JPL Mars Space Images - Featured Image--

    # set and visit url
    url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url)

    time.sleep(1)

    # Scrape page into Soup
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")

    # find the image url for the current Featured Mars Image and assign the url string to a variable called
    # featured_image_url
    relative_image_path = (
        soup.find("article")["style"]
        .replace("background-image: url(", "")
        .replace(");", "")[1:-1]
    )
    featured_img_url = "https://www.jpl.nasa.gov" + relative_image_path

    # # -----Mars Weather-------------------------------------
    # set and visit url
    url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(url)

    time.sleep(1)

    # Scrape page into Soup
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")

    # Scrape the latest Mars weather tweet from the page

    results = soup.find("div", class_="js-tweet-text-container")

    latest_tweet = results.find(
        "p", class_="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text"
    )

    [s.extract() for s in latest_tweet("a")]

    tweet_weather = latest_tweet.text

    #  -----Mars FACTS----
    # set and visit url
    url = "https://space-facts.com/mars/"

    tables = pd.read_html(url)

    df = tables[0]
    df.columns = ["Description", "Values"]

    df.set_index("Description", inplace=True)

    html_table = df.to_html()

    # -----Mars Hemispheres----
    # set and visit url
    url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(url)

    time.sleep(1)

    # Scrape page into Soup
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")

    # Collect Website 1 urls
    items = soup.find_all("div", class_="item")

    hemi_imgs = []

    # astropedia_url = "https://astrogeology.usgs.gov"

    for item in items:
        try:
            title = item.find("div", class_="description")
            hemi_title = title.a.text

            browser.click_link_by_partial_text(hemi_title)
            html2 = browser.html
            soup_2 = BeautifulSoup(html2, "html.parser")

            hemi_link = soup_2.find("div", class_="downloads").find("li").a["href"]
            hemi_title = soup_2.find("h2", class_="title").text

            # Store data in a dictionary
            data = {"img_url": hemi_link, "title": hemi_title}

            hemi_imgs.append(data)

            browser.visit(url)

        except AttributeError as e:
            print("Error:", e)
    print(hemi_imgs)

    browser.quit()

    # ------Dictionary to be imported to Mongo and website------
    scrape_data = {
        "news": mars_news,
        "featured_img": featured_img_url,
        "mars_weather": tweet_weather,
        "mars_table": html_table,
        "hemi_imgs": hemi_imgs
    }
    return scrape_data
