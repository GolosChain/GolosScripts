import json
from time import time
from piston.steem import (
    Steem,
    BroadcastingError
)

config  = json.load(open('config.json'))
creator = config["registory"]
wif     = config["wif"]
steem   = Steem(node='ws://127.0.0.1:8090', nobroadcast=False, wif=wif)

transfer_list = json.load(open('./step_three_init_tx_power.json'))
# transfer_list = json.load(open('./step_five_init_tx_power.json'))
# transfer_list = json.load(open('./step_six_sharedrop_tx_power.json'
logs          = []

for index, tx in enumerate(transfer_list):
    try:
        transfer_log = steem.transfer_to_vesting(account=creator,
                                                 amount=tx['amount'],
                                                 to=tx['account'])
        logs.append(transfer_log)
        print ("[+] <{0}> Transfered {1} to {2}".format(index+1, tx['amount'], tx['account']))
    except BroadcastingError:
        print ("[-] <{0}> Didn't transferred {1} to {2}".format(index+1, tx['amount'], tx['account']))
        pass

json.dump(logs, open('golospower_transfer_log_' + str(int(time())) + '.json', 'w'),
                                                                    indent=4,
                                                                    sort_keys=True,
                                                                    separators=(',', ':'))
