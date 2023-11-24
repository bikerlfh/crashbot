# Standard Library
from threading import Event

# Libraries
import socketio
import uvicorn

# Internal
from apps.constants import WSEvent
from apps.game.ws_server import events
from apps.globals import GlobalVars

sio = socketio.AsyncServer(async_mode="asgi")
app = socketio.ASGIApp(sio)

event_ = None


@sio.on("connect")
async def connect(sid, environ):
    print("connect to game server", sid)


@sio.on("disconnect")
def disconnect(sid):
    GlobalVars.WS_SERVER_EVENT.set()
    print("event set:", GlobalVars.WS_SERVER_EVENT.is_set())
    print("disconnect to game server", sid)


@sio.on(WSEvent.LOGIN)
async def login(sid, data, room=None):
    data_ = events.login_event(data)
    await sio.emit("login", data=data_, room=sid)


@sio.on(WSEvent.VERIFY)
async def verify(sid, data, room=None):
    data_ = events.verify_event()
    await sio.emit("verify", data=data_, room=sid)


@sio.on(WSEvent.AUTO_PLAY)
async def set_auto_play(sid, data, room=None):
    data_ = events.auto_play_event(data)
    await sio.emit(WSEvent.AUTO_PLAY, data=data_, room=sid)


@sio.on(WSEvent.CHANGE_BOT)
async def change_bot(sid, data, room=None):
    data_ = events.change_bot_event(data)
    await sio.emit(WSEvent.CHANGE_BOT, data=data_, room=sid)


@sio.on(WSEvent.SET_MAX_AMOUNT_TO_BET)
async def set_max_amount_to_bet(sid, data, room=None):
    data_ = events.set_max_amount_to_bet_event(data)
    await sio.emit(WSEvent.SET_MAX_AMOUNT_TO_BET, data=data_, room=sid)


@sio.on(WSEvent.CLOSE_GAME)
async def close_game(sid, data, room=None):
    data_ = await events.close_game_event()
    await sio.emit(WSEvent.CLOSE_GAME, data=data_, room=sid)


@sio.on(WSEvent.START_BOT)
async def start_bot(sid, data, room=None):
    await events.start_bot_event(data, sio, sid)


def run_server(event: Event):
    GlobalVars.set_io(sio)
    GlobalVars.WS_SERVER_EVENT = event
    uvicorn.run(
        app,
        host=GlobalVars.config.WS_SERVER_HOST,
        port=GlobalVars.config.WS_SERVER_PORT,
    )
