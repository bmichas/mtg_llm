import time
from io import StringIO
import pickle
import os

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from tqdm import tqdm

from selenium.webdriver.firefox.options import Options as FirefoxOptions


def main():
    root = "https://edhrec.com"
    # urls = ["https://edhrec.com/commanders/mono-white",
    #         "https://edhrec.com/commanders/mono-blue",
    #         "https://edhrec.com/commanders/mono-black",
    #         "https://edhrec.com/commanders/mono-red",
    #         "https://edhrec.com/commanders/mono-green",
    #         "https://edhrec.com/commanders/colorless",
    #         "https://edhrec.com/commanders/azorius",
    #         "https://edhrec.com/commanders/dimir",
    #         "https://edhrec.com/commanders/rakdos",
    #         "https://edhrec.com/commanders/gruul",
    #         "https://edhrec.com/commanders/selesnya",
    #         "https://edhrec.com/commanders/orzhov",
    #         "https://edhrec.com/commanders/izzet",
    #         "https://edhrec.com/commanders/golgari",
    #         "https://edhrec.com/commanders/boros",
    #         "https://edhrec.com/commanders/simic",
    #         "https://edhrec.com/commanders/grixis",
    #         "https://edhrec.com/commanders/esper",
    #         "https://edhrec.com/commanders/jund",
    #         "https://edhrec.com/commanders/naya",
    #         "https://edhrec.com/commanders/bant",
    #         "https://edhrec.com/commanders/abzan",
    #         "https://edhrec.com/commanders/jeskai",
    #         "https://edhrec.com/commanders/sultai",
    #         "https://edhrec.com/commanders/mardu",
    #         "https://edhrec.com/commanders/temur"
    # ]

    urls = [
            # "https://edhrec.com/commanders/mono-white",
            # "https://edhrec.com/commanders/mono-blue",
            # "https://edhrec.com/commanders/mono-black",
            # "https://edhrec.com/commanders/mono-red", #ReadTimeoutError
            "https://edhrec.com/commanders/mono-green",
            "https://edhrec.com/commanders/colorless",
            "https://edhrec.com/commanders/azorius",
            "https://edhrec.com/commanders/dimir",
            "https://edhrec.com/commanders/rakdos",
            "https://edhrec.com/commanders/gruul",
            "https://edhrec.com/commanders/selesnya",
            "https://edhrec.com/commanders/orzhov",
            "https://edhrec.com/commanders/izzet",
            "https://edhrec.com/commanders/golgari",
            "https://edhrec.com/commanders/boros",
            "https://edhrec.com/commanders/simic",
            "https://edhrec.com/commanders/grixis",
            "https://edhrec.com/commanders/esper",
            "https://edhrec.com/commanders/jund",
            "https://edhrec.com/commanders/naya",
            "https://edhrec.com/commanders/bant",
            "https://edhrec.com/commanders/abzan",
            "https://edhrec.com/commanders/jeskai",
            "https://edhrec.com/commanders/sultai",
            "https://edhrec.com/commanders/mardu",
            "https://edhrec.com/commanders/temur"
    ]


    for url in tqdm(urls, "URLS"):
        driver = webdriver.Firefox()
        driver.set_window_size(1920, 1080)
        decks = []
        folder_name = url.rstrip('/').split('/')[-1]
        os.makedirs(folder_name, exist_ok=True)
        driver.get(url)
        time.sleep(2)

        accept_cookies_button = driver.find_element(
            By.CSS_SELECTOR,
            "div.sc-knesRu.ePGZca.amc-focus-first",
        )
        accept_cookies_button.click()

        text_view_button = driver.find_element(
            By.CSS_SELECTOR,
            "div.d-flex.flex-column.h-100.justify-content-end > ul.nav.nav-tabs > li.nav-item > button.nav-link > svg.svg-inline--fa.fa-font ",
        )
        text_view_button.click()

        soup = BeautifulSoup(driver.page_source, "html.parser")
        commander_soup_select_string = "#" + folder_name + "commanders > div > span > span > a"
        commanders = soup.select(commander_soup_select_string)

        for commander in tqdm(commanders[:5], "COMMANDERS"):
            try:
                # print(commander["href"])
                driver.get(root + commander["href"])
                decks_button = driver.find_element(
                    By.CSS_SELECTOR, ".NavigationPanel_navButtons__kodsu > a:nth-child(4)"
                )
                decks_button.click()
                time.sleep(3)

                # display_25_decks = driver.find_element(By.CSS_SELECTOR, "div.btn-group > button.btn.btn-secondary")
                # display_25_decks.click()
                display_100_decks = driver.find_element(By.CSS_SELECTOR, "div.btn-group > button.btn-secondary:nth-child(4)")
                display_100_decks.click()
                time.sleep(2)

                sort_by_type = driver.find_element(By.CSS_SELECTOR, "div.w-100.btn-group.btn-group-sm > a.LinkHelper_container__tiM9S.btn.btn-sm.btn-secondary")
                sort_by_type.click()
                time.sleep(2)

                soup = BeautifulSoup(driver.page_source, "html.parser")
                table_links = soup.select(".react-bootstrap-table > table > tbody > tr > td > a")
            except (TimeoutError, NoSuchElementException, ElementClickInterceptedException):
                print(commander)
                continue
            for link in tqdm(table_links, "DECK"):
                try:
                    deck = []
                    driver.get(root + link["href"])
                    decks_button = driver.find_element(
                        By.CSS_SELECTOR,
                        "div.d-flex.flex-column.h-100.justify-content-end > ul.nav.nav-tabs > li.nav-item > button.nav-link > svg.svg-inline--fa.fa-table",
                    )
                    decks_button.click()
                    time.sleep(2)

                    soup = BeautifulSoup(driver.page_source, "html.parser")
                    h3_element = soup.find('h3', class_='m-2')
                    full_text = h3_element.get_text(strip=True)
                    extracted_word = full_text.replace("Deck with ", "", 1)
                    deck.append(extracted_word)

                    table = driver.find_element(By.CSS_SELECTOR, ".table")
                    df = pd.read_html(StringIO(table.get_attribute("outerHTML")), header=0)[0]
                    for card in list(df["Name"]):
                        midpoint = len(card) // 2
                        deck.append(card[:midpoint])

                    decks.append(deck)
                    pickle_file_path = os.path.join(folder_name, "decks.pkl")
                    with open(pickle_file_path, "wb") as fp:
                        pickle.dump(decks, fp)
                except (TimeoutError, NoSuchElementException, ElementClickInterceptedException):
                    print(link)
                    continue


if __name__ == "__main__":
    main()
