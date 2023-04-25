import uvicorn
import socketio
from apps.game.ws.constants import WS_SERVER_HOST, WS_SERVER_PORT
from apps.globals import GlobalVars
from apps.game.ws import events
from apps.constants import WSEvent

sio = socketio.AsyncServer(async_mode="asgi")
app = socketio.ASGIApp(sio)


@sio.on("connect")
async def connect(sid, environ):
    print("connect to game server", sid)


@sio.on("disconnect")
def disconnect(sid):
    print("disconnect to game server", sid)


@sio.on(WSEvent.LOGIN)
async def login(sid, data, room=None):
    is_logged = events.login_event(data)
    await sio.emit("login", data={"logged": is_logged}, room=sid)


@sio.on(WSEvent.VERIFY)
async def verify(sid, data, room=None):
    is_valid = events.verify_event()
    await sio.emit("verify", data={"logged": is_valid}, room=sid)


@sio.on(WSEvent.AUTO_PLAY)
async def set_auto_play(sid, data, room=None):
    print("set_auto_play", data)
    data_ = events.auto_play_event(data)
    await sio.emit(WSEvent.AUTO_PLAY, data=data_, room=sid)


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


def run_server():
    GlobalVars.set_io(sio)
    uvicorn.run(app, host=WS_SERVER_HOST, port=WS_SERVER_PORT)
