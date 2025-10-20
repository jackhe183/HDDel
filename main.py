from fastapi import FastAPI
import uvicorn

from .apis.HD_lines_del import router as hd_line_del

app = FastAPI()

app.include_router(hd_line_del)

if __name__ == '__main__':
    uvicorn.run(
        "ShenYuanHDDel.main:app",
        host="0.0.0.0",
        port=8005,
        reload=True
    )