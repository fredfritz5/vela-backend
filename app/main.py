from fastapi import FastAPI
from app.daraja.callbacks import router as daraja_router
from app.daraja.routes import router as pay_router


app = FastAPI(title="Vela API", version="1.0.0")
app.include_router(daraja_router)
app.include_router(pay_router)


@app.get("/healthz")
def health_check():
    return {"status": "ok", "service": "vela-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
