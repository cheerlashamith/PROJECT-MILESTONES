import requests
import json

def test_models():
    models = ['llama3.1:latest', 'qwen3:14b', 'gemma3:4b', 'qwen2.5:7b']
    print("Starting verification of all Ollama models...\n")
    for model in models:
        print(f"Testing {model}...")
        try:
            response = requests.post(
                'http://localhost:11434/api/generate', 
                json={'model': model, 'prompt': 'Say strictly "OK"', 'stream': False}, 
                timeout=180
            )
            if response.status_code == 200:
                data = response.json()
                print(f"  [PASS] {model} is WORKING. Response: {data.get('response', '').strip()}\n")
            else:
                print(f"  [FAIL] {model} FAILED. Status: {response.status_code}, Response: {response.text}\n")
        except Exception as e:
            print(f"  [ERROR] {model} encountered an error: {e}\n")
            
if __name__ == '__main__':
    test_models()
