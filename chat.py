# -*- coding: utf-8 -*-

import requests
import json
import random
import time
import re

def gen_context():
    # context_list = [
    #     "hello bro","let's go !","to the moon!","nice","project","have a good day",
    #     "good","luck","how's going","so do i","yeah","same to me","1","cool","so far so good",
    #     "hi~","of course","really","cool~","ok","what?","why?","not bad","well done","great",
    #     "perferct","thanks","ture","yes","no","here","interesting","it's funny","i am tired"
    # ]
    context_list = [
        "lv7太久了》。。","LFG!"
    ]
    text = random.choice(context_list)
    return text

def get_context():
    chanel_list = ['934397710344286252']
    #英文：'934397709799022625'
    #中文： 934397710344286252
    authorization_list = ['//填入你自己的authorid！！！！！！！！！！！！！！']
    headr = {
        "Authorization": authorization_list[0],
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    }
    chanel_id = random.choice(chanel_list)
    url = "https://discord.com/api/v9/channels/{}/messages?limit=100".format(chanel_id)
    res = requests.get(url=url, headers=headr,proxies={'http': 'http://127.0.0.1:10809', 'https': 'http://127.0.0.1:10809'})
    result = json.loads(res.content)
    result_list = []
    for context in result:
        if ('<') not in context['content'] :
            if ('@') not in context['content'] :
                if ('http') not in context['content']:
                    if ('?') not in context['content']:
                        result_list.append(context['content'])

    return random.choice(result_list)


def chat():
    chanel_list = ['934397710344286252']
    #英文：'934397709799022625'
    #中文： 934397710344286252
    authorization_list = ['//填入你自己的authorid！！！！！！！！！！！！！！']

    for authorization in authorization_list:
        header = {
            "Authorization":authorization,
            "Content-Type":"application/json",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"
        }

        for chanel_id in chanel_list:
            msg = {

                "content": get_context(),
                "nonce": "82329451214{}33232234".format(random.randrange(0, 1000)),
                "tts": False

            }
            url = 'https://discord.com/api/v9/channels/{}/messages'.format(chanel_id)

            try:

                res = requests.post(url=url, headers=header, data=json.dumps(msg),proxies={'http': 'http://127.0.0.1:10809', 'https': 'http://127.0.0.1:10809'})
                if res.ok == True:
                    result = json.loads(res.text)
                    url_delete = 'https://discord.com/api/v9/channels/{}/messages/{}'.format(chanel_id, result['id'])
                    requests.delete(url=url_delete, headers=header,
                                    proxies={'http': 'http://127.0.0.1:10809', 'https': 'http://127.0.0.1:10809'})
                print(res.content)
            except:
                pass
            continue
        time.sleep(random.randrange(60,120))
        # time.sleep(120)


if __name__ == '__main__':
    while True:
        try:
            chat()
            # sleeptime = random.randrange(9000, 10000)
            # time.sleep(sleeptime)
        except:
            pass
        continue