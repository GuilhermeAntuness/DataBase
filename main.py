import uvicorn
from fastapi import FastAPI
from database import engine, Base
from app.routers import book as b, empresa as e, cargo as c, emprestimo as em, pessoa as p




Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


app = FastAPI()

@app.get("/")
def check_api():
    return {"Response":"Api Online!"}

app.include_router(em.router)
app.include_router(b.router)
app.include_router(p.router)
app.include_router(c.router)
app.include_router(e.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)