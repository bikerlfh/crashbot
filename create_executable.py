# Standard Library
import os
import platform
import shutil
import zipfile

# Internal
from apps.gui.utils import os as utils_os


def _zipdir(dir_path: str, zip_path: str):
    print("**************zipping executable**************")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_name in os.listdir(dir_path):
            if ".zip" in file_name:
                continue
            if os.path.isdir(os.path.join(dir_path, file_name)):
                zipf.write(
                    os.path.join(dir_path, file_name) + "/",
                    f"crashbot/{file_name}/",
                )
                continue
            zipf.write(
                os.path.join(dir_path, file_name), f"crashbot/{file_name}/"
            )


def main():
    is_windows = utils_os.is_windows()
    print(
        f"**************"
        f"generating executable for crashbot "
        f"({platform.system()})**************"
    )
    try:
        # Libraries
        import pyarmor  # noqa
    except ImportError:
        os.system("pip install --upgrade pip")
        os.system("pip install -r requirements_installer.txt")
        if is_windows:
            # install playwright chromium
            os.system("$Env:PLAYWRIGHT_BROWSERS_PATH=0")
        else:
            os.system("export PLAYWRIGHT_BROWSERS_PATH=0")
        os.system("python -m playwright install chromium")
    file_name = "crashbot.exe" if is_windows else "crashbot"
    #  question input one_file
    q_one_file = input(
        "Do you want to generate a one file executable? (default true) (y/n): "
    )
    _one_file = q_one_file.lower() != "n"
    # remove dist folder
    shutil.rmtree("dist", ignore_errors=True)
    # use pyarmor to obfuscate the code and one file
    if os.path.exists("conf._ini"):
        shutil.copy("conf._ini", "conf.ini")
    if _one_file:
        print("**************generating one file executable**************")
        os.system("pyinstaller --onefile --icon=crashbot-icon.ico crashbot.py")
        shutil.copytree("locales", "dist/locales")
        shutil.copy("conf.ini", "dist/conf.ini")
        shutil.copy("custom_bots.json", "dist/custom_bots.json")
        shutil.copy("crashbot-icon.ico", "dist/crashbot-icon.ico")
    else:
        file_name = f"crashbot/{file_name}"
        print("**************generating executable**************")
        os.system(
            f'pyinstaller --icon=crashbot-icon.ico \
            --add-data "custom_bots.json{os.pathsep}." \
            --add-data "locales{os.pathsep}locales" \
            --add-data "license.txt{os.pathsep}." \
            --add-data "conf.ini{os.pathsep}." \
            --add-data "crashbot-icon.ico{os.pathsep}." crashbot.py'
        )
    os.system(
        f"pyarmor gen -O obfdist --pack dist/{file_name} -r crashbot.py apps"
    )
    print("FINISHED!")


if __name__ == "__main__":
    main()
