import datetime
import json
from time import sleep

# pip install https://github.com/algo2t/alphatrade

from alphatrade import AlphaTrade, LiveFeedType
from omspy_brokers.sasonline import Sasonline
from toolkit.fileutils import Fileutils
import pyotp

# import config
# NOTE create a config.py file in the same directory as sas_login_eg.py file
# Contents of the config.py must be as below, config.py is used for storing credentials
#### config.py START ####
# login_id = "RR"
# password = "SAS@131"
# twofa = "rr"

# try:
#     access_token = open('access_token.txt', 'r').read().rstrip()
# except Exception as e:
#     print('Exception occurred :: {}'.format(e))
#     access_token = None
#### config.py END ####

try:
    access_token = open('access_token.txt', 'r').read().rstrip()
except Exception as e:
    print('Exception occurred :: {}'.format(e))
    access_token = None

fpath = "../../../"
cred = Fileutils().get_lst_fm_yml(fpath + "sas.yaml")
pin = pyotp.TOTP(cred['totp']).now()
totp = f"{int(pin):06d}" if len(pin) <= 5 else pin
sas = AlphaTrade(login_id=cred['login_id'],
                 password=cred['password'], twofa=totp, access_token=access_token)
print(vars(sas))

# sas = AlphaTrade(login_id=config.login_id, password=config.password, twofa=config.twofa)

# NOTE access_token can be supplied if already available
# sas = AlphaTrade(login_id=config.login_id, password=config.password,
#                  twofa=config.twofa, access_token=config.access_token)

# NOTE access_token can be supplied if already available and master_contracts to download
# sas = AlphaTrade(login_id=config.login_id, password=config.password,
#                  twofa=config.twofa, access_token=config.access_token, master_contracts_to_download=['CDS'])


print(sas.get_profile())
usd_inr = sas.get_instrument_by_symbol('CDS', 'USDINR APR FUT')
print(usd_inr)
print(sas.get_balance())
