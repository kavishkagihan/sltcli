# sltcli

### Description
Command Line Tool to fetch usage, bill and account information for SLT users

### Installation

1. Clone this repository

```bash
git clone https://github.com/kavishkagihan/sltcli.git
```
2. Run the script for the first time.
```bash
cd sltcli
python3 sltcli.py login
```
This copy the `example_config.json` file to `$HOME/.sltcli/config.json` and ask you to add the credentials.

3. Next you need to edit the config file and change the username and password you use to login to https://myslt.slt.lk/ 

```
{
    "authentication": {
        "username": "change_your_username",
        "password": "change_your_username"
    },
```
4. Once you have done that, you can run the script again.

```bash
python3 sltcli.py login
```

### Usage

You can use this to fetch usage, bill and account information from https://myslt.slt.lk/ while sitting in the command line.

```
usage: sltcli.py [-h] [-a] {login,usage,account,bill,logout}

Command Line Tool to fetch usage, bill and account information for SLT users

positional arguments:
  {login,usage,account,bill,logout}
                        Action to perform

options:
  -h, --help            show this help message and exit
  -a, --all             Output all the details in json
```

- You can use `login` to login and save the session.

```bash
python3 sltcli.py login
```
- You can use `logout` to logout
- You can use `usage`, `account` and `bill` to get the usage information, account details and payment details respectively. (This will show a filtered output of the most important data)

```bash
python3 sltsli.py {usage,account,bill}
```
- You can use `-a` flag with these actions to get the full repsonse instead of the filtered output.

```bash
python3 sltsli.py {usage,account,bill} -a
```
