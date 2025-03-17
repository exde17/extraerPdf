

# /////////////////////////////////////////////////////////////////

# from fastapi import FastAPI, File, UploadFile
# from fastapi.responses import JSONResponse, FileResponse
# import fitz  # PyMuPDF
# import os
# from datetime import datetime
# from fastapi.middleware.cors import CORSMiddleware
# import re
# import json

# app = FastAPI()

# # Habilitar CORS para permitir peticiones desde cualquier origen
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Carpeta donde se guardarán los archivos procesados
# OUTPUT_DIR = "output_files"
# os.makedirs(OUTPUT_DIR, exist_ok=True)

# def parse_pdf_text(text):
#     """Extrae información estructurada del texto del PDF, incluyendo el texto completo."""
#     extracted_data = {}
    
#     # Guardar el texto completo para referencia
#     extracted_data["full_text"] = text

#     # 🔹 Extraer datos generales de forma flexible
#     acta_match = re.search(r"Acta:\s*(\d+)", text)
#     extracted_data["acta"] = acta_match.group(1) if acta_match else None

#     cliente_match = re.search(r"Cliente:\s*(.+)", text)
#     extracted_data["cliente"] = cliente_match.group(1).strip() if cliente_match else None

#     direccion_match = re.search(r"Dirección:\s*(.+)", text)
#     extracted_data["direccion"] = direccion_match.group(1).strip() if direccion_match else None

#     fecha_revision_match = re.search(r"Fecha revisión:\s*(.+)", text)
#     extracted_data["fecha_revision"] = fecha_revision_match.group(1).strip() if fecha_revision_match else None

#     inspector_match = re.search(r"Revisó:\s*(.+)", text)
#     extracted_data["inspector"] = inspector_match.group(1).strip() if inspector_match else None

#     municipio_match = re.search(r"Municipio:\s*(.+)", text)
#     extracted_data["municipio"] = municipio_match.group(1).strip() if municipio_match else None

#     # 🔹 Extraer información sobre el medidor con mayor flexibilidad
#     medidor_instalado = re.search(
#         r"MEDIDOR ENERG[IÍ]A\s+Instalado\*\*\s*NUEVO\s*\*\*\s*(.+?)Ubicación:", 
#         text, re.DOTALL | re.IGNORECASE
#     )
#     extracted_data["medidor_instalado"] = medidor_instalado.group(1).strip() if medidor_instalado else None

#     medidor_retirado = re.search(
#         r"MEDIDOR ENERG[IÍ]A\s+Retirado\s*(.+?)Ubicación:", 
#         text, re.DOTALL | re.IGNORECASE
#     )
#     extracted_data["medidor_retirado"] = medidor_retirado.group(1).strip() if medidor_retirado else None

#     # 🔹 Extraer equipos eléctricos revisados
#     equipos = []
#     equipos_regex = re.findall(
#         r"(Bombillo Ahorrador|Nevera|Televisor|Licuadora)\s+(\d+)\s+(\d+)\s+(.+)",
#         text, re.IGNORECASE
#     )
#     for equipo in equipos_regex:
#         equipos.append({
#             "nombre": equipo[0],
#             "cantidad": int(equipo[1]),
#             "potencia_w": int(equipo[2]),
#             "uso": equipo[3].strip()
#         })
#     extracted_data["equipos_revisados"] = equipos

#     # 🔹 Extraer los sellos inspeccionados
#     sellos = []
#     # Se utiliza un patrón más general para capturar información de sellos
#     sellos_regex = re.findall(
#         r"(Sello\s*\([^)]+\))\s+(Instalado|Revisado|Retirado)\s+(\d+)\s+ESSA\s+(\w+)\s+([\w\s]+?)\s+([\w\s]+)(?:\s|$)",
#         text, re.IGNORECASE
#     )
#     for sello in sellos_regex:
#         sellos.append({
#             "tipo": sello[0].strip(),
#             "estado": sello[1].strip(),
#             "codigo": sello[2].strip(),
#             "color": sello[3].strip(),
#             "descripcion": sello[4].strip(),
#             "ubicacion": sello[5].strip()
#         })
#     extracted_data["sellos"] = sellos

#     # 🔹 Extraer situación encontrada y observaciones, permitiendo capturar varias líneas
#     situacion_match = re.search(r"Situación Encontrada\s*(.+?)(?=\n\s*\n|$)", text, re.DOTALL)
#     extracted_data["situacion_encontrada"] = situacion_match.group(1).strip() if situacion_match else None

#     observacion_match = re.search(r"Observación:\s*(.+?)(?=\n\s*\n|$)", text, re.DOTALL)
#     extracted_data["observaciones"] = observacion_match.group(1).strip() if observacion_match else None

#     # 🔹 Extraer el total de materiales no facturados (capturando números con comas o puntos)
#     total_materiales_match = re.search(r"TOTAL\s+([\d.,]+)", text)
#     if total_materiales_match:
#         try:
#             extracted_data["total_materiales"] = float(total_materiales_match.group(1).replace(",", ""))
#         except ValueError:
#             extracted_data["total_materiales"] = None
#     else:
#         extracted_data["total_materiales"] = None

#     return extracted_data

# def extract_text_from_pdf(pdf_path):
#     """Extrae el texto completo y lo estructura por página."""
#     try:
#         doc = fitz.open(pdf_path)
#         extracted_pages = []

#         # Recorremos cada página, obtenemos el texto completo y aplicamos la extracción estructurada
#         for page_num, page in enumerate(doc, start=1):
#             page_text = page.get_text("text")
#             structured_data = parse_pdf_text(page_text)
#             extracted_pages.append({
#                 "page": page_num,
#                 "raw_text": page_text,
#                 "content": structured_data
#             })

#         return extracted_pages, len(doc)
#     except Exception as e:
#         return str(e), 0
    
# @app.post("/extract-text/")
# async def extract_text_from_uploaded_pdf(file: UploadFile = File(...)):
#     """Endpoint para extraer texto de un PDF y devolverlo en JSON estructurado junto con el texto completo."""
#     pdf_path = f"{OUTPUT_DIR}/{file.filename}"
#     with open(pdf_path, "wb") as f:
#         f.write(await file.read())

#     extracted_text, num_pages = extract_text_from_pdf(pdf_path)

#     json_filename = file.filename.replace(".pdf", ".json")
#     json_path = f"{OUTPUT_DIR}/{json_filename}"
#     with open(json_path, "w", encoding="utf-8") as json_file:
#         json.dump(extracted_text, json_file, indent=4, ensure_ascii=False)

#     return JSONResponse(content={
#         "message": "Texto extraído con éxito",
#         "document": {
#             "filename": file.filename,
#             "pages": num_pages,
#             "extracted_text": {
#                 "pages": extracted_text,
#                 "summary": {
#                     "total_pages": num_pages,
#                     "processed_by": "FastAPI PDF Extractor",
#                     "created_at": datetime.utcnow().isoformat() + "Z"
#                 }
#             }
#         },
#         "download_link": f"/download/{json_filename}"
#     })

# @app.get("/download/{filename}")
# async def download_txt(filename: str):
#     """Endpoint para descargar el archivo JSON generado."""
#     file_path = f"{OUTPUT_DIR}/{filename}"
#     if os.path.exists(file_path):
#         return FileResponse(file_path, media_type="application/json", filename=filename)
#     return JSONResponse(content={"error": "Archivo no encontrado"}, status_code=404)

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

# ////////////////////////////////////////////////////////7

# from fastapi import FastAPI, File, UploadFile
# from fastapi.responses import JSONResponse, FileResponse
# import fitz  # PyMuPDF
# import os
# from datetime import datetime
# from fastapi.middleware.cors import CORSMiddleware
# import re
# import json

# app = FastAPI(
#     title="PDF Extractor API",
#     description="Servicio para extraer datos estructurados de PDFs con extracción estricta"
# )

# # Habilitar CORS para permitir peticiones desde cualquier origen
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Carpeta donde se guardarán los archivos procesados
# OUTPUT_DIR = "output_files"
# os.makedirs(OUTPUT_DIR, exist_ok=True)

# def parse_pdf_text(text):
#     """Extrae información estructurada del texto del PDF de forma estricta,
#     usando anclajes y patrones precisos para evitar capturar datos erróneos."""
#     extracted_data = {}
    
#     # --- Datos Generales ---
#     # Acta (se espera que la línea contenga solo "Acta: <número>")
#     acta_match = re.search(r"^Acta:\s*(\d+)\s*$", text, re.MULTILINE)
#     extracted_data["numero_acta"] = acta_match.group(1) if acta_match else None

#     # Cliente: se espera el formato "Cliente: <código> <nombre>"
#     cliente_match = re.search(r"^Cliente:\s*(\d+)\s+(.+)$", text, re.MULTILINE)
#     if cliente_match:
#         extracted_data["codigo_cliente"] = cliente_match.group(1)
#         extracted_data["nombre_cliente"] = cliente_match.group(2).strip()
#     else:
#         extracted_data["codigo_cliente"] = None
#         extracted_data["nombre_cliente"] = None

#     # Dirección: capturamos únicamente el contenido de la línea
#     direccion_match = re.search(r"^Dirección:\s*(.+)$", text, re.MULTILINE)
#     extracted_data["direccion"] = direccion_match.group(1).strip() if direccion_match else None

#     # Municipio: se espera que esté en una línea con "Municipio:"
#     municipio_match = re.search(r"^Municipio:\s*(.+)$", text, re.MULTILINE)
#     extracted_data["municipio"] = municipio_match.group(1).strip() if municipio_match else None

#     # Fecha de revisión
#     fecha_revision_match = re.search(r"^Fecha revisión:\s*(.+)$", text, re.MULTILINE)
#     extracted_data["fecha_revision"] = fecha_revision_match.group(1).strip() if fecha_revision_match else None

#     # Inspector (quien revisó)
#     inspector_match = re.search(r"^Revisó:\s*(.+)$", text, re.MULTILINE)
#     extracted_data["inspector"] = inspector_match.group(1).strip() if inspector_match else None

#     # Inicio de la revisión
#     inicio_revision_match = re.search(r"^Inicio Revisión:\s*(.+)$", text, re.MULTILINE)
#     extracted_data["inicio_revision"] = inicio_revision_match.group(1).strip() if inicio_revision_match else None

#     # Usuario/Técnico
#     usuario_tecnico_match = re.search(r"^Nombre Usuario y/o Técnico:\s*(.+)$", text, re.MULTILINE)
#     extracted_data["usuario_tecnico"] = usuario_tecnico_match.group(1).strip() if usuario_tecnico_match else None

#     # Identificación y/o Matrícula
#     identificacion_match = re.search(r"^Identificación y/o Matricula:\s*(.+)$", text, re.MULTILINE)
#     extracted_data["identificacion"] = identificacion_match.group(1).strip() if identificacion_match else None

#     # --- Información del Medidor ---
#     medidor_info = {}
#     # Se espera que tras "MEDIDOR ENERGÍA Revisado" aparezca en la siguiente línea
#     medidor_modelo_match = re.search(r"^MEDIDOR ENERG[IÍ]A\s+Revisado\s*$\n^(.+)$", text, re.MULTILINE)
#     if medidor_modelo_match:
#         modelo_completo = medidor_modelo_match.group(1).strip()
#         if '-' in modelo_completo:
#             parts = modelo_completo.split('-', 1)
#             medidor_info["marca"] = parts[0].strip()
#             medidor_info["modelo"] = parts[1].strip()
#         else:
#             medidor_info["marca"] = modelo_completo
#             medidor_info["modelo"] = None
#     else:
#         medidor_info["marca"] = None
#         medidor_info["modelo"] = None

#     # Serie (se espera un valor sin espacios)
#     serie_match = re.search(r"^Serie #:\s*(\S+)$", text, re.MULTILINE)
#     medidor_info["serie"] = serie_match.group(1).strip() if serie_match else None

#     # Ubicación del medidor
#     ubicacion_match = re.search(r"^Ubicación:\s*(.+)$", text, re.MULTILINE)
#     medidor_info["ubicacion"] = ubicacion_match.group(1).strip() if ubicacion_match else None

#     # Lectura (se espera un número con punto decimal)
#     lectura_match = re.search(r"^Lectura\s+\d+/\w+/\d+\s+(\d+\.\d+)$", text, re.MULTILINE)
#     medidor_info["lectura"] = lectura_match.group(1).strip() if lectura_match else None

#     # Tipo de medida
#     tipo_medida_match = re.search(r"^Medida\(s\):\s*(.+)$", text, re.MULTILINE)
#     medidor_info["tipo_medida"] = tipo_medida_match.group(1).strip() if tipo_medida_match else None

#     # Porcentaje de error
#     error_match = re.search(r"^% ERROR\s+(\d+(?:\.\d+)?)\s*$", text, re.MULTILINE)
#     medidor_info["porcentaje_error"] = error_match.group(1).strip() if error_match else None

#     # Potencias: se espera que las líneas inicien de forma exacta
#     pot_activa_match = re.search(r"^POT\. ACTIVA\s+(\d+(?:\.\d+)?)\s+POT\. REACTIVA", text, re.MULTILINE)
#     medidor_info["potencia_activa"] = pot_activa_match.group(1).strip() if pot_activa_match else None

#     pot_reactiva_match = re.search(r"^POT\. REACTIVA\s+(\d+(?:\.\d+)?)\s+POT\. APARENTE", text, re.MULTILINE)
#     medidor_info["potencia_reactiva"] = pot_reactiva_match.group(1).strip() if pot_reactiva_match else None

#     pot_aparente_match = re.search(r"^POT\. APARENTE\s+(\d+(?:\.\d+)?)\s+FACTOR POT\.", text, re.MULTILINE)
#     medidor_info["potencia_aparente"] = pot_aparente_match.group(1).strip() if pot_aparente_match else None

#     factor_pot_match = re.search(r"^FACTOR POT\.\s+(\d+(?:\.\d+)?)\s+% ERROR", text, re.MULTILINE)
#     medidor_info["factor_potencia"] = factor_pot_match.group(1).strip() if factor_pot_match else None

#     extracted_data["medidor"] = medidor_info

#     # --- Sellos ---
#     # Se espera que cada sello esté en una línea con el formato exacto
#     sellos = []
#     sello_pattern = (
#         r"^Sello\s+\(([^)]+)\)\s+"
#         r"(Instalado|Revisado|Retirado)\s+"
#         r"(\d+)\s+ESSA\s+"
#         r"(\w+)\s+"
#         r"(.+?)\s+"
#         r"(CIERRE\s+MARIPOSA)\s+"
#         r"(Buen Estado|No existe en\s+terreno)\s*$"
#     )
#     for match in re.finditer(sello_pattern, text, re.MULTILINE):
#         sellos.append({
#             "tipo": match.group(1).strip(),
#             "estado": match.group(2).strip(),
#             "codigo": match.group(3).strip(),
#             "color": match.group(4).strip(),
#             "descripcion": match.group(5).strip(),
#             "ubicacion": match.group(6).strip(),
#             "estado_sello": match.group(7).strip()
#         })
#     extracted_data["sellos"] = sellos

#     # --- Aforo (Equipos) ---
#     equipos = []
#     # Se asume que la sección de aforo está delimitada (entre "Aforo" y "Diagrama" o "Materiales a facturar")
#     aforo_section_match = re.search(r"(?<=Aforo)(.*?)(?=Diagrama|Materiales a facturar|$)", text, re.DOTALL)
#     if aforo_section_match:
#         aforo_section = aforo_section_match.group(1)
#         equipo_pattern = r"^([A-Za-zÁ-Úá-ú\s]+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\w+)\s*$"
#         for match in re.finditer(equipo_pattern, aforo_section, re.MULTILINE):
#             equipos.append({
#                 "nombre": match.group(1).strip(),
#                 "cantidad": int(match.group(2)),
#                 "potencia_w": int(match.group(3)),
#                 "horas_uso": int(match.group(4)),
#                 "tipo_uso": match.group(5).strip()
#             })
#     extracted_data["equipos"] = equipos

#     # --- Materiales Facturados ---
#     materiales = []
#     materiales_section_match = re.search(r"(?<=Materiales a facturar)(.*?)(?=^TOTAL\s+\d)", text, re.DOTALL | re.MULTILINE)
#     if materiales_section_match:
#         materiales_section = materiales_section_match.group(1)
#         material_pattern = (
#             r"^([A-ZÁ-Ú\s\d*.\"]+)\s+"
#             r"(\d+)\s+Cantidad\s+"
#             r"([\d,]+)\s+([\d.]+)%\s+"
#             r"(\d+)\s+([\d,]+)\s*$"
#         )
#         for match in re.finditer(material_pattern, materiales_section, re.MULTILINE):
#             try:
#                 materiales.append({
#                     "descripcion": match.group(1).strip(),
#                     "cantidad": int(match.group(2)),
#                     "valor_unitario": float(match.group(3).replace(",", "")),
#                     "iva_porcentaje": float(match.group(4)),
#                     "meses_financiacion": int(match.group(5)),
#                     "valor_total": float(match.group(6).replace(",", ""))
#                 })
#             except Exception:
#                 continue
#     extracted_data["materiales"] = materiales

#     total_match = re.search(r"^TOTAL\s+([\d.,]+)\s*$", text, re.MULTILINE)
#     if total_match:
#         try:
#             extracted_data["total_materiales"] = float(total_match.group(1).replace(",", ""))
#         except ValueError:
#             extracted_data["total_materiales"] = None
#     else:
#         extracted_data["total_materiales"] = None

#     # --- Financiación ---
#     financiacion = {}
#     cuotas_match = re.search(r"^Cuotas:\s+(\d+)\s*$", text, re.MULTILINE)
#     financiacion["cuotas"] = int(cuotas_match.group(1)) if cuotas_match else None 
#     extracted_data["financiacion"] = financiacion

#     return extracted_data

# # Endpoint para recibir el PDF, extraer y devolver la información estrictamente filtrada
# @app.post("/extract-text/")
# async def extract_text_from_pdf(file: UploadFile = File(...)):
#     # Guardar el archivo temporalmente
#     pdf_path = os.path.join(OUTPUT_DIR, file.filename)
#     with open(pdf_path, "wb") as f:
#         f.write(await file.read())
    
#     # Abrir el PDF y extraer el texto completo (todas las páginas)
#     doc = fitz.open(pdf_path)
#     full_text = ""
#     for page in doc:
#         full_text += page.get_text("text") + "\n"
    
#     # Procesar el texto extraído de forma estricta
#     extracted_data = parse_pdf_text(full_text)
    
#     return JSONResponse(content=extracted_data)

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

# /////////////////////////////////////////////////////////////////

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import fitz  # PyMuPDF
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="PDF Dynamic Extractor API", description="Extrae información de PDFs de forma dinámica")

# Habilitar CORS para permitir peticiones desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Carpeta para guardar los archivos
OUTPUT_DIR = "output_files"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def dynamic_parse_pdf_text(text: str) -> dict:
    """
    Procesa el texto de un PDF de forma dinámica.
    Recorre el contenido línea por línea, buscando patrones de 'clave: valor'.
    Si una línea no contiene dos puntos (:) y hay una clave previa, se asume que es parte del valor.
    """
    extracted_data = {}
    lines = text.splitlines()
    last_key = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Si la línea contiene ":" la tratamos como un posible par clave:valor
        if ':' in line:
            parts = line.split(':', 1)
            key = parts[0].strip().lower()  # normalizamos la clave
            value = parts[1].strip()

            # Si ya existe la clave, convertimos el valor a lista para almacenar varios elementos
            if key in extracted_data:
                if isinstance(extracted_data[key], list):
                    extracted_data[key].append(value)
                else:
                    extracted_data[key] = [extracted_data[key], value]
            else:
                extracted_data[key] = value

            last_key = key  # Guardamos la clave actual para posibles líneas adicionales
        else:
            # Si no se encontró ":" y existe una clave previa, se concatena la línea al valor anterior
            if last_key:
                if isinstance(extracted_data[last_key], list):
                    extracted_data[last_key][-1] += " " + line
                else:
                    extracted_data[last_key] += " " + line
            else:
                # Si no hay clave previa, se guarda bajo un campo genérico "content"
                if "content" in extracted_data:
                    extracted_data["content"].append(line)
                else:
                    extracted_data["content"] = [line]

    return extracted_data

@app.post("/extract-dynamic/")
async def extract_dynamic_pdf(file: UploadFile = File(...)):
    # Guarda el PDF de forma temporal
    pdf_path = os.path.join(OUTPUT_DIR, file.filename)
    with open(pdf_path, "wb") as f:
        f.write(await file.read())
    
    # Abre el PDF y extrae el texto completo de todas las páginas
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text("text") + "\n"
    
    # Procesa el texto de forma dinámica
    extracted_data = dynamic_parse_pdf_text(full_text)
    
    return JSONResponse(content=extracted_data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
