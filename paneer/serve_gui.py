import asyncio
import websockets
import json
from paneer.comms import exposed_functions

async def handle_call(websocket, path):
    print('connected')
    async for message in websocket:
        print('hello')
        print(message)
        data = json.loads(message)
        print(data)
        command = data.get("action")
        args = {v for k, v in data.items() if k not in ["action", "id"]}
        print(command)
        print(args)
        if command in exposed_functions:
            result = exposed_functions[command](*args)
            response = {"res": result, "id": data.get("id")}
        else:
            response = {"error": f"no command named: {command}", "id": data.get("id")}
        print(response,"tf")
        await websocket.send(json.dumps(response))

async def start_server():
    server = await websockets.serve(handle_call, "localhost", 8765)
    return server

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(start_server())
    asyncio.get_event_loop().run_forever()
