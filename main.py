import uvicorn
from fastapi import FastAPI
from database import engine, Base
from app.routers import empresa, emprestimo, cargo
from app import models




Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


app = FastAPI()

@app.get("/")
def check_api():
    return {"Response":"Api Online!"}

app.include_router(empresa.router)
app.include_router(emprestimo.router)
app.include_router(cargo.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)