from omspy_brokers.sasonline import Sasonline
from toolkit.fileutils import Fileutils
from toolkit.logger import Logger

fpath = "../../../"

cred = Fileutils().get_lst_fm_yml(fpath + "sas.yaml")
logging = Logger(20)
try:
    sas = Sasonline(cred['login_id'], cred['password'], cred['totp'])
    if sas.authenticate():
        print("\n successfully authenticated")
except Exception as e:
    print(e)
    SystemExit()
