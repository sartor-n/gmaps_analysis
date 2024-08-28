from src.driver import WebDriverManager, accept_cookies_conditions

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchWindowException
from typing import Optional, List
from IPython.display import Image, display


from src.logger import get_logger

logger = get_logger(__name__)

SEARCH_RESULT_ELMENT = "a.hfpxzc"
SEARCH_BOX_EL_ID = "searchboxinput"


def gather_all_places(
    query: str,
    language: str = "en",
    coordinates: tuple[float, float, float] = (42.010398, 2.1113405, 10.1),
    output_file: Optional[str] = None,
) -> list[str]:
    """
    Gathers a list of places corresponding to a given search query on Google Maps.

    Args:
        query (str): The search query to find places on Google Maps.
        language (str, optional): The language to be used in Google Maps. Default is "en" (English).
        coordinates (tuple[float, float, float], optional): A tuple containing the latitude, longitude,
            and zoom level to start the search from. Default is (42.010398, 2.1113405, 10.1).
        output_file (Optional[str], optional): The file path to store the collected URLs. Default is None.

    Returns:
        list[str]: A list of URLs for the places found corresponding to the search query.

    Notes:
        - The function opens Google Maps in a web browser and prompts the user to manually zoom in on the
          desired area before starting the extraction process.
        - The user is required to press Enter to start the extraction after zooming in.
        - The function continues scrolling through the search results until all results are collected.
        - If an output_file is provided, the results will be stored in the specified file as a JSON list."""

    logger.debug(f"Starting to gather places for query: '{query}' with coordinates: {coordinates} and language: '{language}'")

    driver_manager = WebDriverManager()
    driver = driver_manager.get_driver(headless=False)
    places_urls = []

    try:
        # Open Google Maps
        url = f"https://www.google.com/maps/@{coordinates[0]},{coordinates[1]},{coordinates[2]}z?hl={language}"
        driver.get(url)
        accept_cookies_conditions()

        input("Please zoom in on the desired area on the map, then press Enter to start the extraction...")

        logger.debug(f"Performing search in {driver.current_url}")

        # Find the search box
        search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, SEARCH_BOX_EL_ID)))

        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)

        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, SEARCH_RESULT_ELMENT)))

        display(Image(driver.get_screenshot_as_png(), width=600))

        previous_count = 0

        while True:
            search_result_els = driver.find_elements(By.CSS_SELECTOR, SEARCH_RESULT_ELMENT)
            current_count = len(search_result_els)

            if current_count == previous_count:
                break

            for place in search_result_els[previous_count:]:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", place)
                url = place.get_attribute('href')
                if url and url not in places_urls:
                    places_urls.append(url)

            previous_count = current_count
            time.sleep(2)        

    except (KeyboardInterrupt, NoSuchWindowException) as e:
        logger.error("Early termination or window closed. Returning results collected so far.", exc_info=True)
        
    finally:
        logger.debug(f"Finished gathering places. Total places found: {len(places_urls)}")
        driver_manager.close_driver()

    if output_file:
        store_output(places_urls, output_file)

    return places_urls


import json


def store_output(list_of_places_urls: List[str], filename: str = "list_of_places.json"):
    """
    Stores a list of place URLs into a JSON file.

    Args:
        list_of_places_urls (List[str]): The list of place URLs to be stored.
        filename (str, optional): The name of the file where the URLs will be stored. Default is "list_of_places.json".

    Notes:
        - The function ensures that the file has a ".json" extension. If not, it appends ".json" to the filename.
        - The list of URLs is saved in the specified file in JSON format.
        - If there is an issue with writing to the file (e.g., due to permissions or disk space), an error message is printed with details.
    """

    logger.debug(f"Storing output to file: {filename}")

    try:
        if not filename.endswith(".json"):
            filename = filename + ".json"

        with open(file=filename, mode="w", encoding="utf-8") as f:
            json.dump(list_of_places_urls, f)

        logger.debug(f"Successfully stored the results to {filename}")

    except OSError as e:
        logger.error(f"Couldn't store the results in {filename} - Details: {e}", exc_info=True)