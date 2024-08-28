from openai import OpenAI
import os



def pick_topic_relevant_chunks(text, topic:str):
    """Takes a RAW review and extracts from long reviews only relevant information"""

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


    if len(text)> 250:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"You receive from the user the text of a review of a GMaps location. You will extract and return EXCLUSIVELY sentences and chunks that are referring to '{topic}' and the context to understand it. If the text contains no information about '{topic}', return '#NONE#'",
                },        {
                    "role": "user",
                    "content": text,
                }
            ],
            model="gpt-4o-mini",
        )
        return chat_completion.choices[0].message.content if chat_completion.choices[0].message.content != "#NONE#" else None
    else:
        return text