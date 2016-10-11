#!/usr/bin/env python3
import json
from time import time
from random import choice
from piston.steem import (
    Steem,
    AccountExistsException,
    BroadcastingError
)

config  = json.load(open('config.json'))
creator = config["registory"]
wif     = config["wif"]
steem   = Steem(node='ws://127.0.0.1:8090', nobroadcast=False, wif=wif)

registration_list   = json.load(open('step_one_init_registration_list.json'))
# registration_list   = json.load(open('step_four_pre_registration_list.json'))
logs                = []
registered_list     = []
non_registered_list = []

charsets = [
    'abcdefghijklmnopqrstuvwxyz',
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    '0123456789',
    '^!\$%&/()=?{[]}+~#-_.:,;<>|\\',
    ]

def generate_password(length=32):
    pwd = []
    charset = choice(charsets)
    while len(pwd) < length:
        pwd.append(choice(charset))
        charset = choice(list(set(charsets) - set([charset])))
    return "".join(pwd)

for account in registration_list:
    try:
        random_string = generate_password(32)
        registration_log = steem.create_account(account_name=account,
                                                creator=creator,
                                                password=random_string,
                                                storekeys=False)
        created_account = {
            'account'    : account,
            'password'   : random_string
        }
        logs.append(registration_log)
        registered_list.append(created_account)
        print('[+] Successfully registered account: {0} with password -> {1} '.format(account, random_string))
    except AccountExistsException:
        non_registered_list.append(account)
        print('[-] Already registered account: {0}'.format(account))
        pass
    except BroadcastingError:
        pass

json.dump(logs, open('registration_logs_' + str(int(time())) + '.json', 'w'),
                                                                    indent=4,
                                                                    sort_keys=True,
                                                                    separators=(',', ':'))
json.dump(registered_list, open('registered_accounts_credentials_' + str(int(time())) + '.json', 'w'),
                                                                    indent=4,
                                                                    sort_keys=True,
                                                                    separators=(',', ':'))
json.dump(non_registered_list, open('non_registered_accounts_list_' + str(int(time())) + '.json', 'w'),
                                                                    indent=4,
                                                                    sort_keys=True,
                                                                    separators=(',', ':'))
