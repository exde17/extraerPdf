import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path, output_txt_path):
    try:
        # Abre el archivo PDF
        doc = fitz.open(pdf_path)
        text = ""

        # Extrae el texto de cada página
        for page in doc:
            text += page.get_text("text") + "\n"

        # Guarda el texto en un archivo
        with open(output_txt_path, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"Texto extraído y guardado en {output_txt_path}")
    except Exception as e:
        print(f"Error al procesar el PDF: {e}")

# Ejemplo de uso
pdf_path = r"C:\Users\user1\Documents\comprobante de pago Mario .pdf"
output_txt_path = "texto_extraido.txt"
extract_text_from_pdf(pdf_path, output_txt_path)
