from fastapi import FastAPI, HTTPException, Depends
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from httpx import AsyncClient
from dotenv import load_dotenv
import os
import DB

load_dotenv()

app = FastAPI()

async def get_external_data(api_key: str = os.getenv("API_KEY")):
    async with AsyncClient() as client:
        try:
            response = await client.get(api_key)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch data: {e}")

@app.get("/fetch_data")
async def fetch_data():
    data = await get_external_data()
    return data

@app.post("/post_data")
async def post_data(data: dict):
    connection = DB.connect_to_database()
    cursor = connection.cursor()
    cursor.append(fetch_data())
    return {"message": "Data added to database successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
