import json
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import declarative_base

from app.utils import engine, Base
from config import Config

from starlette.requests import Request
from app.orders.routes import router as order_routes
from app.couriers.routes import router as couriers_routes

app = FastAPI(title=Config.APP_NAME, description=Config.APP_DESC)
app.include_router(order_routes)
app.include_router(couriers_routes)

Base.metadata.create_all(bind=engine)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error = json.loads(exc.json())
    path = str(request.url).rsplit("/", 1)[1]

    if path == "couriers":
        res = {
            "validation_error": {
                "couriers": [
                    {"id": exc.body["data"][id["loc"][2]]["courier_id"]} for id in error
                ]
            }
        }
    elif path == "orders":
        res = {
            "validation_error": {
                "orders": [
                    {"id": exc.body["data"][id["loc"][2]]["order_id"]} for id in error
                ]
            }
        }

    return JSONResponse(res, status_code=400)

