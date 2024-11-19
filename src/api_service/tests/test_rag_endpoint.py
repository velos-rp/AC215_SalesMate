import requests


def test_rag_endpoint():
    HOST = "sales-mate-api-service"

    BASE = f"http://{HOST}:9000"
    ENDPOINT = "rag-copilot"
    URL = f"{BASE}/{ENDPOINT}/"

    sample_chat = """
    Sorry, I was saying that in the short term, I'm thinking of buying a
    plot of land to build a country house. In the medium term, and in the
    long term, I have a dream of opening my own art gallery. What advice
    do you have for good financial planning?
    """

    params = {"input": sample_chat}

    response = requests.get(URL, params=params)

    # Check if the request was successful
    assert response.status_code == 200
