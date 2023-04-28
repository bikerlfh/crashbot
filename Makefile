designer:
	designer ui/$(ui).ui

generate-ui:
	pyuic6 -x ui/$(ui).ui -o file.py

run:
	python app.py

black: ## black
	black . --line-length=79

generate-installer:
	pyinstaller --onefile --icon=resources/bot.ico crashbot.py
