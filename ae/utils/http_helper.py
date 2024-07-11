from typing import Any

import requests


def make_post_request(url: str, data: dict[str, Any], api_key: str, api_key_header_name: str = "apikey") -> dict[str, Any]|None:
    """
    Makes a POST request to the specified URL with a JSON body and an API key header.

    Args:
        url (str): The URL to send the POST request to.
        data (Dict[str, Any]): The JSON data to include in the POST request body.
        api_key (str): The API key to include in the request headers.
        api_key_header_name (str): The name of the header to include the API key in. Defaults to "apikey".

    Returns:
        Optional[Dict[str, Any]]: The JSON response from the server if the request was successful and the response is in JSON format.
        None: If the request failed or the response is not in JSON format.

    Raises:
        requests.exceptions.RequestException: If an error occurs during the HTTP request.
    """
    # Define the headers for the request
    headers = {
        'Content-Type': 'application/json',
        api_key_header_name: api_key
    }

    try:
        # Make the POST request with the given URL, data, and headers
        response = requests.post(url, json=data, headers=headers)

        # Check if the request was successful
        response.raise_for_status()

        # Attempt to return the JSON response
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
    except ValueError:
        print("Error: Response is not in JSON format")
        return None
