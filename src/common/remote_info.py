import asyncio
import requests
import time
import json
from src.common import config

REMOTE_SHEET_URL = 'https://script.google.com/macros/s/AKfycbzpGcS0Een8ukM9QMWgWw-3m9ISPc5cWQQXQVmpz7Ao3fYNAiQbZYFzHzpRhPLXWKI4bw/exec'

def run_async(callback):
    def inner(func):
        def wrapper(*args, **kwargs):
            def __exec():
                out = func(*args, **kwargs)
                callback(out)
                return out

            return asyncio.get_event_loop().run_in_executor(None, __exec)

        return wrapper

    return inner


def _callback(*args):
    print(str(args[0][0]))
    config.remote_infos[str(args[0][0])] = args[0]
    print(config.remote_infos[str(args[0][0])])

# Must provide a callback function, callback func will be executed after the func completes execution !!
@run_async(_callback)
def get_remote_async(id):
    config.remote_infos[str(id)] = None
    return get_user_info(id)

def wait_for_get(id):
    while True:
        if config.remote_infos[str(id)]:
            return config.remote_infos[str(id)]
        time.sleep(0.1)

def get_user_info(id):
    """
    get user info from remote google sheet.
    :param id:   target user id.
    :return:     list:[id,current_map,channel,status,daily,lastest_online_time] .
    """
    params = {
        'game': 'TMS',
        'mission': 'accManage',
        'prefix': id,
        'json': '[]'
    }

    r = requests.get(REMOTE_SHEET_URL, params = params)
    try:
        content = json.loads(r.content)
        print("succeed, result : ",content['result'])
        return content['result']
    except:
        print("retry remote info")
        time.sleep(1)
        return get_user_info(id)

@run_async(_callback)
def update_remote_async(id,info):
    return update_user_info(id,info)

def update_user_info(id,info):
    """
    get user info from remote google sheet.
    :param id:   target user id.
    :param info:   updated info,same spec as get_user_info return.
    :return:     list:[id,current_map,channel,status,daily,lastest_online_time] .
    """
    params = {
        'game': 'TMS',
        'mission': 'accManage',
        'prefix': id,
        'json': json.dumps(info)
    }
    
    r = requests.get(REMOTE_SHEET_URL, params = params)
    try:
        content = json.loads(r.content)
        print("succeed, result : ",content['result'])
        return content['result']
    except:
        print("retry remote info")
        time.sleep(1)
        return update_user_info(id,info)

# asyncio.get_event_loop().run_in_executor(None, __exec)
# get_remote_async("ewei")
# print('wait : ',wait_for_get('ewei'))
# print("Non blocking code ran !!")