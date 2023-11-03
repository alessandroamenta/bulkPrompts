import aiohttp
import asyncio
import logging

API_URL = "https://api.openai.com/v1/chat/completions"

logging.basicConfig(level=logging.INFO)

async def is_valid_api_key(api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo-16k",  # Use the model you want to check with
        "messages": [{"role": "user", "content": "test"}],
        "max_tokens": 350
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, headers=headers, json=data) as response:
            if response.status == 200:
                return True  # The API key is valid
            else:
                return False  # The API key is invalid or there was another error

async def get_answer(session, prompt, model_choice, common_instructions, api_key):
    full_prompt = f"{common_instructions}\n{prompt}" if common_instructions else prompt
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "OpenAI Python v0.27.3"
    }
    data = {
        "model": model_choice,
        "messages": [{"role": "user", "content": full_prompt}],
        "temperature": 0.2,
        "top_p": 1
    }
    async with session.post(API_URL, headers=headers, json=data) as response:
        logging.info(f"Request payload: {data}")
        if response.status != 200:
            # Log non-200 responses with their text for debugging
            response_text = await response.text()
            logging.error(f"Non-200 response received: {response.status}\nResponse text: {response_text}")
            return None  # Handle non-200 responses appropriately

        try:
            response_data = await response.json()
            logging.info(f"Response data: {response_data}")
            # Extract content if the expected structure is present
            return response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
        except Exception as e:
            # Log any exception that occurs during the JSON parsing
            logging.error(f"Exception occurred while parsing the response: {e}")
            return None  # Handle exceptions appropriately


async def get_answers(prompts, model_choice, common_instructions, api_key):
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*(get_answer(session, prompt, model_choice, common_instructions, api_key) for prompt in prompts))
    return results