
Command generate py with ui
##################################################################

pyuic6 -x [path ui] -o [path file ui]

example:
pyuic6 -x ui/login.ui -o file.py

##################################################################

## INSTALL

# INSTALL DESIGNER UI IN UBUNTU
https://pythonbasics.org/qt-designer-python/
https://www.pythontutorial.net/pyqt/qt-designer/

/usr/lib/x86_64-linux-gnu/qt5/bin

# LINUX
sudo apt-get install '^libxcb.*-dev' libx11-xcb-dev libglu1-mesa-dev libxrender-dev libxi-dev libxkbcommon-dev libxkbcommon-x11-dev

pip install -r requirements.txt

## ENVARS

* URL_SOCKET: url socket
* MAX_AMOUNT_HOME_BET_PERCENTAGE:  max amount home bet percentage (0.01 - 1)
* MAX_AMOUNT_BALANCE_PERCENTAGE: max amount balance percentage (0.01 - 1)
* ALLOWED_LOG_CODES: allowed log codes (comma separated without spaces) example:info,error,debug,warning