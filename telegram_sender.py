import urllib.request

import requests


def send_to_telegram(content: dict):
    message = format_2_sms(content)
    apiToken = 'xxx'
    chatID = 'xxx'
    apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'

    try:
        response = requests.post(apiURL, json={'chat_id': chatID, 'text': message})
        print(response.text)
    except Exception as e:
        print(e)


def format_2_sms(content: str):
    sms = 'Badminton court available:\n-----\n'
    for available_hour in content:
        sms += available_hour['date'] + '\n' + str(available_hour['available_hours']) + '\n'
        sms += '-----\n'
    return sms
