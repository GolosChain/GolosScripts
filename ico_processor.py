#!/usr/bin/env python
from blockcypher import get_address_full, from_satoshis, get_total_num_transactions
import requests
import json
import pymssql
import time
import xlsxwriter
import pytz, datetime
import traceback, logging
UTC_TZ = pytz.utc

def check_bonus(received):
    return {
                                                                 received < datetime.datetime(2016, 11, 1, 11, 0, tzinfo=UTC_TZ):  0.00,
        datetime.datetime(2016, 11, 1, 11, 0, tzinfo=UTC_TZ)  <= received < datetime.datetime(2016, 11, 15, 11, 0, tzinfo=UTC_TZ): 1.25,
        datetime.datetime(2016, 11, 15, 11, 0, tzinfo=UTC_TZ) <= received < datetime.datetime(2016, 11, 18, 11, 0, tzinfo=UTC_TZ): 1.20,
        datetime.datetime(2016, 11, 18, 11, 0, tzinfo=UTC_TZ) <= received < datetime.datetime(2016, 11, 21, 11, 0, tzinfo=UTC_TZ): 1.15,
        datetime.datetime(2016, 11, 21, 11, 0, tzinfo=UTC_TZ) <= received < datetime.datetime(2016, 11, 24, 11, 0, tzinfo=UTC_TZ): 1.10,
        datetime.datetime(2016, 11, 24, 11, 0, tzinfo=UTC_TZ) <= received < datetime.datetime(2016, 11, 27, 11, 0, tzinfo=UTC_TZ): 1.05,
        datetime.datetime(2016, 11, 27, 11, 0, tzinfo=UTC_TZ) <= received                                                        : 1.00
    }[1.0]

config  = json.load(open('blockcypher.json'))
api_key = config["api_key"]
ico_list = {}
ico_list_exception = {}
processed_accounts = 0
processed_txs = 0
total_amount = 0.0
total_normalized_amount = 0.0
total_token_amount = 27072000.0

ico_workbook = xlsxwriter.Workbook('ico_list.xlsx')
ico_worksheet = ico_workbook.add_worksheet()
ico_worksheet.write(0, 0, "Account")
ico_worksheet.write(0, 1, "Account address")
ico_worksheet.write(0, 2, "Account total transactions")
ico_worksheet.write(0, 3, "Account amount")
ico_worksheet.write(0, 4, "Account normalized account")
ico_worksheet.write(0, 5, "Weight")
ico_worksheet.write(0, 6, "Tokens")
ico_worksheet.write(0, 7, "Transactions description")
ico_worksheet.set_column('A:H', 35)

conn = pymssql.connect(server="sql.golos.cloud", port=1433, user="golos", password="golos", database="DBGolos")
cursor = conn.cursor()
cursor.execute("SELECT name, json_metadata FROM accounts WHERE CHARINDEX('ico_address', json_metadata) > 0;")
row = cursor.fetchone()

try:
    print("[-] Started accounts investments processing")
    while row:
        account = row[0]
        account_address = json.loads(json.loads(row[1]))["ico_address"]
        account_amount = 0.0
        account_normalized_amount = 0.0
        account_total_transactions = 0
        txs = []
        response = requests.get("https://chain.so/api/v2/get_address_received/BTC/"+str(account_address))
        if response.status_code == 200:
            content = response.json()
        if response.status_code == 404 or content['data']['unconfirmed_received_value'] == '0.00000000':
            print("[!] Processed zero investments account which registered ico address")
            row = cursor.fetchone()
            time.sleep(1)
            continue
        address_details = get_address_full(address=account_address, api_key=api_key)
        if len(address_details['txs']) == 0:
            row = cursor.fetchone()
            continue
        for tx in address_details['txs']:
            if  tx['outputs'][0]['addresses'][0] == '3CWicRKHQqcj1N6fT1pC9J3hUzHw1KyPv3':
                amount = round(float(from_satoshis(tx['inputs'][0]['output_value'], 'btc')), 4)
                normalized_amount = round(float(amount * check_bonus(tx['received'])), 4)
                current_tx = {
                    "hash": tx['hash'],
                    "amount": amount,
                    "date": tx['received'],
                    "normalized_amount": normalized_amount
                }
                account_total_transactions += 1
                account_amount += amount
                account_amount = round(account_amount, 4)
                account_normalized_amount += normalized_amount
                account_normalized_amount = round(account_normalized_amount, 4)
                txs.append(current_tx)
        processed_txs += account_total_transactions
        total_amount += account_amount
        total_normalized_amount += account_normalized_amount
        ico_list[account] = {
            "address": account_address,
            "transactions": txs,
            "total_transactions": account_total_transactions,
            "amount": account_amount,
            "normalized_amount": account_normalized_amount
        }
        processed_accounts += 1
        print("[{0}] Checked investor @{1}: [tx: {2}, v: {3}, nv: {4}]".format(processed_accounts, account, account_total_transactions, account_amount, account_normalized_amount))
        ico_worksheet.write(processed_accounts, 0, str(account))
        ico_worksheet.write(processed_accounts, 1, str(account_address))
        ico_worksheet.write(processed_accounts, 2, str(account_total_transactions))
        ico_worksheet.write(processed_accounts, 3, str(account_amount))
        ico_worksheet.write(processed_accounts, 4, str(account_normalized_amount))
        ico_worksheet.write(processed_accounts, 7, str(txs))
        row = cursor.fetchone()

        ico_list_exception = ico_list
        time.sleep(1)
    print("[+] Finished accounts investments processing")

    processed_accounts = 0
    print("[-] Started weights processing for investors")
    for account in ico_list:
        processed_accounts +=1
        weight = round(float(ico_list[account]["normalized_amount"])/total_normalized_amount, 12)
        ico_list[account]["weight"] = weight
        tokens = round(total_token_amount * weight, 3)
        ico_list[account]["tokens"] = tokens
        ico_worksheet.write(processed_accounts, 5, str(weight))
        ico_worksheet.write(processed_accounts, 6, str(tokens))
    print("[+] Finished weights processing for investors")
except KeyboardInterrupt as e:
    print("[!] Raised keyboard interrupt, going to save progress...")
    with open('ico_list_exception.json', 'w') as outfile:
        json.dump(ico_list_exception, outfile, indent=4, sort_keys=True, separators=(',', ':'), default=lambda x:str(x))
    print("[!] Saved progress after keyboard interrupt")
    raise
except Exception as e:
    print("[!] Raised unrecognized error, going to save progress...")
    logging.error(traceback.format_exc())
    with open('ico_list_exception.json', 'w') as outfile:
        json.dump(ico_list_exception, outfile, indent=4, sort_keys=True, separators=(',', ':'), default=lambda x:str(x))
    print("[!] Saved progress with error")
else:
    with open('ico_list.json', 'w') as outfile:
        json.dump(ico_list, outfile, indent=4, sort_keys=True, separators=(',', ':'), default=lambda x:str(x))
    print('[*] Raised: {0}'.format(total_amount))
    print('[*] Raised (normalized): {0}'.format(total_normalized_amount))
    print('[*] Total number of investors: {0}'.format(processed_accounts))
    print('[*] Total number of transactions: {0}'.format(processed_txs))
finally:
    ico_workbook.close()
    print("[*] Script finished")
