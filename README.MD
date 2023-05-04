
## Command generate py with ui
```
pyuic6 -x [path ui] -o [path file ui]
```
example:
```
pyuic6 -x ui/login.ui -o file.py
```

# Install Requirements

### - Sqlite 3

#### Linux
```
sudo apt-get install sqlite3
```
#### Windows
https://www.sqlite.org/download.html


### INSTALL DESIGNER UI IN UBUNTU
https://pythonbasics.org/qt-designer-python/

/usr/lib/x86_64-linux-gnu/qt5/bin

# LINUX
```
sudo apt-get install '^libxcb.*-dev' libx11-xcb-dev libglu1-mesa-dev libxrender-dev libxi-dev libxkbcommon-dev libxkbcommon-x11-dev
```
```
pip install -r requirements.txt
```

# CONFIG FILE (conf.ini)

* API_URL: url api
* MAX_AMOUNT_HOME_BET_PERCENTAGE:  max amount home bet percentage (0.01 - 1)
* MAX_AMOUNT_BALANCE_PERCENTAGE: max amount balance percentage (0.01 - 1)
* ALLOWED_LOG_CODES: allowed log codes (comma separated without spaces) example:info,error,debug,warning

## ENVARS

* URL_SOCKET: url socket
* IS_ALLOWED_TO_SAVE_MULTIPLIERS: is allowed to save multipliers (1: true, 0: false)


# Logs

you can find the logs in the folder data/logs.db (sqlite3)


# COMPILE APPLICATION:

For the compilation of the application, it will be done with **pyinstaller** the following command applies to all operating systems

```
pip install pyinstaller
```
```
pyinstaller --onefile --icon=resources/bot.ico crashbot.py
```
or
```
make generate-installer
```