from selenium.webdriver import Chrome, ChromeOptions


def load_driver():
    """
    Loads and returns a selenium webdriver driver with specified options.

    Returns:
        driver: The driver with specified options.
    """
    options = ChromeOptions()
    options.add_argument('--incognito')
    options.add_argument('--headless')

    driver = Chrome(options=options)

    return driver
