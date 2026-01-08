from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import shutil
import tempfile

# Import Prometheus (giả sử bạn copy pol.py vào cùng folder, hoặc adjust path)
from pol import deobfuscate  # Function chính từ Prometheus (sửa nếu cần)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")  # Nếu có CSS/JS

templates = Jinja2Templates(directory="templates")  # Folder cho HTML templates

# Trang chủ với form upload
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Handle upload và deob
@app.post("/deobfuscate")
async def process_file(file: UploadFile = File(...), mode: str = Form("dev")):  # Mode: "dev" (bytecode) hoặc "dis" (disassembly) – nhưng Prometheus default xuất source
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, file.filename)
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Gọi deobfuscate từ Prometheus (nó xuất string source, mình save thành file)
        deob_content = deobfuscate(input_path)  # Giả sử function trả string source clean
        output_path = os.path.join(tmpdir, "deobfuscated.lua")
        with open(output_path, "w") as f:
            f.write(deob_content)

        # Trả về file để tải
        return FileResponse(output_path, media_type="application/octet-stream", filename="deobfuscated.lua")

# Để test local: uvicorn main:app --reload
