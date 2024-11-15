import os
from flask import Flask, request, jsonify
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

# Setup
GCP_PROJECT = os.environ["GCP_PROJECT"]
GCP_LOCATION = "us-central1"
MODEL_ENDPOINT = "projects/project-id-3187519002330642642/locations/us-central1/endpoints/6870682135716429824"  # Replace with your finetuned model endpoint

generation_config = GenerationConfig(
    max_output_tokens=3000,
    temperature=0.75,
    top_p=0.95,
)

vertexai.init(project=GCP_PROJECT, location=GCP_LOCATION)
generative_model = GenerativeModel(MODEL_ENDPOINT)

app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    query = data.get('prompt', '')
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    try:
        response = generative_model.generate_content(
            [query],
            generation_config=generation_config,
            stream=False,
        )
        generated_text = response.text
        return jsonify({'response': generated_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
