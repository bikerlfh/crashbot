# Libraries
from socketio import AsyncServer

# Internal
from apps.constants import BotType, HomeBets, WSEvent
from apps.game.game import Game
from apps.game.ws_server import handlers
from apps.game.ws_server.utils import make_error
from apps.globals import GlobalVars
from apps.gui.gui_events import SendEventToGUI
from apps.utils.local_storage import LocalStorage

local_storage = LocalStorage()


def verify_event(**_kwargs) -> dict[str, any]:
    return handlers.verify_token()


def login_event(data: dict[str, any]) -> dict[str, any]:
    """
    ws_server callback for login
    :param data: dict(logged: bool)
    :return: None
    """
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return make_error("username and password are required")
    return handlers.login(username=username, password=password)


def auto_play_event(data: dict[str, any]) -> dict[str, any]:
    auto_play = data.get("auto_play")
    GlobalVars.set_auto_play(auto_play)
    data_ = dict(auto_play=GlobalVars.get_auto_play())
    return data_


def set_max_amount_to_bet_event(data: dict[str, any]) -> dict[str, any]:
    max_amount_to_bet = data.get("max_amount_to_bet")
    if not max_amount_to_bet:
        return make_error("maxAmountToBet is required")
    GlobalVars.set_max_amount_to_bet(max_amount_to_bet)
    game = GlobalVars.get_game()
    if not game:
        return make_error("game is not running")
    max_amount_to_bet = GlobalVars.get_max_amount_to_bet()
    game.bot.set_max_amount_to_bet(max_amount_to_bet)
    data = dict(max_amount_to_bet=max_amount_to_bet)
    return data


async def close_game_event(**_kwargs) -> dict[str, any]:
    game = GlobalVars.get_game()
    if not game:
        return dict(closed=True)
    await game.close()
    GlobalVars.set_game(None)
    return dict(closed=True)


async def start_bot_event(data: dict[str, any], sio: AsyncServer, sid: any) -> any:
    GlobalVars.set_io(sio)
    bot_type = data.get("bot_type")
    home_bet_id = data.get("home_bet_id")
    username = data.get("username")
    password = data.get("password")
    if not bot_type or not home_bet_id:
        await sio.emit(
            WSEvent.START_BOT,
            data=make_error("bot_type and home_bet_id are required"),
            room=sid,
        )
        return
    home_bet = list(filter(lambda x: x.id == home_bet_id, HomeBets))
    if not home_bet:
        await sio.emit(
            WSEvent.START_BOT, data=make_error("invalid home_bet_id"), room=sid
        )
        return
    home_bet = home_bet[0]
    bot_type = BotType(bot_type)
    GlobalVars.set_username(username)
    GlobalVars.set_password(password)
    game = GlobalVars.get_game()
    if game:
        return make_error("game is already running")

    game = Game(home_bet=home_bet, bot_type=bot_type, use_bot_static=True)
    GlobalVars.set_game(game)
    await sio.emit(WSEvent.START_BOT, data=dict(started=True), room=sid)
    try:
        await game.initialize()
        await game.play()
    except Exception as e:
        await game.close()
        GlobalVars.set_game(None)
        SendEventToGUI.exception(
            dict(
                exception=str(e),
                message="Error while running the bot",
            )
        )
