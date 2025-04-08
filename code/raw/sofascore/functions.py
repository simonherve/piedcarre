import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

import json
from selenium import webdriver
from selenium.webdriver.common.by import By

def get_json(url):
    """
    Fetches JSON data from a given URL by using Selenium to render the page
    and extracting the content within a <pre> tag.

    Args:
        url (str): The URL to fetch the JSON data from.

    Returns:
        dict: A dictionary containing the status code and either the JSON data
              or an error message.
              - If successful (status_code 200), the dictionary will have the format:
                {"status_code": 200, "json": <parsed JSON data>}
              - If an "error" key is found in the parsed JSON (status_code 403):
                {"status_code": 403}
              - If any exception occurs during the process (status_code 400):
                {"status_code": 400, "exception": <exception object>}
    """
    try:
        # Initialize a Chrome webdriver instance. This will open a Chrome browser.
        driver = webdriver.Chrome()
        # Navigate the browser to the specified URL.
        driver.get(url)
        # Find the first <pre> HTML element on the page. This is often used
        # to display preformatted text, including JSON responses.
        pre = driver.find_element(By.TAG_NAME, 'pre')
        # Extract the text content from the <pre> element and parse it as JSON.
        response = json.loads(pre.text)
        # Close the browser window. It's important to clean up the webdriver.
        driver.close()

        # Check if the parsed JSON response contains an "error" key.
        # This is a common way for APIs to indicate an error within a successful HTTP request.
        if "error" in response.keys():
            # If an "error" key is present, return a 403 status code (Forbidden).
            return {"status_code": 403}
        else:
            # If no "error" key is found, assume the request was successful and
            # return a 200 status code (OK) along with the parsed JSON data.
            return {"status_code": 200, "json": response}

    # Catch any exceptions that might occur during the process, such as network errors,
    # issues with the webdriver, or problems parsing the JSON.
    except Exception as e:
        # If an exception occurs, return a 400 status code (Bad Request) along with
        # the exception object for debugging purposes.
        return {"status_code": 400, "exception": e}