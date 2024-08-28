from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import pandas as pd
from tqdm import tqdm
from src.extract_reviews import extract_place


from typing import List, Optional

from src.logger import get_logger

logger = get_logger(__name__)


def extract_places_batch(
    topic: str,
    limit: int,
    list_of_places_urls: Optional[List[str]] = None,
    input_file: Optional[str] = None,
) -> pd.DataFrame:
    """
    Processes a batch of Google Maps place URLs to extract reviews related to a specific topic.

    Args:
        topic (str): The specific topic or keyword to search for in the reviews.
        limit (int): The maximum number of reviews to collect for each place.
        list_of_places_urls (Optional[List[str]], optional): A list of Google Maps place URLs to process. Default is None.
        input_file (Optional[str], optional): The file path to load a list of URLs from a JSON file. Default is None.

    Returns:
        pd.DataFrame: A DataFrame containing all the extracted reviews related to the topic from the batch of URLs.

    Notes:
        - If both `list_of_places_urls` and `input_file` are provided, the function will prioritize `list_of_places_urls`.
        - The function uses `ThreadPoolExecutor` for parallel processing of multiple URLs to speed up extraction.
        - The final DataFrame aggregates reviews from all processed URLs.
    """

    list_of_places_urls = loads_urls(list_of_places_urls, input_file)

    # Initialize an empty DataFrame
    final_store = pd.DataFrame()

    logger.debug(f"Starting batch extraction of {len(list_of_places_urls)} places...")
    # Use ThreadPoolExecutor for parallel execution
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(extract_place, topic, url, limit): url
            for url in list_of_places_urls
        }

        for future in tqdm(
            as_completed(futures), total=len(futures), desc="Processing Places", postfix="\n"
        ):
            try:
                results_store = future.result()

                if not isinstance(results_store, pd.DataFrame):
                    logger.error(f"Expected DataFrame from extract_place, got {type(results_store)}")
                elif not results_store.empty:
                    final_store = pd.concat([final_store, results_store], ignore_index=True)
            except Exception as e:
                logger.error(f"Error processing a place: {e}")

    logger.debug(f"Completed batch extraction. Total extracted reviews: {len(final_store)}")
    return final_store
 


def loads_urls(
    list_of_places_urls: Optional[List[str]], input_file: Optional[str]
) -> List[str]:
    """
    Loads a list of Google Maps place URLs from a provided list or a JSON file.

    Args:
        list_of_places_urls (Optional[List[str]]): A list of Google Maps place URLs. Default is None.
        input_file (Optional[str]): The file path to load URLs from a JSON file. Default is None.

    Returns:
        List[str]: The list of Google Maps place URLs.

    Raises:
        ValueError: If both `list_of_places_urls` and `input_file` are not provided.

    Notes:
        - If both `list_of_places_urls` and `input_file` are provided, the function will prioritize `list_of_places_urls`.
        - The function validates the input and raises an exception if neither a list nor a file is provided.
    """
    if list_of_places_urls:
        # Uses the provided list
        logger.debug("Using provided list of URLs.")
        # TODO: add validation
        pass
    elif input_file:
        logger.debug(f"Loading URLs from file: {input_file}")
        # Loads the list of URLs from JSON persistently stored
        with open(input_file, "r", encoding="utf-8") as f:
            list_of_places_urls = json.load(f)
    elif not list_of_places_urls and not input_file:
        logger.error("Both 'list_of_places_urls' and 'input_file' are undefined.")
        raise ValueError(
            "At least one of list_of_places_urls and input_file must be defined"
        )
    return list_of_places_urls
