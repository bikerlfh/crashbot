# Standard Library
import glob
import os
import platform
import shutil
import zipfile

# Internal
from apps.gui.constants import ICON_NAME
from apps.utils import os as utils_os


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


def remove_po_files(locales_path: str):
    po_files = glob.glob(f"{locales_path}/*/LC_MESSAGES/*.po")
    for po_file in po_files:
        os.remove(po_file)
    os.remove(f"{locales_path}/base.po")


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
            # https://playwright.dev/python/docs/browsers#install-browsers
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
    if _one_file:
        print("**************generating one file executable**************")
        os.system(f"pyinstaller --onefile --icon={ICON_NAME} crashbot.py")
        shutil.copytree("locales", "dist/locales")
        shutil.copy("conf._ini", "dist/conf.ini")
        shutil.copytree("custom_bots", "dist/custom_bots")
        shutil.copy(ICON_NAME, f"dist/{ICON_NAME}")
        remove_po_files("dist/locales")
    else:
        file_name = f"crashbot/{file_name}"
        print("**************generating executable**************")
        os.system(
            f'pyinstaller --icon={ICON_NAME} \
            --add-data "custom_bots{os.pathsep}custom_bots" \
            --add-data "locales{os.pathsep}locales" \
            --add-data "license.txt{os.pathsep}." \
            --add-data "{ICON_NAME}{os.pathsep}." crashbot.py'
        )
        shutil.copy("conf._ini", "dist/crashbot/conf.ini")
        remove_po_files("dist/crashbot/locales")
    os.system(
        f"pyarmor gen -O obfdist --pack dist/{file_name} -r crashbot.py apps"
    )
    print("FINISHED!")


if __name__ == "__main__":
    main()
