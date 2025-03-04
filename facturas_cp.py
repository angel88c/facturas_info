import streamlit as st
import xml.etree.ElementTree as ET
import pandas as pd
import tempfile
import os

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
        "Metodo de pago": None
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

st.set_page_config(page_title="Facturas Info", layout="wide")
st.title("Extractor de datos de Factura")

files = st.file_uploader("Cargue las facturas", accept_multiple_files=True, type="xml")

if files:
    
# load_button = st.button("Load Files")
# if load_button:
    full_info = []
    
    if "temp_dir" not in st.session_state:
        st.session_state["temp_dir"] = tempfile.TemporaryDirectory()
    
    bar = st.progress(0, "Cargando datos...")
    index = 1
    for file in files:
        bar.progress(value=( index / len(files)))
        index = index + 1
        temporal_file_path = os.path.join(st.session_state["temp_dir"].name, file.name)
        with open(temporal_file_path, "wb") as f:
            f.write(file.getbuffer())
            
        info = extract_cfdi_data(temporal_file_path)
        
        full_info.append(info)
    
    bar.empty()
    
    df = pd.DataFrame(full_info)
    df = df.set_index("UUID")
    
   
    #st.write(full_info)
    button = st.button("Copiar al portapapeles", type="primary")
    st.table(df)
    
    if button:
        df.to_clipboard(header=False, excel=True, index=True, sep='\t')
        st.success("La información de las facturas se ha copiado al portapapeles.")