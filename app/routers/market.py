from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Body
from typing import Dict
from sqlalchemy.orm import Session
from app.database import get_db
import json
from app.services.market import MarketService
from app.utils.auth import get_current_user
import asyncio
from datetime import datetime  
from ..models.trade import Trade
from ..services.trade_service import TradeService
from ..schemas.trade import TradeCreate
from .connection_manager import ConnectionManager, ClientType  
from pydantic import BaseModel
from app.models.user import User
import pytz

manager = ConnectionManager()

router = APIRouter(prefix="/api/markets", tags=["Markets"])

class OverrideRequest(BaseModel):
    userId: int
    target_price: float
    symbol: str  
    target_time: str  

async def receive_from_fe(websocket: WebSocket, db: Session):
    try:
        while True:
            data_from_fe = await websocket.receive_text()
            print(f"Received data from FE: {data_from_fe}") 

            try:
                data_json = json.loads(data_from_fe)
                print(f"Parsed JSON from FE: {data_json}")  

                if "symbol" in data_json and "time" in data_json and "type" in data_json and "deposit" in data_json and "userId" in data_json and "current_price" in data_json:
                    utc_time = datetime.fromisoformat(data_json["time"].replace("Z", "+00:00"))
                    local_timezone = pytz.timezone('Asia/Ho_Chi_Minh')  
                    local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(local_timezone)

                    trade_data = TradeCreate(
                        symbol=data_json["symbol"],
                        userId=data_json["userId"],
                        time_predict=local_time,
                        type_predict=data_json["type"],
                        deposit=data_json["deposit"],
                        current_price=data_json["current_price"],
                        result="pending"
                    )

                    trade_service = TradeService(db)
                    created_trade = trade_service.create_trade(trade_data)

                    # In ra thời gian local (giờ Việt Nam)
                    print(f"Created trade with local time: {local_time.strftime('%Y-%m-%d %H:%M:%S')} Vietnam Time")

            except json.JSONDecodeError:
                print("Received data is not a valid JSON")  
            except Exception as e:
                print(f"Error processing data from FE: {e}")  

    except Exception as e:
        print(f"Error receiving data from FE: {e}") 

async def send_market_data(websocket: WebSocket):
    try:
        market_service = MarketService()
        local_timezone = pytz.timezone('Asia/Ho_Chi_Minh')  # Múi giờ Việt Nam

        while True:
            btc_price, eth_price = await market_service.get_prices()
            current_time = datetime.now(local_timezone)  # Lấy thời gian hiện tại theo múi giờ Việt Nam
            current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")

            response_data = json.dumps({
                "btc_price": btc_price,
                "eth_price": eth_price,
                "time": current_time_str  # Gửi thời gian theo múi giờ Việt Nam
            })
            await websocket.send_text(response_data)

            await asyncio.sleep(1)
    except Exception as e:
        print(f"Error sending market data: {e}")  

@router.websocket("/ws/fe/{client_id}")
async def fe_websocket_endpoint(
    websocket: WebSocket,
    client_id: int,
    token: str,
    db: Session = Depends(get_db)
):
    try:
        print(f"Client {client_id} connected to WebSocket")
        user = await get_current_user(token, db)
    except HTTPException as e:
        await websocket.close(code=4001)
        return

    await manager.connect(websocket, ClientType.FE.value, client_id)
    try:
        receive_task = asyncio.create_task(receive_from_fe(websocket, db))
        send_task = asyncio.create_task(send_market_data(websocket))
        await asyncio.gather(receive_task, send_task)

    except WebSocketDisconnect:
        manager.disconnect(ClientType.FE.value, client_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close(code=1011)

def is_admin(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can perform this action")
    return user

@router.post("/over_ride")
async def override_price(
    request: OverrideRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(is_admin)  
):
    try:
        response_message = {"message": "Request received. Processing in the background."}
        asyncio.create_task(process_override_request(request, db))
        
        return response_message

    except Exception as e:
        print(f"Error in override_price: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_override_request(request: OverrideRequest, db: Session):
    try:
        local_timezone = pytz.timezone('Asia/Ho_Chi_Minh')  # Múi giờ Việt Nam

        # Chuyển đổi target_time từ chuỗi sang đối tượng datetime với múi giờ Việt Nam
        target_time = datetime.strptime(request.target_time, "%Y-%m-%d %H:%M:%S")
        target_time = local_timezone.localize(target_time)  # Áp dụng múi giờ Việt Nam

        current_time = datetime.now(local_timezone)  # Lấy thời gian hiện tại theo múi giờ Việt Nam

        print(f"Current time (Vietnam): {current_time.strftime('%Y-%m-%d %H:%M:%S')} Vietnam Time")
        print(f"Target time (Vietnam): {target_time.strftime('%Y-%m-%d %H:%M:%S')} Vietnam Time")

        while current_time < target_time:
            await asyncio.sleep(1)
            current_time = datetime.now(local_timezone)  # Cập nhật thời gian hiện tại theo múi giờ Việt Nam
            print(f"Waiting... Current time (Vietnam): {current_time.strftime('%Y-%m-%d %H:%M:%S')} Vietnam Time")

        print(f"Overriding price for {request.symbol} at {current_time.strftime('%Y-%m-%d %H:%M:%S')} Vietnam Time")
        print(f"Target price: {request.target_price}")

        if request.symbol == "BTC":
            data_to_send = {
                "btc_price": request.target_price,
                "eth_price": None,
                "time": current_time.strftime('%Y-%m-%d %H:%M:%S')  # Gửi thời gian theo múi giờ Việt Nam
            }
            await manager.send_to_fe(str(request.userId), json.dumps(data_to_send))
        elif request.symbol == "ETH":
            data_to_send = {
                "btc_price": None,
                "eth_price": request.target_price,
                "time": current_time.strftime('%Y-%m-%d %H:%M:%S')  # Gửi thời gian theo múi giờ Việt Nam
            }
            await manager.send_to_fe(str(request.userId), json.dumps(data_to_send))
        else:
            raise HTTPException(status_code=400, detail="Invalid symbol. Must be 'BTC' or 'ETH'.")

        print(f"Data sent to FE: {data_to_send}")

    except Exception as e:
        print(f"Error in process_override_request: {e}")