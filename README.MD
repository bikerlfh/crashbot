
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

### INSTALL DESIGNER UI IN WINDOWS

https://www.pythontutorial.net/pyqt/qt-designer/

Install PyQt6 and its tools
First, execute the following command to install pyqt6 package in the pyqt6-env virtual environment:
```
pip install pyqt6
```
Second, install the pyqt6-tools package that contains the Qt Designer and other related tools:
```
pip install pyqt6-tools
```
The pyqt-tools package will install the Qt Designer in the following location:
```
D:\pyqt6\pyqt6-env\Lib\site-packages\qt6_applications\Qt\bin\designer.exe
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


# make executable

you can use pyinstaller to generate the executable or https://pypi.org/project/pyarmor/ with obfuscation (use https://github.com/dashingsoft/pyarmor-webui)
```
pyinstaller --onefile --icon=crashbot-icon.ico crashbot.py
```
or
```
make generate-installer
```
### if you use pyenv install the version
PYTHON_CONFIGURE_OPTS="--enable-framework" pyenv install 3.10.4


# create language 

Install gettext
```
pip install python-gettext
```
```
pygettext -d base -o locales/base.po  .
```

Generate the binary file

```
msgfmt -o locales/es/LC_MESSAGES/base.mo locales/es/LC_MESSAGES/base
```
Edit Configurations...

use poedit to translate the file base.po (https://poedit.net/)


(https://phrase.com/blog/posts/translate-python-gnu-gettext/)