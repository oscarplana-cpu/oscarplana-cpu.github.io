"""Convierte el resultado de la exportación a PDF de un doc (JSON con el PDF en base64) en un archivo .pdf.
Uso: python3 pdf_de_export.py <resultado.txt> <salida.pdf>"""
import base64, json, sys
d = json.loads(open(sys.argv[1]).read())
def buscar(o):
    if isinstance(o, dict):
        for v in o.values():
            if isinstance(v, str) and len(v) > 10000: return v
            r = buscar(v)
            if r: return r
    if isinstance(o, list):
        for v in o:
            r = buscar(v)
            if r: return r
open(sys.argv[2], "wb").write(base64.b64decode(buscar(d)))
print(sys.argv[2], d.get("data", {}).get("pages"), "páginas")
