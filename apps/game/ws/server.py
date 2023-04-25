import uvicorn
import socketio

from apps.game.ws import events


sio = socketio.AsyncServer(async_mode="asgi")
app = socketio.ASGIApp(sio)


@sio.on("connect")
async def connect(sid, environ):
    print("connect ", sid)


@sio.on("disconnect")
def disconnect(sid):
    print("disconnect ", sid)


@sio.on("login")
async def login_event(sid, data, room=None):
    is_logged = events.login(data)
    await sio.emit("login", data={"logged": is_logged}, room=sid)


@sio.on("verify")
async def verify_event(sid, data, room=None):
    is_valid = events.verify(data)
    await sio.emit("verify", data={"logged": is_valid}, room=sid)


@sio.on("setMaxAmountToBet")
async def set_max_amount_to_bet_event(sid, data, room=None):
    print(f"message {data} - {room} - {sid}")
    await sio.emit("setMaxAmountToBet", data={"message": "received"}, room=sid)


def run_server():
    uvicorn.run(app, host="localhost", port=5000)
