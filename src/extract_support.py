from typing import Optional, List, Any
from selenium.webdriver.remote.webelement import WebElement
import pandas as pd
import time
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.driver import WebDriverManager

from src.logger import get_logger

logger = get_logger(__name__)


REVIEWS_ELS_CLASS = "jftiEf.fontBodyMedium"
MORE_BTN_CLASS = "w8nwRe.kyuRq"
REVIEW_TEXT_EL_CLASS = "wiI7pd"
REVIEW_DATE_EL_CLASS = "rsqaWe"
REVIEW_POSITIVE_STAR_EL_CLASS = "hCCjke.google-symbols.NhBTye.elGi1d"
REVIEW_SECTION_EL_XPATH = "//div[contains(@class, 'pV4rW q8YqMd')]//div[contains(@class, 'etWJQ kdfrQc NUqjXc')]//button[contains(@class, 'g88MCb S9kvJb')]"
REVIEWS_SEARCHBOX_EL_CLASS = "sW8iyd"


def discover_reviews(
    last_cc_element: Optional[WebElement] = None, limit: Optional[int] = None
) -> List[WebElement]:
    driver = WebDriverManager().get_driver()

    all_reviews_els = driver.find_elements(By.CLASS_NAME, REVIEWS_ELS_CLASS)
    logger.debug(f"Found {len(all_reviews_els)} review elements.")

    # If a limit is provided, slice the list to only include up to that many elements
    if limit is not None and limit > 0:
        all_reviews_els = all_reviews_els[:limit]

    # If last_cc_element is provided, find its index and return elements after it
    if last_cc_element:
        try:
            idx = all_reviews_els.index(last_cc_element)
            new_els = all_reviews_els[idx + 1 :]
        except ValueError:
            new_els = all_reviews_els  # last_cc_element not found, return all
    else:
        new_els = all_reviews_els

    logger.debug(f"Returning {len(new_els)} new review elements.")
    return new_els


def get_text_element(
    container_el: WebElement, locator: tuple[str, str], default: str = ""
) -> str:
    try:
        return container_el.find_element(*locator).text
    except NoSuchElementException:
        logger.debug(f"Element with locator {locator} not found in container.")
        return default
    
    
def get_url_element(
    container_el: WebElement, locator: tuple[str, str], default: str = ""
) -> str:
    try:
        return container_el.find_element(*locator).get_attribute("href")
    except NoSuchElementException:
        logger.debug(f"Element with locator {locator} not found in container.")
        return default


def process_reviews(
    topic: str,
    reviews_list: List[WebElement],
    place_info: Optional[dict[str, Any]] = None,
) -> pd.DataFrame:
    """Runs through the list of reviews, extracts the relevant information and stores them in a pandas store. It will also include place_info in the row, if provided"""
    review_data_list = []
    from src.clean_review import pick_topic_relevant_chunks
    driver = WebDriverManager().get_driver()

    logger.debug(f"Processing {len(reviews_list)} reviews for topic '{topic}'.")

    for review_el in reviews_list:
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", review_el
        )
        time.sleep(1)

        try:
            more_button = review_el.find_element(By.CLASS_NAME, MORE_BTN_CLASS)
            more_button.click()
        except NoSuchElementException:
            pass

        try:
            review = get_text_element(
                container_el=review_el, locator=(By.CLASS_NAME, REVIEW_TEXT_EL_CLASS)
            )
            date = get_text_element(
                container_el=review_el, locator=(By.CLASS_NAME, REVIEW_DATE_EL_CLASS)
            )
            review_score = len(
                review_el.find_elements(By.CLASS_NAME, REVIEW_POSITIVE_STAR_EL_CLASS)
            )

            relevant_text = pick_topic_relevant_chunks(text=review, topic=topic)
            if relevant_text:
                review_data_list.append(
                    {
                        "review": relevant_text,
                        "date": date,
                        "score": review_score,
                        **place_info,
                    }
                )
        except Exception as e:
            logger.error(f"Failed to extract data from an element: {e}")

    logger.debug(f"Processed {len(review_data_list)} relevant reviews.")
    return pd.DataFrame(review_data_list)

from urllib3.exceptions import HTTPError

def navigate_to_reviews(place_gmaps_url: str, topic: str):
    try:
        driver = WebDriverManager().get_driver()
        reviews_section = WebDriverWait(driver=driver, timeout=10).until(
            EC.presence_of_element_located((By.XPATH, REVIEW_SECTION_EL_XPATH))
        )
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", reviews_section
        )
        reviews_section.click()
        reviews_search_box = driver.find_element(By.CLASS_NAME, REVIEWS_SEARCHBOX_EL_CLASS)
        reviews_search_box.send_keys(topic)
        reviews_search_box.send_keys(Keys.RETURN)
        time.sleep(3)
        logger.debug(f"Navigated to reviews section for URL: {simplify_url(place_gmaps_url)}")
    except HTTPError as e:
        logger.error(f"Couldn't connect to URL: {simplify_url(place_gmaps_url)}")
        raise e




ORIGINAL_MUSEUM_NAME_CLASS = "bwoZTb"
ENG_MUSEUM_NAME_CLASS = "DUwDvf.lfPIob"
DESCRIPTION_CLASS = "PYvSYb"

ADDRESS_CLASS = 'button[data-item-id="address"] .Io6YTe'
PHONE_CLASS = 'button[data-item-id*="phone"] .Io6YTe'
WEB_CLASS = 'a[data-item-id="authority"]'

def extract_place_info(place_gmaps_url: str = None) -> dict[str, str]:

    driver = WebDriverManager().get_driver()
    logger.debug(f"Extracting place info for URL: {simplify_url(place_gmaps_url)}")

    # Extract name and description of Place
    name = get_text_element(driver, (By.CLASS_NAME, ORIGINAL_MUSEUM_NAME_CLASS), None) or get_text_element(driver, (By.CLASS_NAME, ENG_MUSEUM_NAME_CLASS))
    description = get_text_element(driver, (By.CLASS_NAME, DESCRIPTION_CLASS))
    
    # Scrolls to Place Details
    details_section = WebDriverWait(driver=driver, timeout=10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'button[data-item-id="address"]' ))
    )
    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});", details_section
    )

    # Extracts important details
    address = get_text_element(driver, (By.CSS_SELECTOR, ADDRESS_CLASS))
    phone = get_text_element(driver, (By.CSS_SELECTOR, PHONE_CLASS))
    web = get_url_element(driver, (By.CSS_SELECTOR, WEB_CLASS))

    logger.debug(f"Extracted info - Name: {name}, Address: {address}, Phone: {phone}, Web: {web}")
    return {"place_url": place_gmaps_url, "name": name, "description": description, "address": address, "phone": phone, "web": web}

import re

def simplify_url(url):
    # The regex pattern to extract the desired part of the URL
    pattern = r"^https:\/\/www\.google\.com\/maps\/place\/[^\/]+\/"

    # Using re.search to find the match
    match = re.search(pattern, url)

    # Extracting and printing the result
    if match:
        return  match.group(0)
        
    return url