from fastapi import APIRouter

router = APIRouter()

@router.get("/orders")
def get_orders():
    # Mock data
    return [
        {"id": "1", "symbol": "AAPL", "side": "buy", "quantity": 10, "status": "filled", "price": 175.0},
        {"id": "2", "symbol": "GOOGL", "side": "sell", "quantity": 5, "status": "pending", "price": 2850.0},
    ] 