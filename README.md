# FastAPI PDF Dynamic Extractor

Este proyecto implementa una API utilizando **FastAPI** para extraer información de archivos PDF de manera dinámica. La API recibe un archivo PDF, extrae su texto y procesa los datos en formato `clave: valor`, adaptándose a la estructura de cada PDF.

## Estructura del Código

### 1. **Importación de librerías**

```python
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import fitz  # PyMuPDF
import os
from fastapi.middleware.cors import CORSMiddleware
FastAPI: Framework para crear APIs de forma rápida y eficiente.
File y UploadFile: Tipos de datos de FastAPI que nos permiten manejar archivos cargados por el cliente.
JSONResponse: Respuesta que devuelve datos en formato JSON.
fitz (PyMuPDF): Librería que se usa para leer y procesar PDFs.
os: Para interactuar con el sistema de archivos.
CORSMiddleware: Middleware de FastAPI que habilita el CORS (Cross-Origin Resource Sharing), lo que permite que la API pueda ser consumida por clientes de diferentes dominios (en este caso, cualquier cliente).
2. Inicialización de FastAPI
python
Copiar
app = FastAPI(title="PDF Dynamic Extractor API", description="Extrae información de PDFs de forma dinámica")
Se crea una instancia de FastAPI con el título y la descripción para la documentación automática que FastAPI genera.

3. Configuración de CORS
python
Copiar
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite peticiones desde cualquier dominio
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos HTTP
    allow_headers=["*"],  # Permite todos los headers
)
CORS (Cross-Origin Resource Sharing): Permite que el navegador haga peticiones a servidores que no están en el mismo dominio.
En este caso, se habilitan todas las solicitudes desde cualquier origen (allow_origins=["*"]), lo que significa que cualquier cliente puede acceder a la API.
4. Carpeta para guardar los archivos
python
Copiar
OUTPUT_DIR = "output_files"
os.makedirs(OUTPUT_DIR, exist_ok=True)
Se crea un directorio llamado output_files donde se guardarán temporalmente los archivos PDF recibidos.
os.makedirs(OUTPUT_DIR, exist_ok=True) asegura que el directorio se cree solo si no existe.

5. Función para procesar el texto extraído del PDF
python
Copiar
def dynamic_parse_pdf_text(text: str) -> dict:
    extracted_data = {}
    lines = text.splitlines()
    last_key = None

    for line in lines:
        line = line.strip()
        if not line:
            continue
Esta función toma el texto extraído de un PDF y lo procesa línea por línea para intentar extraer "pares clave-valor".
Se separan las líneas utilizando splitlines() para iterar sobre ellas.

Procesamiento de las líneas
python
Copiar
        if ':' in line:
            parts = line.split(':', 1)
            key = parts[0].strip().lower()  # Normalizamos la clave
            value = parts[1].strip()
Si una línea contiene dos puntos (:), se trata de un par clave-valor. Se divide la línea en key y value (clave y valor), y se normaliza la clave a minúsculas.

python
Copiar
            if key in extracted_data:
                if isinstance(extracted_data[key], list):
                    extracted_data[key].append(value)
                else:
                    extracted_data[key] = [extracted_data[key], value]
            else:
                extracted_data[key] = value
Si la clave ya existe en el diccionario extracted_data, el valor se agrega a una lista. Si la clave no existe, se crea una nueva entrada en el diccionario.

Concatenación de líneas sin clave: valor
python
Copiar
        else:
            if last_key:
                if isinstance(extracted_data[last_key], list):
                    extracted_data[last_key][-1] += " " + line
                else:
                    extracted_data[last_key] += " " + line
            else:
                if "content" in extracted_data:
                    extracted_data["content"].append(line)
                else:
                    extracted_data["content"] = [line]
Si una línea no contiene un :, se concatena a la clave previa (si existe). Si no hay clave previa, se almacena el contenido bajo una clave genérica content.

6. Endpoint de FastAPI para extraer texto del PDF
python
Copiar
@app.post("/extract-dynamic/")
async def extract_dynamic_pdf(file: UploadFile = File(...)):
    pdf_path = os.path.join(OUTPUT_DIR, file.filename)
    with open(pdf_path, "wb") as f:
        f.write(await file.read())
Endpoint /extract-dynamic/: Este endpoint recibe un archivo PDF mediante una petición POST.
El archivo se guarda temporalmente en el directorio output_files con el nombre original del archivo.

python
Copiar
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text("text") + "\n"
Se utiliza la librería PyMuPDF (fitz) para abrir el PDF y extraer todo el texto de cada página. El texto de todas las páginas se concatena en full_text.

python
Copiar
    extracted_data = dynamic_parse_pdf_text(full_text)
    return JSONResponse(content=extracted_data)
El texto extraído del PDF se pasa a la función dynamic_parse_pdf_text para procesarlo y se devuelve como una respuesta en formato JSON.

7. Ejecutar el servidor
python
Copiar
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
Si el archivo se ejecuta directamente, se inicia el servidor utilizando Uvicorn en el puerto 8000. Esto hace que la API esté disponible en http://127.0.0.1:8000.

Flujo del código
El cliente envía un archivo PDF a través de una solicitud POST al endpoint /extract-dynamic/.
El servidor guarda el archivo, extrae el texto utilizando PyMuPDF, lo procesa para extraer claves y valores dinámicamente y devuelve el resultado como un JSON.
El cliente recibe el JSON con los datos extraídos del PDF.