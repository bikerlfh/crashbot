# Libraries
from socketio import AsyncServer

# Internal
from apps.constants import WSEvent
from apps.game.bookmakers.home_bet import HomeBet
from apps.game.games.constants import GameType
from apps.game.games.game_base import GameBase
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


def change_bot_event(data: dict[str, any]) -> dict[str, any]:
    bot_name = data.get("bot_name")
    if not bot_name:
        return make_error("bot_name is required")
    game = GlobalVars.get_game()
    if not game:
        return make_error("game is not running")
    game.initialize_bot(bot_name=bot_name)
    data = dict(bot_name=game.bot.BOT_NAME)
    return data


def set_max_amount_to_bet_event(data: dict[str, any]) -> dict[str, any]:
    max_amount_to_bet = data.get("max_amount_to_bet")
    if not max_amount_to_bet:
        return make_error("maxAmountToBet is required")
    GlobalVars.set_max_amount_to_bet(max_amount_to_bet)
    game = GlobalVars.get_game()
    if not game:
        return make_error("game is not running")
    max_amount_to_bet = GlobalVars.get_max_amount_to_bet()
    game.bot.set_max_amount_to_bet(amount=max_amount_to_bet, user_change=True)
    data = dict(max_amount_to_bet=max_amount_to_bet)
    return data


async def close_game_event(**_kwargs) -> dict[str, any]:
    game = GlobalVars.get_game()
    if not game:
        return dict(closed=True)
    await game.close()
    GlobalVars.set_game(None)
    local_storage.remove_last_initial_balance(home_bet_id=game.home_bet.id)
    return dict(closed=True)


async def start_bot_event(
    data: dict[str, any], sio: AsyncServer, sid: any
) -> any:
    GlobalVars.set_io(sio)
    bot_name = data.get("bot_name")
    home_bet_id = data.get("home_bet_id")
    username = data.get("username")
    password = data.get("password")
    use_game_ai = data.get("use_game_ai", False)
    if not bot_name or not home_bet_id:
        await sio.emit(
            WSEvent.START_BOT,
            data=make_error("bot_name and home_bet_id are required"),
            room=sid,
        )
        return
    home_bets = GlobalVars.get_allowed_home_bets()
    home_bet_ = next(filter(lambda x: x.id == home_bet_id, home_bets), None)
    if not home_bet_:
        await sio.emit(
            WSEvent.START_BOT, data=make_error("invalid home_bet_id"), room=sid
        )
        return
    home_bet = HomeBet(**vars(home_bet_))
    GlobalVars.set_username(username)
    GlobalVars.set_password(password)
    game = GlobalVars.get_game()
    if game:
        return make_error("game is already running")

    game_type = GameType.STRATEGY.value
    if use_game_ai:
        game_type = GameType.AI.value
    game = GameBase(
        configuration=game_type,
        home_bet=home_bet,
        bot_name=bot_name,
    )
    GlobalVars.set_game(game)
    await sio.emit(WSEvent.START_BOT, data=dict(started=True), room=sid)
    try:
        await game.initialize()
        await game.play()
    except Exception as e:
        await game.close()
        GlobalVars.set_game(None)
        local_storage.set_last_initial_balance(
            home_bet_id=game.home_bet.id, balance=game.initial_balance
        )
        SendEventToGUI.exception(
            dict(
                exception=str(e),
                message="Error while running the bot",
            )
        )
