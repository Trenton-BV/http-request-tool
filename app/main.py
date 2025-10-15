from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import httpx
import uvicorn
from typing import Dict, Any, Optional, List
import json
import os
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, desc
from database import Base, RequestHistory, DATABASE_URL
import time

app = FastAPI()

# Create static directory if it doesn't exist
os.makedirs("static", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Database setup
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

class RequestData(BaseModel):
    method: str
    url: str
    headers: Optional[Dict[str, str]] = {}
    body: Optional[Dict[str, Any]] = {}

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/request")
async def make_request(request_data: RequestData, db: AsyncSession = Depends(get_db)):
    method = request_data.method.lower()
    url = request_data.url
    headers = request_data.headers or {}
    body = request_data.body

    if not url.startswith(('http://', 'https://')):
        url = f"http://{url}"

    start_time = time.time()
    error_msg = None
    status_code = None
    response_headers = None
    response_text = None

    try:
        async with httpx.AsyncClient(verify=False, timeout=30.0) as client:
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

            status_code = response.status_code
            response_headers = dict(response.headers)
            response_text = response.text
            
            result = {
                "status_code": status_code,
                "headers": response_headers,
                "content": response_text
            }
    except Exception as e:
        error_msg = str(e)
        result = {"error": error_msg}
        status_code = 0
    
    # Calculate duration
    duration_ms = int((time.time() - start_time) * 1000)
    
    # Save to database
    try:
        history_entry = RequestHistory(
            method=request_data.method.upper(),
            url=url,
            headers=json.dumps(headers),
            body=json.dumps(body) if body else None,
            status_code=status_code,
            response_headers=json.dumps(response_headers) if response_headers else None,
            response_body=response_text,
            error=error_msg,
            duration_ms=duration_ms
        )
        db.add(history_entry)
        await db.commit()
        await db.refresh(history_entry)
        result["history_id"] = history_entry.id
    except Exception as db_error:
        print(f"Failed to save to database: {db_error}")
    
    if error_msg:
        raise HTTPException(status_code=400, detail=error_msg)
    
    return result

@app.get("/api/history")
async def get_history(limit: int = 50, offset: int = 0, db: AsyncSession = Depends(get_db)):
    """Get request history with pagination"""
    stmt = select(RequestHistory).order_by(desc(RequestHistory.timestamp)).limit(limit).offset(offset)
    result = await db.execute(stmt)
    history = result.scalars().all()
    
    return {
        "items": [item.to_dict() for item in history],
        "limit": limit,
        "offset": offset
    }

@app.get("/api/history/{history_id}")
async def get_history_item(history_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific history item by ID"""
    stmt = select(RequestHistory).where(RequestHistory.id == history_id)
    result = await db.execute(stmt)
    history = result.scalar_one_or_none()
    
    if not history:
        raise HTTPException(status_code=404, detail="History item not found")
    
    return history.to_dict()

@app.delete("/api/history/{history_id}")
async def delete_history_item(history_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a specific history item"""
    stmt = select(RequestHistory).where(RequestHistory.id == history_id)
    result = await db.execute(stmt)
    history = result.scalar_one_or_none()
    
    if not history:
        raise HTTPException(status_code=404, detail="History item not found")
    
    await db.delete(history)
    await db.commit()
    
    return {"message": "History item deleted"}

@app.delete("/api/history")
async def clear_history(db: AsyncSession = Depends(get_db)):
    """Clear all history"""
    await db.execute("DELETE FROM request_history")
    await db.commit()
    
    return {"message": "History cleared"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
