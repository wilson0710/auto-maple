import requests
import json
import time

REMOTE_SHEET_URL = 'https://script.google.com/macros/s/AKfycbzpGcS0Een8ukM9QMWgWw-3m9ISPc5cWQQXQVmpz7Ao3fYNAiQbZYFzHzpRhPLXWKI4bw/exec'

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