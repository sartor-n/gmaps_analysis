from selenium.common.exceptions import (
    TimeoutException,
    JavascriptException,
    WebDriverException,
)
from src.driver import WebDriverManager, accept_cookies_conditions

from src.extract_support import (
    extract_place_info,
    navigate_to_reviews,
    discover_reviews,
    process_reviews,
)


from traceback import format_exc

import pandas as pd
from typing import Optional

import time
import random


def extract_place(
    topic: str,
    place_gmaps_url: str,
    limit: Optional[int] = None,
    store: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """Extracts and collects reviews related to a specific topic from a Google Maps place page.

    Args:
        topic (str): The specific topic or keyword to search for in the reviews.
        place_gmaps_url (str): The URL of the Google Maps place from which to extract reviews.
        store (Optional[pd.DataFrame], optional): An existing DataFrame to update with the newly collected reviews.
            If None, a new DataFrame will be created. Default is None.
        limit (Optional[int], optional): The maximum number of reviews to collect. If None, all available reviews
            related to the topic will be collected. Default is None.

    Returns:
        pd.DataFrame: A DataFrame containing the collected reviews related to the specified topic.

    Notes:
        - The function initializes a WebDriver instance to navigate to the provided Google Maps place URL.
        - It then navigates to the reviews section, searches for the specified topic, and collects relevant reviews.
        - If errors occur during navigation or review collection (e.g., due to timeouts, JavaScript errors, or WebDriver issues),
          the function will skip the place and print an error message.
        - The function returns an updated DataFrame containing the newly collected reviews along with any previously stored reviews.
    """
    local_store = pd.DataFrame()

    # Each thread will initialize its own WebDriver
    driver_manager = WebDriverManager()
    driver = driver_manager.get_driver(headless=True)

    # Waits a random amount of time to avoid calls all together
    time.sleep(random.randint(0, 4) / 10)

    try:
        driver.get(place_gmaps_url)
        accept_cookies_conditions()

        place_info = extract_place_info(place_gmaps_url)
        navigate_to_reviews(place_gmaps_url=place_gmaps_url, topic=topic)

        local_store = _collect_reviews(topic, place_info, limit)

    except (WebDriverException):
        print(
            f"Error in processing {place_gmaps_url[:min(100, len(place_gmaps_url)-1)]}, will skip it.\nDetails: {format_exc()}"
        )
    finally:
        driver_manager.close_driver()

    if store:
        return pd.concat([store, local_store], ignore_index=True)
    return local_store


from retry import retry


@retry(exceptions=[WebDriverException, TimeoutException], tries=2, delay=1, jitter=(1, 3))
def _collect_reviews(
    topic: str, place_info: dict, limit: Optional[int]
) -> pd.DataFrame:
    """
    Collects reviews related to a specific topic from the Google Maps place page.

    Args:
        topic (str): The specific topic or keyword to search for in the reviews.
        place_info (dict): A dictionary containing information about the place.
        limit (Optional[int], optional): The maximum number of reviews to collect. Default is None.

    Returns:
        pd.DataFrame: A DataFrame containing the collected reviews.
    """
    local_store = pd.DataFrame()
    reviews_list = discover_reviews(limit=limit)
    still_to_go = True

    while still_to_go:
        try:
            new_reviews = process_reviews(
                topic=topic, reviews_list=reviews_list, place_info=place_info
            )
            local_store = pd.concat([local_store, new_reviews], ignore_index=True)

            reviews_list = discover_reviews(
                last_cc_element=reviews_list[-1] if len(reviews_list) > 0 else None,
                limit=limit,
            )

            if len(reviews_list) == 0:
                still_to_go = False

        except (TimeoutException, JavascriptException, WebDriverException) as e:
            print(f"Error during processing reviews: {e}")
            still_to_go = False

    print(f"Got {len(local_store)} reviews for {place_info.get('name', '--')}")
    return local_store
