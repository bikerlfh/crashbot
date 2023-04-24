from apps.scrappers.aviator.aviator_demo import AviatorDemo


def open_aviator_demo() -> None:
    aviator = AviatorDemo("https://www.spribe.co/games/aviator")
    aviator.open()