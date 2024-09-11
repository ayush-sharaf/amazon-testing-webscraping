import time
import os
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import test2 as config

def amazon_login(driver):
    driver.get(config.AMAZON_URL)
    time.sleep(random.uniform(2, 4))
    sign_in_button = driver.find_element(By.ID, 'nav-link-accountList')
    sign_in_button.click()
    time.sleep(2)
    email_input = driver.find_element(By.CLASS_NAME, 'a-input-text')
    email_input.send_keys(config.EMAIL)
    time.sleep(random.uniform(1, 3))
    email_input.send_keys(Keys.RETURN)
    time.sleep(random.uniform(2, 4))
    password_input = driver.find_element(By.ID, 'ap_password')
    password_input.send_keys(config.PASSWORD)
    time.sleep(random.uniform(1, 3))
    password_input.send_keys(Keys.RETURN)
    time.sleep(random.uniform(2, 4))
    try:
        account_name = driver.find_element(By.ID, 'nav-link-accountList-nav-line-1')
        print(f"Login successful! Logged in as: {account_name.text}")
        return True
    except Exception as e:
        print(f"Login failed. Please check your credentials.")
        return False

def amazon_logout(driver):
    try:
        account_list = driver.find_element(By.ID, 'nav-link-accountList')
        action = ActionChains(driver)
        action.move_to_element(account_list).perform()
        time.sleep(random.uniform(2, 4))
        sign_out_button = driver.find_element(By.XPATH, "//span[text()='Sign Out']")
        sign_out_button.click()
        print("Logout successful!")
    except Exception as e:
        print(f"Logout failed. Error: {e}")

def extract_product_info(driver, query):
    if not os.path.exists('data'):
        os.makedirs('data')
    file = 0
    for i in range(1, 3):  # Adjust range for more pages if needed
        driver.get(f"https://www.amazon.in/s?k={query}&page={i}")
        time.sleep(random.uniform(3, 6))
        elems = driver.find_elements(By.XPATH, "//div[@data-component-type='s-search-result']")
        print(f"{len(elems)} items found on page {i}")
        for elem in elems:
            d = elem.get_attribute("outerHTML")
            with open(f"data/{query}_{file}.html", "w", encoding="utf-8") as f:
                f.write(d)
                file += 1
        time.sleep(random.uniform(2, 4))

def parse_html_and_save_to_csv():
    d = {'title': [], 'price': [], 'link': []}
    for file in os.listdir("data"):
        try:
            with open(f"data/{file}", encoding='utf-8') as f:
                html_doc = f.read()
            soup = BeautifulSoup(html_doc, 'html.parser')
            t = soup.find("span", {"class": "a-size-medium a-color-base a-text-normal"})
            title = t.get_text() if t else "N/A"
            l = t.find_parent("a") if t else None
            link = "https://www.amazon.in" + l['href'] if l else "N/A"
            p = soup.find("span", attrs={"class": "a-price-whole"})
            price = p.get_text() if p else "N/A"
            print(title, price, link, end="\n")
            d['title'].append(title)
            d['price'].append(price)
            d['link'].append(link)
        except Exception as e:
            print(e)
    pd.DataFrame(data=d).to_csv("data.csv", index=False)

def main():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    # Path to the manually downloaded chromedriver
    chromedriver_path = 'chromedriver-mac-arm64/chromedriver'
    driver = webdriver.Chrome(service=Service(chromedriver_path), options=options)
    try:
        if amazon_login(driver):
            extract_product_info(driver, config.QUERY)
            parse_html_and_save_to_csv()
            amazon_logout(driver)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
