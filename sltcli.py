"""
Author: Kavishka Gihan Fernando (https://twitter.com/_kavigihan)
Version: 1.0

usage: sltcli.py [-h] [-a] {login,usage,account,bill,logout}

Command Line Tool to fetch usage, bill and account information for SLT users

positional arguments:
  {login,usage,account,bill,logout}
                        Action to perform

options:
  -h, --help            show this help message and exit
  -a, --all             Output all the details in json

"""

import requests
import json
import shutil
import argparse
from pathlib import Path

CONFIG_FILE = Path(Path.home()) / '.sltcli' / 'config.json'
EXAMPLE_CONFIG_FILE = Path(__file__).resolve().parent / 'example_config.json'

def loadConfig(config_file):
    global EXAMPLE_CONFIG_FILE

    if not config_file.exists():
        print(f"{config_file} not found! Copying the example config.")
        config_dir = config_file.parent
        config_dir.mkdir(parents=True, exist_ok=True)

        with open(EXAMPLE_CONFIG_FILE, 'rb') as src, open(config_file, 'wb') as dst:
            shutil.copyfileobj(src, dst)

        print(f"Config copied! Update the credentials before using.")
        exit(1)

    with open(config_file, 'r') as f:
        return json.load(f)

def updateConfig(key_type, key, value):
    data = loadConfig(CONFIG_FILE)

    data[key_type][key] = value

    with open(CONFIG_FILE, "w") as file:
        json.dump(data, file, indent=4)


def loginUser(username, password):
    global CONFIG_FILE
    loginUrl = loadConfig(CONFIG_FILE)["server"]["loginUrl"]
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "X-IBM-Client-Id": "41aed706-8fdf-4b1e-883e-91e44d7f379b",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://myslt.slt.lk",
        "DNT": "1",
        "Connection": "keep-alive",
        "Referer": "https://myslt.slt.lk/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
    }

    data = {
        "username": username,
        "password": password,
        "channelID": "WEB",
    }

    response = requests.post(loginUrl, headers=headers, data=data)
    if response.status_code == 200:
        access_token = json.loads(response.text)["accessToken"]
    else:
        return False

    if access_token:
        updateConfig("authentication", "authorization_header", f"bearer {access_token}")
        return True
    else:
        return False


def getAccountDetails(authorization_header):
    config = loadConfig(CONFIG_FILE)
    AccountDetailsUrl = config["server"]["AccountDetailsUrl"]
    username = config["authentication"]["username"]

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Authorization": authorization_header,
        "X-IBM-Client-Id": "41aed706-8fdf-4b1e-883e-91e44d7f379b",
        "Origin": "https://myslt.slt.lk",
        "Connection": "keep-alive",
        "Referer": "https://myslt.slt.lk/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
    }

    params = {
        "username": username,
    }

    response = requests.get(
        AccountDetailsUrl,
        params=params,
        headers=headers,
    )

    if response.status_code == 200:

        accountno = json.loads(response.text)["dataBundle"][0]["accountno"]
        telephone = json.loads(response.text)["dataBundle"][0]["telephoneno"]
        subscriberID = f"94{telephone[1:]}"

        if telephone and subscriberID:
            updateConfig("account", "accountno", accountno)
            updateConfig("account", "telephone", telephone)
            updateConfig("account", "subscriberID", subscriberID)
            return True, None
        else:
            return False, None
    else:
        return False, None


def getUsageDetails(authorization_header, all_out=False):

    config = loadConfig(CONFIG_FILE)
    UsageDetailsUrl = config["server"]["UsageDetailsUrl"]
    subscriberID = config["account"]["subscriberID"]

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Authorization": authorization_header,
        "X-IBM-Client-Id": "41aed706-8fdf-4b1e-883e-91e44d7f379b",
        "Origin": "https://myslt.slt.lk",
        "Connection": "keep-alive",
        "Referer": "https://myslt.slt.lk/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
    }

    params = {
        "subscriberID": subscriberID,
    }

    response = requests.get(UsageDetailsUrl, params=params, headers=headers)

    if response.status_code == 200:
        data = json.loads(response.text)

        if all_out:
            return data
        else:
            package_name = data["dataBundle"]["my_package_info"]["package_name"]
            output = {}
            output["package_name"] = package_name
            output["bundles"] = []
            for entry in data["dataBundle"]["my_package_info"]["usageDetails"]:
                name = entry["name"]
                limit = entry["limit"]
                used = entry["used"]
                output["bundles"].append({name: f"{used}/{limit}"})
            return output
    else:
        return None, None


def getProfileDetails(authorization_header, all_out=False):

    config = loadConfig(CONFIG_FILE)
    subscriberID = config["account"]["subscriberID"]
    ProfileDetailsUrl = config["server"]["ProfileDetailsUrl"]

    headers = {
        "Host": "omniscapp.slt.lk",
        "Sec-Ch-Ua": '"Not=A?Brand";v="99", "Chromium";v="118"',
        "Accept": "application/json, text/plain, */*",
        "X-Ibm-Client-Id": "41aed706-8fdf-4b1e-883e-91e44d7f379b",
        "Sec-Ch-Ua-Mobile": "?0",
        "Authorization": authorization_header,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.90 Safari/537.36",
        "Sec-Ch-Ua-Platform": '"Linux"',
        "Origin": "https://myslt.slt.lk",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://myslt.slt.lk/",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Connection": "close",
    }

    params = {
        "subscriberID": subscriberID,
    }

    response = requests.get(ProfileDetailsUrl, params=params, headers=headers)

    if response.status_code == 200:
        data = json.loads(response.text)

        if all_out:
            return data
        else:
            output = {}
            output["subscriberid"] = data["dataBundle"]["subscriberid"]
            output["fullname"] = data["dataBundle"]["fullname"]
            output["subscriber_package"] = data["dataBundle"][
                "subscriber_package_display"
            ]
            output["email"] = data["dataBundle"]["email"]
            output["phone"] = data["dataBundle"]["phone"]
            return output

    else:
        return None


def getBillPaymentDetails(authorization_header, all_out=False):

    config = loadConfig(CONFIG_FILE)
    telephone = config["account"]["telephone"]
    accountno = config["account"]["accountno"]
    BillPaymentUrl = config["server"]["BillPaymentUrl"]

    headers = {
        "Host": "omniscapp.slt.lk",
        "Sec-Ch-Ua": '"Not=A?Brand";v="99", "Chromium";v="118"',
        "Accept": "application/json, text/plain, */*",
        "X-Ibm-Client-Id": "41aed706-8fdf-4b1e-883e-91e44d7f379b",
        "Sec-Ch-Ua-Mobile": "?0",
        "Authorization": authorization_header,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.90 Safari/537.36",
        "Sec-Ch-Ua-Platform": '"Linux"',
        "Origin": "https://myslt.slt.lk",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://myslt.slt.lk/",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Connection": "close",
    }

    params = {
        "telephoneNo": telephone,
        "accountNo": accountno,
    }

    response = requests.get(BillPaymentUrl, params=params, headers=headers)

    if response.status_code == 200:
        data = json.loads(response.text)

        if all_out:
            return data
        else:
            output = {}
            output["outstandingBalance"] = data["dataBundle"][
                "listofbillingInquiryType"
            ][0]["outstandingBalance"]
            output["paymentDueDate"] = data["dataBundle"]["listofbillingInquiryType"][
                0
            ]["paymentDueDate"]

            return output

    else:
        return None


def logout():
    global CONFIG_FILE

    config = loadConfig(CONFIG_FILE)
    config["authentication"].pop("authorization_header", None)
    config["account"].pop("telephone", None)
    config["account"].pop("accountno", None)
    config["account"].pop("subscriberID", None)

    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Command Line Tool to fetch usage information for SLT users by kavigihan"
    )
    parser.add_argument(
        "action",
        choices=["login", "usage", "account", "bill", "logout"],
        help="Action to perform",
    )
    parser.add_argument(
        "-a", "--all", action="store_true", help="Output all the details in json"
    )
    args = parser.parse_args()

    config = loadConfig(CONFIG_FILE)
    if args.action == "login":
        if "authorization_header" not in config["authentication"]:
            if loginUser(
                config["authentication"]["username"],
                config["authentication"]["password"],
            ):
                print("Login successful.")
            else:
                print("Login failed!")
                exit(1)
        else:
            print("Already logged in, logout first to relogin!")
            exit(1)

        config = loadConfig(CONFIG_FILE)
        if getAccountDetails(config["authentication"]["authorization_header"])[0]:
            print("Account information fetched and saved!")
        else:
            print("Error fetching account information!")

    elif args.action == "usage":

        if ("authorization_header" not in config["authentication"]) or (
            "subscriberID" not in config["account"]
        ):
            print("Please log in and provide account details.")
            return

        if args.all:
            usageDetails = getUsageDetails(
                config["authentication"]["authorization_header"], all_out=True
            )
            print(json.dumps(usageDetails))
        else:

            output = getUsageDetails(config["authentication"]["authorization_header"])
            if output:
                print(json.dumps(output))
            else:
                print("Error fetching usage information!")

    elif args.action == "account":

        if ("authorization_header" not in config["authentication"]) or (
            "subscriberID" not in config["account"]
        ):
            print("Please log in and provide account details.")
            return

        if args.all:
            profileDetails = getProfileDetails(
                config["authentication"]["authorization_header"], all_out=True
            )
            print(json.dumps(profileDetails))
        else:

            profileDetails = getProfileDetails(
                config["authentication"]["authorization_header"]
            )
            if profileDetails:
                print(json.dumps(profileDetails))
            else:
                print("Error fetching account information!")

    elif args.action == "bill":

        if ("authorization_header" not in config["authentication"]) or (
            "subscriberID" not in config["account"]
        ):
            print("Please log in and provide account details.")
            return

        if args.all:
            billDetails = getBillPaymentDetails(
                config["authentication"]["authorization_header"], all_out=True
            )
            print(json.dumps(billDetails))
        else:

            billDetails = getBillPaymentDetails(
                config["authentication"]["authorization_header"]
            )
            if billDetails:
                print(json.dumps(billDetails))
            else:
                print("Error fetching bill information!")

    elif args.action == "logout":
        if logout():
            print("Logout successful!")


if __name__ == "__main__":
    main()
