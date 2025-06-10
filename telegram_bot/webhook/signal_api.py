from fastapi import FastAPI, HTTPException, Header, Request
from pydantic import BaseModel
from typing import Optional
import httpx
import json
from bot.config import config
from bot.handlers.signals import broadcast_signal

app = FastAPI(title="Trading Bot Signal API")

class SignalData(BaseModel):
    pair: str
    direction: str
    entry: float
    sl: float
    tp: float

async def verify_signal_secret(signal_secret: Optional[str] = Header(None)):
    """Verify signal secret from header"""
    if not signal_secret or signal_secret != config.signal_secret:
        raise HTTPException(
            status_code=401,
            detail="Invalid signal secret"
        )

@app.post("/signal")
async def receive_signal(
    signal: SignalData,
    signal_secret: Optional[str] = Header(None)
):
    """Receive trading signal"""
    # Verify signal secret
    await verify_signal_secret(signal_secret)
    
    # Convert signal to dict
    signal_data = signal.dict()
    
    # Broadcast signal to all authorized users
    async with httpx.AsyncClient() as client:
        await broadcast_signal(client, signal_data)
    
    return {"status": "success", "message": "Signal broadcasted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 