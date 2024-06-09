import time
from io import StringIO

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By


def main():
    root = "https://edhrec.com"
    urls = ["https://edhrec.com/commanders/w"]
    driver = webdriver.Firefox()
    driver.set_window_size(1920, 1080)

    for url in urls:
        driver.get(url)
        time.sleep(2)

        accept_cookies_button = driver.find_element(
            By.CSS_SELECTOR,
            "div.sc-qRumB:nth-child(2)",
        )
        accept_cookies_button.click()

        text_view_button = driver.find_element(
            By.CSS_SELECTOR,
            ".CardLists_buttons__y4Jqa > div:nth-child(3) > a:nth-child(1)",
        )
        text_view_button.click()

        soup = BeautifulSoup(driver.page_source, "html.parser")
        commanders = soup.select("#mono-whitecommanders > div > span > span > a")

        for commander in commanders:
            print(commander["href"])
            driver.get(root + commander["href"])
            decks_button = driver.find_element(
                By.CSS_SELECTOR, ".NavigationPanel_navButtons__kodsu > a:nth-child(4)"
            )
            decks_button.click()
            time.sleep(3)

            sort_by_type = driver.find_element(By.CSS_SELECTOR, "th.sortable:nth-child(3)")
            sort_by_type.click()
            time.sleep(2)
            
            table = driver.find_element(By.CSS_SELECTOR, ".table")
            df = pd.read_html(StringIO(table.get_attribute("outerHTML")), header=0)[0]
            df.rename(columns={df.columns[0]: "Card List"}, inplace=True)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            table_links = soup.select(
                ".react-bootstrap-table > table > tbody > tr > td > a"
            )

            for index, link in enumerate(table_links):
                driver.get(root + link["href"])
                decks_button = driver.find_element(
                    By.CSS_SELECTOR,
                    ".CardLists_buttons__y4Jqa > div:nth-child(3) > a:nth-child(1)",
                )
                decks_button.click()
                time.sleep(2)

                soup = BeautifulSoup(driver.page_source, "html.parser")
                card_names = soup.select("span > span > a")

                print(index)

                df.loc[index, "Card List"] = ",".join(
                    [card_name.string for card_name in card_names]
                )

            print(df)


if __name__ == "__main__":
    main()
