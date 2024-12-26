import os
from dotenv import load_dotenv
import requests
from time import sleep

load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')
TG_API_LINK = f'https://api.telegram.org/bot{BOT_TOKEN}/'
OPENAI_API_LINK = 'https://status.openai.com/api/v2/summary.json'

def main():
    if not test_token():
        print('BOT_TOKEN invalid or does not exist')
        exit(1)
    alreadySent = False
    while True:
        chat_ids = get_chat_ids()
        gptstatus = get_chatgpt_status()
        if gptstatus == 'major_outage': 
            if not alreadySent:
                broadcast(chat_ids, 'Major outage on ChatGPT')
                alreadySent = True
        else:
            alreadySent = False

        sleep(10)


def test_token():
    r = requests.get(TG_API_LINK+'getMe')
    return r.json()['ok']


def broadcast(chat_ids, message):
    for chat_id in chat_ids:
        r = requests.post(TG_API_LINK+'sendMessage', data = {'chat_id':chat_id, 'text':message})
        json = r.json()
        if not json['ok']:
            print('failed to send message to',chat_id)
        #no more than 30 messages/sec
        sleep(1/29)


def get_chat_ids():
    chat_ids = set()
    r = requests.get(TG_API_LINK+'getUpdates')
    updates = r.json()['result']
    for update in updates:
        chat_ids.add(update['message']['chat']['id'])
    return chat_ids


def get_chatgpt_status():
    #major_outage, partial_outage, operational
    r = requests.get(OPENAI_API_LINK)
    components = r.json()['components']
    for component in components:
        if component['name'] == 'ChatGPT':
            return component['status']


main()
