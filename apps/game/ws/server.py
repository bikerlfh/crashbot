import uvicorn
import socketio
from apps.game.ws.constants import WS_SERVER_HOST, WS_SERVER_PORT
from apps.globals import GlobalVars
from apps.game.ws import events


sio = socketio.AsyncServer(async_mode="asgi")
app = socketio.ASGIApp(sio)


@sio.on("connect")
async def connect(sid, environ):
    print("connect to game server", sid)


@sio.on("disconnect")
def disconnect(sid):
    print("disconnect to game server", sid)


@sio.on("login")
async def login(sid, data, room=None):
    is_logged = events.login_event(data)
    await sio.emit("login", data={"logged": is_logged}, room=sid)


@sio.on("verify")
async def verify(sid, data, room=None):
    is_valid = events.verify_event()
    await sio.emit("verify", data={"logged": is_valid}, room=sid)


@sio.on("autoPlay")
async def set_auto_play(sid, data, room=None):
    data_ = events.auto_play_event(data)
    await sio.emit("autoPlay", data=data_, room=sid)


@sio.on("setMaxAmountToBet")
async def set_max_amount_to_bet(sid, data, room=None):
    data_ = events.set_max_amount_to_bet_event(data)
    await sio.emit("setMaxAmountToBet", data=data_, room=sid)


@sio.on("closeGame")
async def close_game(sid, data, room=None):
    data_ = await events.close_game_event()
    await sio.emit("closeGame", data=data_, room=sid)


@sio.on("startBot")
async def start_bot(sid, data, room=None):
    await events.start_bot_event(data, sio, sid)


def run_server():
    GlobalVars.set_io(sio)
    uvicorn.run(app, host=WS_SERVER_HOST, port=WS_SERVER_PORT)
