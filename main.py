import fastapi
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from api import asterisk_caller, asterisk_events

app = fastapi.FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(asterisk_caller.router)
app.include_router(asterisk_events.router)

if __name__ == '__main__':
    uvicorn.run("main:app", port=8000, host='0.0.0.0', reload=True)
