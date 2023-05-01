designer:
	designer ui/$(ui).ui

generate-ui:
	pyuic6 -x ui/$(ui).ui -o file.py

generate-ui-login:
	pyuic6 -x apps/gui/resources/ui/login.ui -o file.py -p apps/gui/windows/login/login_designer_new.py

generate-ui-parameters:
	pyuic6 -x apps/gui/resources/ui/parameter.ui -o apps/gui/windows/parameter/parameter_designer_new.py

generate-ui-console:
	pyuic6 -x apps/gui/resources/ui/console.ui -o apps/gui/windows/console/console_designer_new.py

run:
	python app.py

black: ## black
	black . --line-length=79

generate-installer:
	pyinstaller --onefile --icon=resources/bot.ico crashbot.py
