from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")  # Run Chrome in headless mode
driver = webdriver.Chrome()

# Step 2: Open Twitter login page
url = "https://twitter.com/login"
driver.get(url)

# Wait for the page to load
time.sleep(5)

# Step 3: Log in to Twitter
try:
    username_input = driver.find_element(By.NAME, "text")
    username_input.send_keys("username")
    username_input.send_keys(Keys.RETURN)

    time.sleep(2)  # Wait for the password field to appear

    password_input = driver.find_element(By.NAME, "password")
    password_input.send_keys("passowrd")
    password_input.send_keys(Keys.RETURN)

    time.sleep(5)  # Wait for the main page to load
except Exception as e:
    print(f"Login failed: {e}")
    driver.quit()
    exit()

# Step 4: Open Elon Musk's Twitter page
elon_url = "https://twitter.com/elonmusk"
driver.get(elon_url)

# Wait for the page to load
time.sleep(5)

# Step 5: Scroll to load more tweets (Optional: Repeat for more tweets)
scroll_pause_time = 2
for _ in range(3):  # Adjust the range to control how many scrolls to make
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_pause_time)

# Step 6: Parse the loaded page with BeautifulSoup
soup = BeautifulSoup(driver.page_source, "html.parser")

# Step 7: Extract tweet text
tweets = soup.find_all("div", {"data-testid": "tweet"})

for tweet in tweets:
    try:
        text = tweet.find("div", {"lang": True}).text  # Extract tweet text
        print(f"Tweet: {text}")
        print("-" * 50)
    except AttributeError:
        continue  # Skip if no text is found

# Step 8: Close the browser
driver.quit()
