import uvicorn

from config import Config
from app.main import app

uvicorn.run(app, host=Config.URL, port=Config.PORT)
