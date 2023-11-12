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

def get_answer(prompt, model_choice, common_instructions, api_key, temperature, seed):
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
        "top_p": 1,
        "seed": seed 
    }
    response = requests.post(API_URL, headers=headers, json=data)
    logging.info(f"Response Status: {response.status_code}, Response Time: {response.elapsed.total_seconds()} seconds")
    if response.status_code != 200:
        logging.error(f"Non-200 response received: {response.status_code}\nResponse text: {response.text}")
        return None
    try:
        response_data = response.json()
        answer = response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
        system_fingerprint = response_data.get('system_fingerprint', 'Not available')
        return answer, system_fingerprint
    except Exception as e:
        logging.error(f"Exception occurred while parsing the response: {e}")
        return None, None 

def get_answers(prompts, model_choice, common_instructions, api_key, temperature, seed, progress_bar):
    results = []
    total = len(prompts)
    for index, prompt in enumerate(prompts):
        answer, system_fingerprint = get_answer(prompt, model_choice, common_instructions, api_key, temperature, seed)
        results.append(answer)
        # Update the progress bar
        progress = (index + 1) / total
        progress_bar.progress(progress)
        logging.info(f"Processing prompt {index+1}/{total}: {prompt[:50]}... System Fingerprint: {system_fingerprint}")

        time.sleep(5) 

    return results