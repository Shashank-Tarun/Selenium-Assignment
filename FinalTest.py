import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import requests
from PIL import Image
from io import BytesIO
import time
from translate import Translator
from collections import Counter
import os
from concurrent.futures import ThreadPoolExecutor

# Function to sanitize filenames
def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

# Function to scrape articles on a specific browser and platform
def scrape_articles_on_browser(browser, os_name, os_version):
    username = 'shashankmuthyala_eG3pOm'
    access_key = 'raq9aN4zUTiTeTf2cYqL'

    # BrowserStack Options
    chrome_options = ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    desired_capabilities = {
        'browser': browser,
        'browser_version': 'latest',
        'os': os_name,
        'os_version': os_version,
        'name': f'Tech Test {browser}-{os_name}',  # Test name
        'build': 'Technical Assignment',  # Build name
    }

    # Merge options and capabilities
    capabilities = chrome_options.to_capabilities()
    capabilities.update(desired_capabilities)

    # Initialize WebDriver for BrowserStack
    driver = webdriver.Remote(
        command_executor=f'https://{username}:{access_key}@hub-cloud.browserstack.com/wd/hub',
        options=chrome_options
    )

    article_data = []
    try:
        # Navigate to El País
        driver.get("https://elpais.com")
        time.sleep(5)

        # Handle cookie consent
        try:
            consent_button = driver.find_element(By.ID, "didomi-notice-agree-button")
            consent_button.click()
        except Exception:
            print("No consent button found or already accepted.")

        # Navigate to the "Opinión" section
        opinion_link = driver.find_element(By.XPATH, '//a[contains(text(), "Opinión")]')
        opinion_link.click()
        time.sleep(5)

        # Fetch the first five articles
        articles = driver.find_elements(By.CSS_SELECTOR, "article")[:5]

        for article in articles:
            try:
                title = article.find_element(By.TAG_NAME, "h2").text
                content = article.find_element(By.TAG_NAME, "p").text
                image_url = article.find_element(By.TAG_NAME, "img").get_attribute("src") if article.find_elements(By.TAG_NAME, "img") else None

                # Download image if available
                if image_url:
                    response = requests.get(image_url)
                    img = Image.open(BytesIO(response.content))
                    img_filename = f"{sanitize_filename(title)}.jpg"
                    img.save(img_filename)

                article_data.append({"title": title, "content": content})
            except Exception as e:
                print(f"Error processing an article: {e}")
    finally:
        driver.quit()

    return article_data

# Function to translate text to English
def translate_text(text):
    translator = Translator(from_lang="es", to_lang="en")
    try:
        return translator.translate(text)
    except Exception as e:
        print(f"Error translating text: {e}")
        return text

# Main execution with parallel threads
if __name__ == "__main__":
    # Define browser configurations for parallel execution
    browser_configs = [
    {"browser": "Chrome", "os": "OS X", "os_version": "Ventura"},  # Updated OS
    {"browser": "Chrome", "os": "Windows", "os_version": "11"},       # Compatible iOS version
    {"browser": "Firefox", "os": "Windows", "os_version": "11"},
    {"browser": "Edge", "os": "Windows", "os_version": "11"},     # Changed to Edge for variety
    {"browser": "Safari", "os": "OS X", "os_version": "Monterey"} # Valid OS X version
    ]

    all_articles = []

    # Use ThreadPoolExecutor for parallel execution
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(
                scrape_articles_on_browser,
                config["browser"],
                config["os"],
                config["os_version"]
            )
            for config in browser_configs
        ]
        for future in futures:
            all_articles.extend(future.result())

    
    
    unique_articles = {f"{article['title']}|{article['content']}": article for article in all_articles}.values()
    
    translated_titles = []
    
    for article in unique_articles:
        try:
            translated_title = translate_text(article['title'])
            translated_titles.append(translated_title)
            
            print(f"Original Title: {article['title']}")
            print(f"Translated Title: {translated_title}")
            print(f"Content: {article['content']}\n")
            
        except Exception as e:
            print(f"Error during translation or output: {e}")

    # Count repeated words
    all_titles = ' '.join(translated_titles).lower().split()
    
    word_counts = Counter(all_titles)
    print(f"word_count:{word_counts}")
    
    repeated_words = {word: count for word, count in word_counts.items() if count > 2}

    print("Words repeated more than twice in titles:")
    if repeated_words:
        for word, count in repeated_words.items():
            print(f"{word}: {count}")
    else:
        print("No words repeated more than twice.")
