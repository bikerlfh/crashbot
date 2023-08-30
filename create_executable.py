# Standard Library
import os
import platform

# Internal
from apps.gui.utils import os as utils_os


def main():
    print(f"generating executable for crashbot ({platform.system()})")
    # coping the requirements.txt file to the dist directory
    os.system("pip install --upgrade pip")
    os.system("pip install -r requirements_installer.txt")
    if utils_os.is_windows():
        # install playwright chromium
        os.system("$Env:PLAYWRIGHT_BROWSERS_PATH=0")
    else:
        os.system("export PLAYWRIGHT_BROWSERS_PATH=0")
    os.system("python -m playwright install chromium")
    # use pyarmor to obfuscate the code and one file
    # os.system("pyinstaller -F crashbot.py")
    os.system("pyinstaller --onefile --icon=crashbot-icon.ico crashbot.py")
    os.system("pyarmor gen -O obfdist --pack dist/crashbot crashbot.py")
    # os.system('pyarmor pack -e " --onefile" crashbot.py')
    os.system("cp -r locales dist/locales")
    os.system("cp conf.ini dist/conf.ini")
    os.system("cp custom_bots.json dist/custom_bots.json")
    os.system("cp crashbot-icon.ico dist/crashbot-icon.ico")
    print("finished")


if __name__ == "__main__":
    main()
