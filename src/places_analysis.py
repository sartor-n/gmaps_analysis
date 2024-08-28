from dotenv import load_dotenv
import os
import pandas as pd
from typing import Dict, Any
import openai
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel

from src.logger import get_logger

logger = get_logger(__name__)
   
def aggregate_reviews(store: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate reviews by place name, combining multiple reviews into one string.
    
    Args:
        store (pd.DataFrame): DataFrame containing the reviews data.
    
    Returns:
        pd.DataFrame: DataFrame with aggregated reviews by place name.
    """
    return (
        store.groupby(["name", "description", "address", "phone", "web"])["review"]
        .apply(lambda x: "\n\n".join(x))
        .reset_index()
    )

def create_prompt_template() -> PromptTemplate:
    """
    Create a prompt template for the review analysis task.
    
    Args:
        questions (str): Formatted string of questions to be asked in the prompt.
    
    Returns:
        PromptTemplate: The generated prompt template.
    """
    template = """
    You are an expert review analyzer. You will be given aggregated reviews of a place, and you need to answer the following questions based on the reviews.
    All your answers are in english, even if the review language is different.

    {questions}

    Reviews: {reviews}
    """
    return PromptTemplate.from_template(template)

from langchain_core.runnables import Runnable

def generate_insights(
    aggregated_reviews: pd.DataFrame, 
    prompt_template: PromptTemplate, 
    structured_llm: Runnable,
    questions: str
) -> Dict[str, Dict[str, Any]]:
    """
    Generate insights for each place by analyzing the reviews with a language model.
    
    Args:
        aggregated_reviews (pd.DataFrame): DataFrame with aggregated reviews.
        prompt_template (PromptTemplate): The prompt template used for the analysis.
        structured_llm (Any): The language model to generate structured output.
    
    Returns:
        Dict[str, Dict[str, Any]]: Dictionary containing insights for each place.
    """
    results = {}
    for _, row in aggregated_reviews.iterrows():
        reviews = row["review"]
        place_name = row["name"]

        formatted_prompt = prompt_template.format(reviews=reviews, questions=questions)

        try:
            response = structured_llm.invoke(formatted_prompt)  # type: BaseModel

            # Store the result in the dictionary
            results[place_name] = {
                **response.dict(),
                **row[["name", "description", "address", "phone", "web", "review"]].to_dict(),
            }
            logger.debug(f"Insights generated for {place_name}.")
        except Exception as e:
            logger.error(f"Error generating insights for {place_name}: {e}")

    return results


def analyse_places(store: pd.DataFrame, questions_structure: BaseModel) -> pd.DataFrame:
    """
    Main function to analyze museum reviews for audio guides and generate insights.
    
    Args:
        store (pd.DataFrame): DataFrame containing the reviews data.
        env_path (str): Path to the .env file with environment variables.
    
    Returns:
        pd.DataFrame: Dataframe containing insights for each museum.
    """
    # Load environment variables and initialize OpenAI API
    load_dotenv()

    openai.api_key = os.environ.get("OPENAI_API_KEY")

    # Aggregate reviews
    aggregated_reviews = aggregate_reviews(store)

    # Initialize OpenAI LLM
    llm = ChatOpenAI(model="gpt-4o-2024-08-06")
    structured_llm = llm.with_structured_output(questions_structure)

    # Define questions
    questions = "\n".join(
        [
            f"{idx}. {field.field_info.description}"
            for idx, field in enumerate(questions_structure.__fields__.values())
        ]
    )

    # Create prompt template
    prompt_template = create_prompt_template()

    # Generate insights
    results = generate_insights(aggregated_reviews, prompt_template, structured_llm, questions)

    return pd.DataFrame.from_dict(results, orient="index")
