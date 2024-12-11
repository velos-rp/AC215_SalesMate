import os
from typing import Dict, List

import vertexai
from api.utils.sytem_prompt import SYSTEM_INSTRUCTION
from google.cloud import secretmanager
from vertexai.generative_models import ChatSession, GenerativeModel

# Setup
GCP_PROJECT = os.environ["GCP_PROJECT"]
GCP_LOCATION = "us-central1"
SECRET_ID = "llm-endpoint"
EMBEDDING_MODEL = "text-embedding-004"
EMBEDDING_DIMENSION = 768
GENERATIVE_MODEL = "gemini-1.5-flash-002"

# Configuration settings for the content generation
generation_config = {
    "max_output_tokens": 8192,  # Maximum number of tokens for output
    "temperature": 0.1,  # Control randomness in output
    "top_p": 0.95,  # Use nucleus sampling
}


vertexai.init(project=GCP_PROJECT, location=GCP_LOCATION)


FINETUNED = os.environ["FINETUNED_MODEL"]

if FINETUNED != "1":

    generative_model = GenerativeModel(
        GENERATIVE_MODEL, system_instruction=[SYSTEM_INSTRUCTION]
    )
    print("Using general model fir Gemini calls")
else:
    client = secretmanager.SecretManagerServiceClient()
    secret_version_name = f"projects/{GCP_PROJECT}/secrets/{SECRET_ID}/versions/latest"
    response = client.access_secret_version(request={"name": secret_version_name})
    model_endpoint = response.payload.data.decode("UTF-8")
    generative_model = GenerativeModel(
        model_endpoint, system_instruction=[SYSTEM_INSTRUCTION]
    )
    print("Using finetuned model for Gemini calls")


# Initialize chat sessions
chat_sessions: Dict[str, ChatSession] = {}


def create_chat_session() -> ChatSession:
    """Create a new chat session with the model"""
    return generative_model.start_chat()


def generate_chat_response(chat_session: ChatSession, message: Dict) -> str:
    """
    Generate a response using the chat session to maintain history.
    Handles text inputs.

    Args:
      chat_session: The Vertex AI chat session
      message: Dict containing 'content' (text)

    Returns:
        str: The model's response
    """

    message_parts = []

    # Add text content if present
    if message.get("content"):
        message_parts.append(message["content"])

    if not message_parts:
        raise ValueError("Message must contain 'content'")

    response = chat_session.send_message(
        message.get("content"), generation_config=generation_config
    )

    return response.text


def rebuild_chat_session(chat_history: List[Dict]) -> ChatSession:
    """Rebuild a chat session with complete context"""
    new_session = create_chat_session()

    for message in chat_history:
        if message["role"] == "user":
            generate_chat_response(new_session, message)
        #
        #     response = new_session.send_message(
        #         message["content"],
        #         generation_config=generation_config
        #     )

    return new_session
