from omspy_brokers.sasonline import Sasonline
from toolkit.fileutils import Fileutils
from toolkit.utilities import Utilities
from toolkit.logger import Logger

sl_percentage = 3.0
profit_percentage = 7.0
fpath = "../../../"
logging = Logger(20)


def update_local_file(details):
    # sqlite or json?
    import json
    with open("intermediate.json", "w") as json_file:
        json.dump(details, json_file)


def read_local_json(details):
    # Where will this happen?
    import json
    with open("intermediate.json", ) as json_file:
        return json.load(json_file)


if __name__ == "__main__":
    cred = Fileutils().get_lst_fm_yml(fpath + "sas.yaml")
    try:
        sas = Sasonline(cred['login_id'], cred['password'], cred['totp'])
        if sas.authenticate():
            print("\n successfully authenticated")
    except Exception:
        print("exception .. exiting")
        SystemExit()
    # Post successful authentication
    while True:
        resp = sas.orders
        print(resp)
        # get order numbers for those order for which
        # the order status is complete
        pass
        # order_id | related_order_id | type    ! qty
        # 001      | 002              | entry   | 50
        # 002      | 001              | exit    | -50
        # modify_order("some_params")
        Utilities().slp_til_nxt_sec()
