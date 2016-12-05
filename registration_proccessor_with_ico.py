#!/usr/bin/env python3
from blockcypher import create_forwarding_address_with_details
import json
from random import choice
import xlsxwriter
import time
import traceback, logging
from piston.steem import (
    Steem,
    AccountExistsException,
    BroadcastingError
)

config  = json.load(open('config.json'))
creator = config["registory"]
wif     = config["wif"]
steem   = Steem(node='ws://127.0.0.1:8090', nobroadcast=False, wif=wif)

workbook_name = 'acccounts_list_ico_' + str(int(time.time())) + '.xlsx'
ico_workbook = xlsxwriter.Workbook(workbook_name)
ico_worksheet = ico_workbook.add_worksheet()
ico_worksheet.write(0, 0, "Account name")
ico_worksheet.write(0, 1, "Status")
ico_worksheet.write(0, 2, "Account password")
ico_worksheet.write(0, 3, "Account ico address")
ico_worksheet.set_column('A:F', 35)

blockcypher  = json.load(open('blockcypher.json'))
api_key = blockcypher["api_key"]

registration_list   = json.load(open('registration_list_ico.json'))
# registration_list   = json.load(open('step_four_pre_registration_list.json'))
logs                = []
registered_list     = []
non_registered_list = []

logs_exception                = []
registered_list_exception     = []
non_registered_list_exception = []

processed_accounts = 0

charsets = [
    'abcdefghijklmnopqrstuvwxyz',
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    '0123456789',
    ]

def generate_password(length=32):
    pwd = []
    charset = choice(charsets)
    while len(pwd) < length:
        pwd.append(choice(charset))
        charset = choice(list(set(charsets) - set([charset])))
    return "".join(pwd)

try:
    print("[-] Started accounts process creation")
    for account in registration_list:
        processed_accounts += 1
        account_address = create_forwarding_address_with_details(destination_address='3CWicRKHQqcj1N6fT1pC9J3hUzHw1KyPv3',
                                                                 api_key=api_key,
                                                                 callback_url='')
        account_address = account_address['input_address']
        metadata = {"ico_address":str(account_address), "type":"b"}
        random_string = generate_password(32)
        try:
            registration_log = steem.create_account(account_name=account,
                                                    json_meta=metadata,
                                                    creator=creator,
                                                    password=random_string,
                                                    storekeys=False)
            created_account = {
                'account'    : account,
                'password'   : random_string,
                'address'    : account_address
            }

            logs.append(registration_log)
            registered_list.append(created_account)

            ico_worksheet.write(processed_accounts, 0, str(account))
            ico_worksheet.write(processed_accounts, 1, str("Created"))
            ico_worksheet.write(processed_accounts, 2, str(random_string))
            ico_worksheet.write(processed_accounts, 3, str(account_address))

            registered_list_exception = registered_list
            logs_exception = logs

            print('[+][{3}] Successfully registered account: {0} [{2}] with password -> {1}'.format(account, random_string, account_address, processed_accounts))
        except AccountExistsException:
            non_registered_list.append(account)

            print('[-][{1}] Already registered account: {0}'.format(account, processed_accounts))

            ico_worksheet.write(processed_accounts, 0, str(account))
            ico_worksheet.write(processed_accounts, 1, str("Not created [exists]"))

            non_registered_list_exception = non_registered_list
            time.sleep(2)
            pass
        except BroadcastingError:
            non_registered_list.append(account)

            print('[-][{1}] Account name: {0} is invalid'.format(account, processed_accounts))

            ico_worksheet.write(processed_accounts, 0, str(account))
            ico_worksheet.write(processed_accounts, 1, str("Not created [invalid]"))

            non_registered_list_exception = non_registered_list
            pass
except KeyboardInterrupt as e:
    print("[!] Raised keyboard interrupt, going to save progress...")

    json.dump(logs_exception, open('registration_logs_ico_' + str(int(time.time())) + '.json', 'w'),
                                                                        indent=4,
                                                                        sort_keys=True,
                                                                        separators=(',', ':'))
    json.dump(registered_list, open('registered_accounts_credentials_ico_' + str(int(time.time())) + '.json', 'w'),
                                                                        indent=4,
                                                                        sort_keys=True,
                                                                        separators=(',', ':'))
    json.dump(non_registered_list, open('non_registered_accounts_list_ico_' + str(int(time.time())) + '.json', 'w'),
                                                                        indent=4,
                                                                        sort_keys=True,
                                                                        separators=(',', ':'))
    print("[!] Saved progress after keyboard interrupt")
    raise
except Exception as e:
    print("[!] Raised unrecognized error, going to save progress...")

    logging.error(traceback.format_exc())
    json.dump(logs_exception, open('registration_logs_ico_' + str(int(time.time())) + '.json', 'w'),
                                                                        indent=4,
                                                                        sort_keys=True,
                                                                        separators=(',', ':'))
    json.dump(registered_list_exception, open('registered_accounts_credentials_ico_' + str(int(time.time())) + '.json', 'w'),
                                                                        indent=4,
                                                                        sort_keys=True,
                                                                        separators=(',', ':'))
    json.dump(non_registered_list_exception, open('non_registered_accounts_list_ico_' + str(int(time.time())) + '.json', 'w'),
                                                                        indent=4,
                                                                        sort_keys=True,
                                                                        separators=(',', ':'))
    print("[!] Saved progress with error")
else:
    json.dump(logs, open('registration_logs_ico_' + str(int(time.time())) + '.json', 'w'),
                                                                        indent=4,
                                                                        sort_keys=True,
                                                                        separators=(',', ':'))
    json.dump(registered_list, open('registered_accounts_credentials_ico_' + str(int(time.time())) + '.json', 'w'),
                                                                        indent=4,
                                                                        sort_keys=True,
                                                                        separators=(',', ':'))
    json.dump(non_registered_list, open('non_registered_accounts_list_ico_' + str(int(time.time())) + '.json', 'w'),
                                                                        indent=4,
                                                                        sort_keys=True,
                                                                        separators=(',', ':'))
    print("[-] Finished accounts process creation")
finally:
    ico_workbook.close()
    print("[*] Script finished")
