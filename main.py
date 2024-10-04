import telebot
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

BOT_TOKEN = '7466687296:AAFL4UVfoAAxxvzDC90WkBU8b1RcM3WFURk'
bot = telebot.TeleBot(BOT_TOKEN)

logging.basicConfig(level=logging.DEBUG)

@bot.message_handler(commands=['start'])
def start(message):
    logging.debug("Start command received.")
    try:
        bot.reply_to(message, "Welcome to the LinkedIn Job Application Bot! Please log in using the command /login.")
        logging.debug("Reply sent.")
    except Exception as e:
        logging.error(f"Error in start command: {e}")

@bot.message_handler(commands=['login'])
def login(message):
    bot.reply_to(message, "Please send your LinkedIn credentials in the format: `username:password`.")

@bot.message_handler(content_types=['text'])
def handle_login(message):
    if ':' in message.text:
        credentials = message.text.strip().split(':')
        if len(credentials) != 2:
            bot.reply_to(message, "Invalid format. Please use `username:password`.")
            return
        
        username, password = credentials
        bot.reply_to(message, "Logging in to LinkedIn...")
        try:
            apply_for_linkedin_jobs(username, password)
            bot.reply_to(message, "Job application process completed.")
        except Exception as e:
            logging.error(f"Error applying for LinkedIn jobs: {e}")
            bot.reply_to(message, "An error occurred while applying for jobs.")
    else:
        bot.reply_to(message, "Please provide your credentials in the format: `username:password`.")

def apply_for_linkedin_jobs(username, password):
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.get("https://www.linkedin.com/login")

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "session_key"))).send_keys(username)
        driver.find_element(By.NAME, "session_password").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()

        WebDriverWait(driver, 10).until(EC.url_contains("feed"))

        driver.get("https://www.linkedin.com/jobs/")

        show_all_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@aria-label, 'Show all Top job picks for you')]"))
        )
        show_all_button.click()
        sleep(2)  

  
        job_cards = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.job-card-list__title"))
        )

        for job_card in job_cards:
            try:
               
                easy_apply_button = job_card.find_element(By.XPATH, ".//li[contains(text(), 'Easy Apply')]")
                if easy_apply_button.is_displayed():  
                    easy_apply_button.click()
                    logging.info("Clicked 'Easy Apply' button.")

                  
                    sleep(2)  
                    submit_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and contains(text(), 'Submit')]"))
                    )
                    submit_button.click()

                    logging.info("Applied for job successfully.")
                    sleep(1)  
                else:
                    logging.info("Easy Apply button not visible.")
            except Exception as e:
                logging.info("No 'Easy Apply' button found or an error occurred: " + str(e))
                continue  

        driver.quit()
    except Exception as e:
        logging.error(f"Error applying for LinkedIn jobs: {e}")

if __name__ == "__main__":
    logging.debug("Bot is starting...")
    try:
        bot.polling()
    except Exception as e:
        logging.error(f"Error in polling: {e}")
