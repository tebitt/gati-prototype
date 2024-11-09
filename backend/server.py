from fastapi import FastAPI, WebSocket
import uvicorn
import asyncio

app = FastAPI()

location_data = {"lat": 0.0, "lon": 0.0}

@app.websocket("/ws/location")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        await websocket.send_json(location_data)
        await asyncio.sleep(1)

@app.post("/update_location")
async def update_location(lat: float, lon: float):
    global location_data
    location_data = {"lat": lat, "lon": lon}
    return {"status": "Location updated"}

if __name__ == "__main__":
    uvicorn.run("server:app", port=8000, reload=True)
