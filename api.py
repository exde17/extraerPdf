
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

        # Si la línea contiene ":" la trato como un posible par clave:valor
        if ':' in line:
            parts = line.split(':', 1)
            key = parts[0].strip().lower()  # normalizamos la clave
            value = parts[1].strip()

            # Si ya existe la clave, convierto el valor a lista para almacenar varios elementos
            if key in extracted_data:
                if isinstance(extracted_data[key], list):
                    extracted_data[key].append(value)
                else:
                    extracted_data[key] = [extracted_data[key], value]
            else:
                extracted_data[key] = value

            last_key = key  # Guardo la clave actual para posibles líneas adicionales
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
    uvicorn.run(app, host="0.0.0.0", port=8001)
 