# Initialize the text-generation pipeline
import torch
from flask import Flask, jsonify, request
from transformers import pipeline

# Initialize the text-generation pipeline
pipe = pipeline(
    "text-generation",
    model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    torch_dtype=torch.bfloat16,
    device_map="cpu",
)

app = Flask(__name__)


@app.route("/generate", methods=["POST"])
def generate():
    try:
        # Get the prompt from the incoming request
        data = request.get_json()
        query = data.get("prompt")

        # Define the conversation template
        content = "You are a friendly chatbot who always funny and interesting. \
              You only reply with the actual answer without repeating my question."
        messages = [
            {
                "role": "system",
                "content": content,
            },
            {"role": "user", "content": query},
        ]

        # Prepare the prompt
        prompt = pipe.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

        # Generate the output using the model
        outputs = pipe(
            prompt,
            max_new_tokens=256,
            do_sample=True,
            temperature=0.7,
            top_k=50,
            top_p=0.95,
        )

        # Return the generated response
        return jsonify({"response": outputs[0]["generated_text"]})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    # Run the app on port 5000
    app.run(host="0.0.0.0", port=5000)
