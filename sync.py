import requests
import logging
import time

API_URL = "https://api.openai.com/v1/chat/completions"

logging.basicConfig(level=logging.INFO)

def is_valid_api_key(api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo-16k",
        "messages": [{"role": "user", "content": "test"}],
        "max_tokens": 350
    }
    response = requests.post(API_URL, headers=headers, json=data)
    return response.status_code == 200

def get_answer(prompt, model_choice, common_instructions, api_key, temperature):
    full_prompt = f"{common_instructions}\n{prompt}" if common_instructions else prompt
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "OpenAI Python v0.27.3"
    }
    data = {
        "model": model_choice,
        "messages": [{"role": "user", "content": full_prompt}],
        "temperature": temperature,
        "top_p": 1
    }
    response = requests.post(API_URL, headers=headers, json=data)
    if response.status_code == 200:
        response_data = response.json()
        return response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
    else:
        logging.error(f"Error: {response.status_code}, {response.text}")
        return None

def get_answers(prompts, model_choice, common_instructions, api_key, temperature):
    results = []
    for prompt in prompts:
        answer = get_answer(prompt, model_choice, common_instructions, api_key, temperature)
        results.append(answer)
        time.sleep(1)  # Sleep for a second between each request to avoid rate limiting
    return results