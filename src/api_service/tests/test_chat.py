import uuid

import requests


def test_direct_chat():
    # Initialize the session
    session = requests.Session()

    # Define the base URL
    HOST = "sales-mate-api-service"
    BASE = f"http://{HOST}:9876"

    # Set headers once for the session
    # make the session ID a uuid string
    session.headers.update(
        {"Content-Type": "application/json", "X-Session-ID": str(uuid.uuid4())}
    )

    # Define the endpoint and payload
    url = f"{BASE}/direct-chat/chats"
    sample_chat = """
    Hi, my name is John. I'm working with IQT Investment Management and I heard
    you're in the market for a financial planner. I was wondering if you had any
    specific goals in mind and how we can assist you achieve them.
    """
    payload = {"content": sample_chat}

    # Use the session to send a POST request
    response = session.post(url, json=payload)

    # Check if the request was successful
    assert response.status_code == 200

    # close session
    session.close()
