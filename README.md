# TioPatinhas Project

## Introduction

Tio Patinhas is a personal project for trading assets (stocks, cryptos)

## Installation
### min versions
* Python - 3.9.2 · [Download/Update Python3](https://www.python.org/downloads/)
* pip - 21.0.1

>**Note:** This should only be executed once and if you don't already have this installed. Please validate this before running this commands

``` 
$ python3 -m pip install --upgrade pip 
$ python3 -m pip install --user virtualenv
```

### Create Virtual Environment

```
$ cd [PATH]/[PROJECT_FOLDER]/
$ python3 -m venv .env/virtualenv
```

### Install Packages
```
$ source [PATH]/[PROJECT_FOLDER]/.env/virtualenv/bin/activate
$ python -m pip install -r requirements.txt
```

### Install IBC Controller
**IMPORTANT NOTES REGARDING TWS 974 and later versions**
>
>In TWS 974, IBKR have changed the way the autologoff function works within TWS. Starting with that version, when the time approaches the configured autologoff time, logoff can be deferred once by changing the autologoff time in the 'Exit Session Setting' dialog as in earlier versions, but when the new autologoff time arrives, TWS will logoff even if the user (or IBC) changes the autologoff time again.
> IBC enables Interactive Brokers' Trader Workstation (TWS) to be run in 'hands-free' mode, so that a user need not be present. This makes possible the deployment of unattended automated trading systems.
### Min versions
* TWS Offline - 981 · [Download TWS Offline](https://www.interactivebrokers.com/en/index.php?f=14099#tws-software)
* IBC Controller - 3.8.5 · [Download IBC Controller](https://github.com/IbcAlpha/IBC/releases/tag/3.8.5)

### Steps
* Install the TWS Offline version
* After Downloading IBC Controller Zip (IBCMacos-3.8.5.zip), you need to move the content to a specific folder, and set all the files executable. Use this command
```
$ sudo unzip ~/Downloads/IBCMacos-3.8.5.zip -d /opt/ibc
$ cd /opt/ibc
$ sudo chmod o+x *.sh */*.sh
```

>You should also have a `config.ini` with you personal configs. You can check a template inside that Zip.
If you have any daughts of where to pu this please consult this [User Guide](https://github.com/IbcAlpha/IBC/blob/master/userguide.md#getting-started). I have also add a document with that User guide [here](https://github.com/pedrosilva88/TioPatinhasProject/blob/master/Documents/IBCUserGuide.pdf)

In this `config.ini` you should provide your username, password, the version of TWS that you installed and the trading mode that you want to use.

## Run Project
```
$ cd [PATH]/[PROJECT_FOLDER]/
$ source [PATH]/[PROJECT_FOLDER]/.env/virtualenv/bin/activate
$ python main.py [PATH_TO_FILE]/[FILE_CONFIGS].ini
```


## Applications
### Programming and Debugging
- Visual Code
    - Extensions (Python, Pylance, Gitlens)
- Terminal ZSH

### Manage Repo
- Fork




