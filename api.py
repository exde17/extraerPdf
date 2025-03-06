# from fastapi import FastAPI, File, UploadFile
# from fastapi.responses import JSONResponse, FileResponse
# import fitz  # PyMuPDF
# import os
# from datetime import datetime
# from fastapi.middleware.cors import CORSMiddleware


# app = FastAPI()

# # ✅ Habilitar CORS para permitir peticiones desde cualquier frontend
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Permite cualquier origen (puedes restringirlo a un dominio específico)
#     allow_credentials=True,
#     allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
#     allow_headers=["*"],  # Permite todos los headers
# )

# # Carpeta donde se guardarán los archivos procesados
# OUTPUT_DIR = "output_files"
# os.makedirs(OUTPUT_DIR, exist_ok=True)

# def extract_text_from_pdf(pdf_path):
#     """Extrae texto de cada página del PDF y lo devuelve en una estructura organizada."""
#     try:
#         doc = fitz.open(pdf_path)
#         text_data = []

#         # Recorremos cada página y extraemos su contenido
#         for page_num, page in enumerate(doc, start=1):
#             page_text = page.get_text("text")
#             text_data.append({"page": page_num, "content": page_text})

#         return text_data, len(doc)  # Retornamos el texto y el número de páginas
#     except Exception as e:
#         return str(e), 0

# @app.post("/extract-text/")
# async def extract_text_from_uploaded_pdf(file: UploadFile = File(...)):
#     """Endpoint para extraer texto de un PDF y devolverlo en JSON estructurado y como archivo .txt."""
    
#     # Guardar el archivo temporalmente
#     pdf_path = f"{OUTPUT_DIR}/{file.filename}"
#     with open(pdf_path, "wb") as f:
#         f.write(await file.read())

#     # Extraer texto y número de páginas
#     extracted_text, num_pages = extract_text_from_pdf(pdf_path)

#     # Guardar el texto extraído en un archivo .txt
#     txt_filename = file.filename.replace(".pdf", ".txt")
#     txt_path = f"{OUTPUT_DIR}/{txt_filename}"
#     with open(txt_path, "w", encoding="utf-8") as txt_file:
#         for page_data in extracted_text:
#             txt_file.write(f"--- Página {page_data['page']} ---\n")
#             txt_file.write(page_data["content"] + "\n\n")

#     # Respuesta JSON organizada
#     return JSONResponse(content={
#         "message": "Texto extraído con éxito",
#         "document": {
#             "filename": file.filename,
#             "pages": num_pages,
#             "extracted_text": extracted_text
#         },
#         "metadata": {
#             "created_at": datetime.utcnow().isoformat() + "Z",
#             "processed_by": "FastAPI PDF Extractor"
#         },
#         "download_link": f"/download/{txt_filename}"
#     })

# @app.get("/download/{filename}")
# async def download_txt(filename: str):
#     """Endpoint para descargar el archivo de texto extraído."""
#     file_path = f"{OUTPUT_DIR}/{filename}"
#     if os.path.exists(file_path):
#         return FileResponse(file_path, media_type="text/plain", filename=filename)
#     return JSONResponse(content={"error": "Archivo no encontrado"}, status_code=404)

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
import fitz  # PyMuPDF
import os
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
import re

app = FastAPI()

# ✅ Habilitar CORS para permitir peticiones desde cualquier frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite cualquier origen (puedes restringirlo a un dominio específico)
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los headers
)

# Carpeta donde se guardarán los archivos procesados
OUTPUT_DIR = "output_files"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def parse_pdf_text(text):
    """Extrae información estructurada del texto del PDF."""
    extracted_data = {}

    # 🔹 Extraer datos generales
    extracted_data["acta"] = re.search(r"Acta:(\d+)", text).group(1) if re.search(r"Acta:(\d+)", text) else None
    extracted_data["cliente"] = re.search(r"Cliente:(.+)", text).group(1).strip() if re.search(r"Cliente:(.+)", text) else None
    extracted_data["direccion"] = re.search(r"Dirección:(.+)", text).group(1).strip() if re.search(r"Dirección:(.+)", text) else None
    extracted_data["fecha_revision"] = re.search(r"Fecha revisión:\s*(.+)", text).group(1).strip() if re.search(r"Fecha revisión:\s*(.+)", text) else None
    extracted_data["inspector"] = re.search(r"Revisó:(.+)", text).group(1).strip() if re.search(r"Revisó:(.+)", text) else None
    extracted_data["municipio"] = re.search(r"Municipio:(.+)", text).group(1).strip() if re.search(r"Municipio:(.+)", text) else None

    # 🔹 Extraer información sobre el medidor
    medidor_instalado = re.search(r"MEDIDOR ENERGÍA Instalado\*\* NUEVO \*\*(.+?)Ubicación:", text, re.DOTALL)
    medidor_retirado = re.search(r"MEDIDOR ENERGÍA Retirado(.+?)Ubicación:", text, re.DOTALL)

    extracted_data["medidor_instalado"] = medidor_instalado.group(1).strip() if medidor_instalado else None
    extracted_data["medidor_retirado"] = medidor_retirado.group(1).strip() if medidor_retirado else None

    # 🔹 Extraer equipos eléctricos revisados
    equipos = []
    equipos_regex = re.findall(r"(Bombillo Ahorrador|Nevera|Televisor|Licuadora)\s+(\d+)\s+(\d+)\s+(.+)", text)
    for equipo in equipos_regex:
        equipos.append({
            "nombre": equipo[0],
            "cantidad": int(equipo[1]),
            "potencia_w": int(equipo[2]),
            "uso": equipo[3].strip()
        })
    extracted_data["equipos_revisados"] = equipos

    # 🔹 Extraer los sellos inspeccionados
    sellos = []
    sellos_regex = re.findall(r"(Sello.+?)\s+(Instalado|Revisado)\s+(\d+)\s+ESSA\s+(.+?)\s+(.+?)\s+(.+)", text)
    for sello in sellos_regex:
        sellos.append({
            "tipo": sello[0],
            "estado": sello[1],
            "codigo": sello[2],
            "color": sello[3],
            "descripcion": sello[4],
            "ubicacion": sello[5]
        })
    extracted_data["sellos"] = sellos

    # 🔹 Extraer situación encontrada y observaciones
    extracted_data["situacion_encontrada"] = re.search(r"Situación Encontrada\s+(.+)", text).group(1).strip() if re.search(r"Situación Encontrada\s+(.+)", text) else None
    extracted_data["observaciones"] = re.search(r"Observación:\s+(.+)", text).group(1).strip() if re.search(r"Observación:\s+(.+)", text) else None

    # 🔹 Extraer el total de materiales no facturados
    total_materiales = re.search(r"TOTAL\s+([\d,.]+)", text)
    extracted_data["total_materiales"] = float(total_materiales.group(1).replace(",", "")) if total_materiales else None

    return extracted_data

def extract_text_from_pdf(pdf_path):
    """Extrae texto de cada página del PDF y lo devuelve en una estructura organizada."""
    try:
        doc = fitz.open(pdf_path)
        extracted_pages = []

        # Recorremos cada página y extraemos su contenido
        for page_num, page in enumerate(doc, start=1):
            page_text = page.get_text("text")
            structured_data = parse_pdf_text(page_text)  # Procesa el texto extraído
            extracted_pages.append({"page": page_num, "content": structured_data})

        return extracted_pages, len(doc)  # Retornamos el texto estructurado y el número de páginas
    except Exception as e:
        return str(e), 0

@app.post("/extract-text/")
async def extract_text_from_uploaded_pdf(file: UploadFile = File(...)):
    """Endpoint para extraer texto de un PDF y devolverlo en JSON estructurado y como archivo .txt."""

    # Guardar el archivo temporalmente
    pdf_path = f"{OUTPUT_DIR}/{file.filename}"
    with open(pdf_path, "wb") as f:
        f.write(await file.read())

    # Extraer texto y número de páginas
    extracted_text, num_pages = extract_text_from_pdf(pdf_path)

    # Guardar el texto extraído en un archivo .json
    json_filename = file.filename.replace(".pdf", ".json")
    json_path = f"{OUTPUT_DIR}/{json_filename}"
    with open(json_path, "w", encoding="utf-8") as json_file:
        import json
        json.dump(extracted_text, json_file, indent=4, ensure_ascii=False)

    # Respuesta JSON organizada
    return JSONResponse(content={
        "message": "Texto extraído con éxito",
        "document": {
            "filename": file.filename,
            "pages": num_pages,
            "extracted_text": extracted_text
        },
        "metadata": {
            "created_at": datetime.utcnow().isoformat() + "Z",
            "processed_by": "FastAPI PDF Extractor"
        },
        "download_link": f"/download/{json_filename}"
    })

@app.get("/download/{filename}")
async def download_txt(filename: str):
    """Endpoint para descargar el archivo de texto extraído."""
    file_path = f"{OUTPUT_DIR}/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/json", filename=filename)
    return JSONResponse(content={"error": "Archivo no encontrado"}, status_code=404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
