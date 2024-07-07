from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request

# ROUTERS
from .src.routers import users_router
from .src.routers import clubs_router
from .src.routers import categories_router

app = FastAPI()
app.include_router(users_router.router)
app.include_router(clubs_router.router)
app.include_router(categories_router.router)

@app.get("/")
def read_root():
    return JSONResponse(
        content={"message": "Welcome to the API"},
        status_code=200
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
    status_code=500,
        content= {
        "title": "Internal Server Error",
            "message": str(exc)
        }
    )