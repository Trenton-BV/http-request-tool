from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import httpx
import uvicorn
from typing import Dict, Any, Optional
import json
import os

app = FastAPI()

# Create static directory if it doesn't exist
os.makedirs("static", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class RequestData(BaseModel):
    method: str
    url: str
    headers: Optional[Dict[str, str]] = {}
    body: Optional[Dict[str, Any]] = {}

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/request")
async def make_request(request_data: RequestData):
    method = request_data.method.lower()
    url = request_data.url
    headers = request_data.headers or {}
    body = request_data.body

    if not url.startswith(('http://', 'https://')):
        url = f"http://{url}"

    try:
        async with httpx.AsyncClient(verify=False) as client:
            if method == 'get':
                response = await client.get(url, headers=headers, params=body)
            elif method == 'post':
                response = await client.post(url, headers=headers, json=body)
            elif method == 'put':
                response = await client.put(url, headers=headers, json=body)
            elif method == 'delete':
                response = await client.delete(url, headers=headers, json=body)
            else:
                response = await client.request(method, url, headers=headers, json=body)

            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.text
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
