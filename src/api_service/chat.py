import json

import requests

# Your AWS-hosted LLM API URL
API_URL = "http://ec2-18-188-228-148.us-east-2.compute.amazonaws.com:5000/generate"


def chat_with_llm(prompt):
    headers = {"Content-Type": "application/json"}
    data = {"prompt": prompt}
    response = requests.post(API_URL, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        return response.json().get("response", "No response")
    else:
        return f"Error: {response.status_code}, {response.text}"


def main():
    print("Chatbot initialized. Type your messages below (type 'exit' to quit):")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Exiting chat...")
            break
        response = chat_with_llm(user_input)
        print(f"Chatbot: {response}")


if __name__ == "__main__":
    main()
