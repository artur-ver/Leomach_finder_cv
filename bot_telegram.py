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

import telebot
from telebot import types

load_dotenv()

bot = telebot.TeleBot(os.getenv('TOKEN'))

#here is my phone number
users_lst = {1375997606: {'phone_number': '+380965645879', 'cv_to_find': ['human']}}

main_keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
button_under = types.KeyboardButton(text='Parameters 😊')
button_under2 = types.KeyboardButton(text='Find person 🕵️‍♂️')
button_under3 = types.KeyboardButton(text='Show my params 📋')
main_keyboard.add(button_under, button_under2, button_under3)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, text='🚀 You can start 🚀', reply_markup=main_keyboard)


def main(message):
    options = webdriver.ChromeOptions()
    options.add_argument('--incognito')
    # options.add_argument('--headless')
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

    WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located(('xpath', '//*[@id="auth-qr-form"]/div/button[1]')))
    time.sleep(3)
    login_by_phone_number = driver.find_element('xpath', '//*[@id="auth-qr-form"]/div/button[1]')
    login_by_phone_number.click()

    WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located(('xpath', '//*[@id="sign-in-phone-number"]')))
    phone_number = driver.find_element('xpath', '//*[@id="sign-in-phone-number"]')
    time.sleep(1)
    phone_number.clear()
    phone_number.send_keys(users_lst[message.chat.id]['phone_number'])

    next_button = driver.find_element('xpath', '//*[@id="auth-phone-number-form"]/div/form/button[1]/div')
    next_button.click()

    kb = types.ReplyKeyboardMarkup(row_width=2)
    button1 = types.KeyboardButton(text='Code was not sent')
    kb.add(button1)
    code = bot.send_message(message.chat.id, '🔑 Print your code which was sent to Telegram 🔑\n\n'
                                             'AND APPEND IN THE END 1 RANDOM NUMBER\n\n'
                                             'Example: 777776 (6 was appended), 111112 (2 was appended)\n\n'
                                             'If the code was not sent, click this button /send_code_again',
                            reply_markup=kb)

    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(('xpath', '//*[@id="auth-qr-form"]/div/button[1]')))
        if login_by_phone_number:
            login_by_phone_number.click()
            time.sleep(3)
            next_button.click()
    except Exception:
        pass

    bot.register_next_step_handler(code, lambda msg: cont(driver, msg.text, message))


def cont(driver, code, message):
    print(len(message.text))
    if len(message.text) == 6:
        code_field = driver.find_element('xpath', '//*[@id="sign-in-code"]')
        code_field.send_keys(code[0:5])
        '''1'''
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located(('xpath', '//*[@id="telegram-search-input"]')))

        search_channel = driver.find_element('xpath', '//*[@id="telegram-search-input"]')
        search_channel.send_keys('@leomatchbot')

        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located(('css selector', '.ChatInfo')))

        channel_button = driver.find_element('css selector', '.ChatInfo')
        channel_button.click()

        inside_chat(message, driver)
        time.sleep(120)
    else:
        bot.send_message(message.chat.id, "<b>You didn't append some symbol at the end of your message</b>\n"
                                          "You can try again by pressing the 'Find person' button", parse_mode='html')
        driver.close()


def inside_chat(message, driver):
    flag_to_stop = False
    WebDriverWait(driver, 20).until(
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
                cv_text = cv.find_element('css selector', '.text-content.clearfix.with-meta').text.lower().replace('\n',
                                                                                                                   ' ')
                for nickname in users_lst[message.chat.id]['cv_to_find']:
                    if nickname.lower() in cv_text:
                        print(cv_text)
                        print('we found')
                        flag_to_stop = True
                        decide = input('continue: yes/no')
                        if decide == 'yes':
                            send_message.send_keys('3\n')
                            flag_to_stop = False
                        break

                    elif 'нет такого варианта ответа' in cv_text:
                        print(cv_text, 'program needs to write /myprofile')
                        send_message.send_keys('Отмена\n')
                        time.sleep(5)
                        send_message.send_keys('1\n')
                        break

                    elif 'прикрепи к сообщению фото или видео до 15 секунд' in cv_text:
                        print(cv_text, 'program needs to write /myprofile')
                        send_message.send_keys('Вернуться назад\n')
                        time.sleep(5)
                        send_message.send_keys('1\n')
                        break

                    else:
                        print(cv_text)
                        send_message.send_keys('3\n')
                        break

            except Exception:
                print('wrong')
                send_message.send_keys('3\n')


@bot.message_handler(commands=['send_code_again'])
def send_code_again(message):
    main(message)


@bot.message_handler(content_types=['text'])
def text(message):

    if message.text == 'Parameters 😊':
        kb = types.InlineKeyboardMarkup(row_width=2)
        button_change = types.InlineKeyboardButton('CV to find', callback_data='cv_query')
        button_skip = types.InlineKeyboardButton("Phone number", callback_data='phone_query')
        kb.add(button_change, button_skip)
        bot.send_message(message.chat.id, 'What do you want to change?', reply_markup=kb)

    elif message.text == 'Find person 🕵️‍':
        if message.chat.id in users_lst and users_lst[message.chat.id]['cv_to_find']:
            bot.send_message(message.chat.id, f'We will start finding your person: {','.join(users_lst[message.chat.id]['cv_to_find'])}')
            main(message)
        else:
            bot.send_message(message.chat.id, 'You have no CV to find')

    elif message.text == 'Show my params 📋':
        bot.send_message(message.chat.id, f'Phone number: {users_lst[message.chat.id]['phone_number']}\n'
                                            f'Name person in CV: {'\n'.join(users_lst[message.chat.id]['cv_to_find'])}')


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "phone_query":
        phone_append_variable = bot.send_message(call.message.chat.id, 'Send your new phone number')
        bot.register_next_step_handler(phone_append_variable, phone_append)

    elif call.data == 'cv_query':
        kb = types.InlineKeyboardMarkup(row_width=2)
        button1 = types.InlineKeyboardButton('Delete', callback_data='delete_cv')
        button2 = types.InlineKeyboardButton("Append", callback_data='append_cv')
        kb.add(button1, button2)
        bot.send_message(call.message.chat.id, 'Delete or append CV?', reply_markup=kb)

    elif call.data == 'append_cv':
        cv_append_variable = bot.send_message(call.message.chat.id, 'Send the name of the CV you want to find')
        bot.register_next_step_handler(cv_append_variable, cv_append)

    elif call.data == 'delete_cv':
        kb = types.InlineKeyboardMarkup(row_width=2)
        for cv in users_lst[call.message.chat.id]['cv_to_find']:
            personal_button = types.InlineKeyboardButton(f'{cv}', callback_data=f'delete_cv{cv}')
            kb.add(personal_button)
        bot.send_message(call.message.chat.id, 'Choose the CV to delete', reply_markup=kb)

    for cv in users_lst[call.message.chat.id]['cv_to_find']:
        if call.data == f'delete_cv{cv}':
            users_lst[call.message.chat.id]['cv_to_find'].remove(cv)
            bot.send_message(call.message.chat.id, f'CV "{cv}" was deleted')


def cv_append(message):
    users_lst[message.chat.id]['cv_to_find'].append(message.text)
    bot.send_message(message.chat.id, f'We appended the user "{message.text}" in the list of users you want to find')


def phone_append(message):
    try:
        if int(message.text):
            if '+' in message.text:
                users_lst[message.chat.id]['phone_number'] = message.text
                bot.send_message(message.chat.id, f'We changed your phone number to {message.text}')
            else:
                users_lst[message.chat.id]['phone_number'] = '+' + message.text
                bot.send_message(message.chat.id, f'We changed your phone number to +{message.text}')
    except ValueError:
        bot.send_message(message.chat.id, 'You provided an incorrect phone number')


bot.polling(none_stop=True)
