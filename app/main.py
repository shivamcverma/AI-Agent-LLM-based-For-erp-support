from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.routes import health, chat
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(
    title="ERP AI Agent",
    description="AI Agent for School ERP",
    version="1.0.0"
)





@app.get("/") 
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

# Static files
app.mount(
    "/static",
    StaticFiles(directory="frontend/static"),
    name="static"
)

# Templates
templates = Jinja2Templates(directory="frontend/templates")


# API routes
app.include_router(health.router,prefix="/api")

app.include_router(chat.router,prefix="/api")