designer:
	designer apps/gui/resources/ui/$(ui).ui

designer-win:
	env/Lib/site-packages/qt6_applications/Qt/bin/designer.exe apps/gui/resources/ui/$(ui).ui

generate-ui:
	pyuic6 -x apps/gui/resources/ui/${ui}.ui -o file.py

generate-ui-app:
	pyuic6 -x apps/gui/resources/ui/app.ui -o apps/gui/windows/main/main_designer_new.py

generate-ui-login:
	pyuic6 -x apps/gui/resources/ui/login.ui -o apps/gui/windows/login/login_designer_new.py

generate-ui-parameters:
	pyuic6 -x apps/gui/resources/ui/parameter.ui -o apps/gui/windows/parameter/parameter_designer_new.py

generate-ui-console:
	pyuic6 -x apps/gui/resources/ui/console.ui -o apps/gui/windows/console/console_designer_new.py

generate-ui-config-bot:
	pyuic6 -x apps/gui/resources/ui/config_bot.ui -o apps/gui/windows/config_bot/config_bot_designer_new.py

run:
	python crashbot.py

black: ## black
	black . --line-length=79

generate-installer:
	pyinstaller --onefile --icon=/apps/gui/resources/bot.ico crashbot.py

translate:
	msgfmt -o locales/es/LC_MESSAGES/base.mo locales/es/LC_MESSAGES/base