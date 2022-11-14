from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
import time

import pandas as pd


def ScrapComment(url):
    option = webdriver.FirefoxOptions()
    option.add_argument("--headless")
    driver = webdriver.Firefox(service=Service(executable_path=GeckoDriverManager().install()), options=option)
    driver.get(url)
    prev_h = 0
    while True:
        height = driver.execute_script("""
                function getActualHeight() {
                    return Math.max(
                        Math.max(document.body.scrollHeight, document.documentElement.scrollHeight),
                        Math.max(document.body.offsetHeight, document.documentElement.offsetHeight),
                        Math.max(document.body.clientHeight, document.documentElement.clientHeight)
                    );
                }
                return getActualHeight();
            """)
        driver.execute_script(f"window.scrollTo({prev_h},{prev_h + 100})")
        # fix the time sleep value according to your network connection
        time.sleep(1)
        prev_h += 200
        if prev_h >= height:
            break
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    title_text_div = soup.select_one('#container h1')
    title = title_text_div and title_text_div.text
    print(title)
    for div in soup.findAll('div', attrs={'class': 'style-scope ytd-channel-name'}):
        for link in div.findAll('a'):
            owner= link.string

    comment_div = soup.select("#content #content-text")
    comment_list = [x.text for x in comment_div]
    # print(title, comment_list)
    df = pd.DataFrame(comment_list)
    all_comments=df.to_csv('output.csv',index=False)
    return all_comments,title,owner



