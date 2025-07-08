from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend_database_query.Logger import Logger

from backend_database_query.connectors.WebSocketManager import WebSocketManager

'''
Note:   WebSockets (auto)documentation on OpenAPI generated on /docs will not
        show any websockets. OpenAPI support for documenting websockets is WIP
'''


logger = Logger("api_logger").logger
ws_bp = APIRouter(prefix='/ws', tags=['WebSocket'])
ws_manager = WebSocketManager()


@ws_bp.websocket("/echo")
async def natural_search(websocket: WebSocket):
    websocket_id = await ws_manager.connect(websocket)
    try:
        while True:
            input_json = await websocket.receive_json()
            # this will block the loop and prevent processing other stuff
            # do it in a different thread if it is long running
            await ws_manager.send_json({"received": input_json}, websocket_id)
    except WebSocketDisconnect:
        print('disconnected ' + websocket_id)
        await ws_manager.disconnect(websocket_id)
