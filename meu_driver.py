from selenium.webdriver import Firefox, FirefoxOptions


def load_driver():
    """
    Loads and returns a selenium webdriver driver with specified options.

    Returns:
        driver: The driver with specified options.
    """
    options = FirefoxOptions()
    options.add_argument('--incognito')
    options.add_argument('--headless')

    driver = Firefox(options=options)

    return driver
