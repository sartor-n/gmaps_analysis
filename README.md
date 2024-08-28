# GMaps Reviews Analyzer

## Overview

The GMaps Reviews Analyzer is a comprehensive tool designed for extracting and analyzing reviews from Google Maps. With its robust web scraping and review processing functionalities, it facilitates user-defined searches for specific topics across multiple places, aggregates the data, and generates insightful summaries. It leverages various technologies including Selenium for web automation and LangChain for advanced natural language processing.

## Features

- **Place URL Gathering**: Collect URLs of places based on search queries.
- **Review Extraction**: Extract comments and ratings from Google Maps reviews.
- **Parallel Processing**: Efficiently process multiple places in parallel.
- **Data Cleaning**: Use OpenAI's API to filter and extract topic-relevant chunks from reviews.
- **Insight Generation**: Aggregate reviews and generate structured insights using LangChain and OpenAI's language model.

## Installation

1. **Clone the Repository**:
    ```sh
    git clone https://github.com/yourusername/gmaps-reviews-analyzer.git
    cd gmaps-reviews-analyzer
    ```

2. **Create and Activate Virtual Environment**:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install Required Dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

4. **Set Up Environment Variables**:
   - Create a `.env` file in the root directory and add your OpenAI API key:
     ```env
     OPENAI_API_KEY=your_openai_api_key
     ENV=development  # or production
     ```

## Usage

### 1. Gather Place URLs

```python
from src.get_places import gather_all_places

list_of_places_urls = gather_all_places(
    query="bar",
    coordinates=(45.435271, 12.337798, 14.03),
    output_file="output/example_places.json",
    limit=10
)
list_of_places_urls[:3]
```

### 2. Extract Reviews for a Specific Place

```python
from src.extract_reviews import extract_place

info_store = extract_place(
    topic="aperol spritz",
    place_gmaps_url=list_of_places_urls[0],
    limit=5
)
info_store.sample(min(5, len(info_store)))
```

### 3. Extract Reviews for Multiple Places in Parallel

```python
from src.extract_multiple import extract_places_batch

reviews_store = extract_places_batch(
    topic="aperol spritz", 
    limit=15, 
    input_file="output/example_places.json"
)

import pandas as pd

reviews_store.to_csv(f"example_reviews.csv", index=False)
reviews_store.sample(min(5, len(reviews_store)))
```

### 4. Analyze Places for Specific Insights

```python
from langchain_core.pydantic_v1 import BaseModel, Field

class MuseumRating(BaseModel):
    summary: str = Field(description="A summary of the reviews, focused on aperol spritz")
    has_spritz: bool = Field(description="Does this bar serve aperol spritz?")
    rating: int = Field(description="Using a score from 1 to 5, how happy are the users of this bar about their aperol spritz?")

from src.places_analysis import analyse_places

places_analysis_store = analyse_places(store=reviews_store, questions_structure=MuseumRating)

import datetime
places_analysis_store.to_csv(f"places_analysis_{datetime.datetime.now().isoformat()}.csv", index=False)
places_analysis_store
```

### Running the Code

- Open `main.ipynb` in Jupyter Notebook to run the entire workflow.


