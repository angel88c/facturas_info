import pandas as pd
import json
import chardet

def extract_project_code_by_cfdi(df, cfdi):
    resultado = df[df["Num_Fact"] == cfdi]["Código de proyecto"]
    
    if not resultado.empty:
        return resultado.iloc[0]  # Devolver el primer valor encontrado
    else:
        return ""
    
if __name__ == '__main__':
    
    FILE = "/Users/c_angel/Downloads/Entradas - Facturas 12 marzo.txt"
    #FILE = "requirements.txt"

    encoding_detected = None
    with open(FILE, "rb") as file:
        raw_data = file.read(1000)  # Leer una parte del archivo para detectar la codificación
    encoding_detected = chardet.detect(raw_data)['encoding']
    
    # Leer el archivo de texto y convertirlo en un DataFrame
    with open(FILE, "r", encoding=encoding_detected) as file:
        lines = file.readlines()

    # Extraer los encabezados de la tabla
    titles = lines[0].strip().split("\t")

    # Extraer los datos
    records = [dict(zip(titles, line.strip().split("\t"))) for line in lines[1:]]

    # # Convertir los datos a formato JSON
    # json_output = json.dumps(records, indent=4, ensure_ascii=False)

    # # Guardar en un archivo JSON
    # output_file = "facturas.json"
    # with open(output_file, "w", encoding="utf-8") as json_file:
    #     json_file.write(json_output)

    # print(f"Archivo JSON generado: {output_file}")
    
    # with open(output_file, "r", encoding="utf-8") as file:
    #     data = json.load(file)  # Cargar el JSON como lista de diccionarios

    # Convertir la lista de diccionarios a un DataFrame de pandas
    df = pd.DataFrame(records)
    print(df)
    
    CFDI="0A51ECD5-4548-7F40-A5A1-EC87BDF5171E"
    extracted = extract_project_code_by_cfdi(df, CFDI)
    print(f"Código de proyecto para la factura {CFDI}: {extracted}")