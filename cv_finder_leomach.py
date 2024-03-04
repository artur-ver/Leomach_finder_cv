import time
import os

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium_stealth import stealth
from fake_useragent import UserAgent

from dotenv import load_dotenv

load_dotenv()

options = webdriver.ChromeOptions()
options.add_argument('--incognito')
#options.add_argument('--headless')
options.add_argument(f"--user-agent={UserAgent().random}")
options.add_argument("--disable-blink-features=AutomationControlled")

options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_experimental_option('useAutomationExtension', False)

service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )

driver.get('https://web.telegram.org/a/')

user_phone_number = os.getenv('PHONE_NUMBER')


def main():
    WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located(('xpath', '//*[@id="auth-qr-form"]/div/button[1]')))
    time.sleep(3)
    login_by_phone_number = driver.find_element('xpath', '//*[@id="auth-qr-form"]/div/button[1]')
    login_by_phone_number.click()

    WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located(('xpath', '//*[@id="sign-in-phone-code"]')))

    phone_number = driver.find_element('xpath', '//*[@id="sign-in-phone-number"]')
    time.sleep(1)
    phone_number.clear()
    phone_number.send_keys(user_phone_number)

    next_button = driver.find_element('xpath', '//*[@id="auth-phone-number-form"]/div/form/button[1]/div')
    next_button.click()

    code = input('Print code from telegram')

    code_field = driver.find_element('xpath', '//*[@id="sign-in-code"]')
    code_field.send_keys(code)
    '''1'''
    WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located(('xpath', '//*[@id="telegram-search-input"]')))

    search_chanel = driver.find_element('xpath', '//*[@id="telegram-search-input"]')
    search_chanel.send_keys('@leomatchbot')

    WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located(('css selector', '.ChatInfo')))

    chanel_button = driver.find_element('css selector', '.ChatInfo')
    chanel_button.click()

    inside_chat()
    time.sleep(120)


nicknames = [os.getenv('YOUR_NICKNAME')]    #only_1


def inside_chat():
    flag_to_stop = False
    text_field = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located(('xpath', '//*[@id="editable-message-text"]')))
    send_message = driver.find_element('xpath', '//*[@id="editable-message-text"]')
    send_message.send_keys('/language\n')
    time.sleep(3)
    option_button = driver.find_element('css selector', '.icon.icon-bot-command')
    option_button.click()
    time.sleep(3)
    language_button = driver.find_element('css selector', '.Button.default.primary.has-ripple')
    language_button.click()
    time.sleep(3)
    send_message.send_keys('/myprofile\n')
    time.sleep(3)
    send_message.send_keys('5\n')

    while not flag_to_stop:
        time.sleep(3)
        cv = driver.find_element('css selector', '.last-in-list')
        if cv:
            try:
                cv_text = cv.find_element('css selector', '.text-content.clearfix.with-meta').text.lower().replace('\n', ' ')
                for nickname in nicknames:
                    if nickname.lower() in cv_text in cv_text:
                        print(cv_text)
                        print('we found')
                        flag_to_stop = True
                        decide = input('continue: yes/no')
                        if decide == 'yes':
                            send_message.send_keys('3\n')
                            flag_to_stop = False
                        break

                    elif cv_text == 'нет такого варианта ответа':
                        print(cv_text)
                        send_message.send_keys('/myprofile\n')
                        time.sleep(5)
                        send_message.send_keys('5\n')
                        break

                    else:
                        print(cv_text)
                        send_message.send_keys('3\n')
                        break

            except Exception:
                print('wrong')
                send_message.send_keys('3\n')


if __name__ == '__main__':
    main()
