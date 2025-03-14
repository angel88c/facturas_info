import streamlit as st
import xml.etree.ElementTree as ET
import pandas as pd
import tempfile
import os
import chardet

def extract_project_code_by_cfdi(df, cfdi):
    cfdi = cfdi.upper()
    resultado = df[df["Ref_Entrada"] == cfdi]["Código de proyecto"]
    
    #if resultado.empty:
    #    resultado = df[df["Ref_Entrada"] == cfdi]["Código de proyecto"]
    
    if resultado.empty:
        return ""
    
    return resultado.iloc[0]  # Devolver el primer valor encontrado
    

def extract_cfdi_data(xml_path):
    namespaces = {
        "cfdi": "http://www.sat.gob.mx/cfd/4",
        "tfd": "http://www.sat.gob.mx/TimbreFiscalDigital"
    }

    tree = ET.parse(xml_path)
    root = tree.getroot()

    data = {
        "UUID": None,
        "Razon Social": None,
        "Total": None,
        "Moneda": None,
        "1": "",
        "Fecha de factura": None,
        "2": "",
        "3": "",
        "4": "",
        "5": "",
        "6": "",
        "7": "",
        "8": "",
        "9": "",
        "10":"",
        "Metodo de pago": None,
        "11": "",
        "BU": "",
        "Codigo de proyecto": ""
    }

    # Extraer UUID del Timbre Fiscal
    complemento = root.find(".//cfdi:Complemento", namespaces)
    if complemento is not None:
        timbre = complemento.find(".//tfd:TimbreFiscalDigital", namespaces)
        if timbre is not None:
            data["UUID"] = timbre.get("UUID", "").strip()

    # Extraer datos del Comprobante (Total, Fecha, Método de pago)
    comprobante = root
    data["Total"] = comprobante.get("Total", "").strip()
    fecha_completa = comprobante.get("Fecha", "").strip()
    if fecha_completa:
        fecha_partes = fecha_completa.split("T")[0].split("-")
        if len(fecha_partes) == 3:
            año, mes, dia = fecha_partes
            data["Fecha de factura"] = f"{dia}-{mes}-{año}".strip()
        else:
            data["Fecha de factura"] = ""  # Formato inválido
    else:
        data["Fecha de factura"] = ""  # Fecha no encontrada
    data["Metodo de pago"] = comprobante.get("MetodoPago", "").strip()
    data["Moneda"] = comprobante.get("Moneda", "").strip()

    # Extraer Razón Social del Emisor
    emisor = root.find(".//cfdi:Emisor", namespaces)
    if emisor is not None:
        data["Razon Social"] = emisor.get("Nombre", "").strip()

    return data

df = None

if "temp_dir" not in st.session_state:
    st.session_state["temp_dir"] = tempfile.TemporaryDirectory()
        
st.set_page_config(page_title="Facturas Info", layout="wide")
st.title("Extractor de datos de Factura")

txt_file = st.file_uploader("Cargue el archivo TXT")
if txt_file:
    
    FILE = os.path.join(st.session_state["temp_dir"].name, txt_file.name)
    with open(FILE, "wb") as f:
        f.write(txt_file.getbuffer())

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
    st.success("Archivo txt cargado correctamente")

files = st.file_uploader("Cargue las facturas", accept_multiple_files=True, type="xml")

if files:
    
# load_button = st.button("Load Files")
# if load_button:
    full_info = []
    
    bar = st.progress(0, "Cargando datos...")
    index = 1
    for file in files:
        bar.progress(value=( index / len(files)))
        index = index + 1
        temporal_file_path = os.path.join(st.session_state["temp_dir"].name, file.name)
        with open(temporal_file_path, "wb") as f:
            f.write(file.getbuffer())
            
        info = extract_cfdi_data(temporal_file_path)
        uuid = info["UUID"]
        st.write(uuid)
        if uuid and df is not None:
            info["Codigo de proyecto"] = extract_project_code_by_cfdi(df, uuid)
            info["BU"] = info["Codigo de proyecto"][:3]
        
        full_info.append(info)
    
    bar.empty()
    
    df = pd.DataFrame(full_info)
    df = df.set_index("UUID")
    
    #st.text_area("Copy this data", df.to_string())
    #styled_df = df.style.set_properties(**{'font-size': '12pt'})
    #st.markdown(styled_df.to_html(), unsafe_allow_html=True)
    st.write(df)
    #button = st.button("Copiar al portapapeles", type="primary")
    #st.table(df)
    
    #if button:
    #df.to_clipboard(header=False, excel=True, index=True, sep='\t')
    #styled_df = df.style.set_properties(**{'font-size': '12pt'})
    #st.markdown(styled_df.to_html(), unsafe_allow_html=True)
    #st.success("La información de las facturas se ha copiado al portapapeles.")        