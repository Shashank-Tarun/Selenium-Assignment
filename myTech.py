# This is Python-Selenium code
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
from PIL import Image
from io import BytesIO
import time
from translate import Translator
from collections import Counter
import os

#Function to sanitize filenames
def sanitize_filename(filename):
#Remove invalid characters for filenames
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

#Function to scrape articles
def scrape_articles():
    # Initialize the WebDriver
    driver = webdriver.Chrome()

    # Navigate to El País Opinion section
    driver.get("https://elpais.com")
    
    # Handle cookie consent
    try:
        consent_button = driver.find_element(by=By.ID, value="didomi-notice-agree-button")
        time.sleep(5)
        consent_button.click()
    except Exception:
        print("No consent button found or already accepted.")
    
    # Navigate to the "Opinion" section
    opinion_link = driver.find_element(By.XPATH, '//a[contains(text(), "Opinión")]')
    opinion_link.click()
    time.sleep(5)

    # Fetch the first five articles
    articles = driver.find_elements(By.CSS_SELECTOR, "article")[:5]

    # Initialize a list to store article data
    article_data = []

    for article in articles:
        try:
            title = article.find_element(By.TAG_NAME, "h2").text
            content = article.find_element(By.TAG_NAME, "p").text
            image_url = article.find_element(By.TAG_NAME, "img").get_attribute("src") if article.find_elements(By.TAG_NAME, "img") else None
            
            # Download the image if available
            if image_url:
                response = requests.get(image_url)
                img = Image.open(BytesIO(response.content))
                img_filename = f"{sanitize_filename(title)}.jpg"
                img.save(img_filename)
                print(f"Saved image: {img_filename}")  # Print confirmation of saved image

          
            article_data.append({"title": title, "content": content})
        except Exception as e:
            print(f"Error processing an article: {e}")

    # Close the WebDriver
    driver.quit()
    
    return article_data

# Function to translate text to English
def translate_text(text):
    translator = Translator(from_lang="es", to_lang="en")
    try:
        return translator.translate(text)
    except Exception as e:
        print(f"Error translating text: {e}")
        return text  # Return original text if translation fails

# Main execution
if __name__ == "__main__":
    # Scrape articles
    article_data = scrape_articles()

    translated_titles = []
    
    # Translate titles and print the articles
    for article in article_data:
        try:
            translated_title = translate_text(article['title'])
            translated_titles.append(translated_title)
          # print(f"translated Titles: {translated_titles}")           
            print(f"Original Title: {article['title']}")
            print(f"Content: {article['content']}\n")
            print("The cover image of each article is stored in this path:", os.getcwd())
            print(f"Translated Title: {translated_title}")

        except Exception as e:
            print(f"Error during translation or output: {e}")
    
    all_titles = ' '.join(translated_titles).lower().split()
  
    word_counts = Counter(all_titles)
    print(f"word counts :{word_counts}")
    
    repeated_words = {word: count for word, count in word_counts.items() if count > 2}
    
    print("Words repeated more than twice in titles:")
    if repeated_words:
        for word, count in repeated_words.items():
            print(f"{word}: {count}")
    else:
        print("No words repeated more than twice.")
    
