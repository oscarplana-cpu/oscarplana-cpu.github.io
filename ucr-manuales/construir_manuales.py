"""Web de manuales y documentos del Portal de Valoración UCR. © 2026 Óscar Plana Cases. Todos los derechos reservados.

Genera index.html cifrado con los documentos de documentos.json, agrupados por apartados.
  - nivel "lectura": se abren con la contraseña de administración de la web o con la de solo lectura.
  - nivel "admin": solo con la contraseña de administración de la web.
Los PDF, sus títulos y sus descripciones van cifrados: sin contraseña no se ve ni qué documentos hay.
Las contraseñas no se guardan en ningún archivo publicado.

Uso:
  python3 construir_manuales.py --claves /ruta/privada/claves_manuales.env --pdfs <carpeta con los PDF> \
      --salida /ruta/al/repo/oscarplana-cpu.github.io/ucr-manuales --commit <commit de herramienta-ucr>
Sin --claves usa las variables UCR_MANUALES_PWD_ADMIN y UCR_MANUALES_PWD_LECTURA.

version.json guarda la fecha, el commit de la herramienta que recogen los manuales y la huella del texto de cada documento (para saber si ha cambiado).
La conexión con la herramienta UCR se activa o desactiva en config.json (no hace falta volver a construir).
"""
import argparse, base64, json, os, pathlib, secrets, datetime
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ITER = 310000
AQUI = pathlib.Path(__file__).resolve().parent
b64 = lambda b: base64.b64encode(b).decode()

ap = argparse.ArgumentParser()
ap.add_argument("--claves", help="archivo claves_manuales.env; si no se da, usa las variables UCR_MANUALES_PWD_ADMIN y UCR_MANUALES_PWD_LECTURA")
ap.add_argument("--pdfs", required=True, help="carpeta con los PDF que nombra documentos.json")
ap.add_argument("--documentos", default=str(AQUI / "documentos.json"))
ap.add_argument("--salida", required=True)
ap.add_argument("--commit", default="", help="commit de herramienta-ucr que recogen los manuales")
ap.add_argument("--huellas", default="{}", help='JSON {clave: sha256 del markdown exportado de cada doc}, para saber si un doc ha cambiado')
a = ap.parse_args()

env = dict(l.strip().split("=", 1) for l in pathlib.Path(a.claves).read_text().splitlines() if "=" in l) if a.claves else {k: os.environ.get(k) for k in ("UCR_MANUALES_PWD_ADMIN", "UCR_MANUALES_PWD_LECTURA")}
if not env.get("UCR_MANUALES_PWD_ADMIN") or not env.get("UCR_MANUALES_PWD_LECTURA"):
    raise SystemExit("Faltan UCR_MANUALES_PWD_ADMIN o UCR_MANUALES_PWD_LECTURA (archivo claves_manuales.env o variables de entorno).")

docs = json.loads(pathlib.Path(a.documentos).read_text(encoding="utf-8"))["documentos"]
carpeta = pathlib.Path(a.pdfs)
faltan = [d["archivo"] for d in docs if not (carpeta / d["archivo"]).exists()]
if faltan: raise SystemExit("Faltan PDF: " + ", ".join(faltan))

def paquete(nivel):
    """Bloque binario: 4 bytes con la longitud del índice JSON, el índice y los PDF seguidos."""
    meta, cuerpo, pos = [], b"", 0
    for d in [d for d in docs if d["nivel"] == nivel]:
        pdf = (carpeta / d["archivo"]).read_bytes()
        meta.append({"seccion": d["seccion"], "titulo": d["titulo"], "desc": d["desc"], "nombre": d["archivo"], "ini": pos, "fin": pos + len(pdf)})
        cuerpo += pdf; pos += len(pdf)
    ind = json.dumps(meta, ensure_ascii=False).encode()
    return len(ind).to_bytes(4, "big") + ind + cuerpo

k_lec, k_adm = AESGCM.generate_key(256), AESGCM.generate_key(256)

def cifrar(clave, datos):
    iv = secrets.token_bytes(12)
    return {"iv": b64(iv), "ct": b64(AESGCM(clave).encrypt(iv, datos, None))}

def envolver(pwd, carga):
    sal = secrets.token_bytes(16)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=sal, iterations=ITER)
    d = cifrar(kdf.derive(pwd.encode()), carga); d["sal"] = b64(sal); return d

datos = {
    "iter": ITER,
    "llaves": [envolver(env["UCR_MANUALES_PWD_ADMIN"], k_lec + k_adm), envolver(env["UCR_MANUALES_PWD_LECTURA"], k_lec)],
    "lectura": cifrar(k_lec, paquete("lectura")),
    "admin": cifrar(k_adm, paquete("admin")),
    "fecha": datetime.date.today().strftime("%d/%m/%Y"),
}
html = (AQUI / "plantilla.html").read_text(encoding="utf-8").replace("/*DATOS*/null", json.dumps(datos, separators=(",", ":")))
for t in (env["UCR_MANUALES_PWD_ADMIN"], env["UCR_MANUALES_PWD_LECTURA"]):
    assert t not in html, "Una contraseña ha acabado en el HTML"
for d in docs:
    assert d["titulo"] not in html, "Un título ha quedado en claro en el HTML"
sal = pathlib.Path(a.salida); sal.mkdir(parents=True, exist_ok=True)
(sal / "index.html").write_text(html, encoding="utf-8")
if not (sal / "config.json").exists():
    (sal / "config.json").write_text((AQUI / "config.json").read_text(encoding="utf-8"), encoding="utf-8")
(sal / "version.json").write_text(json.dumps({"fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "commit_herramienta": a.commit, "huellas_md": json.loads(a.huellas)}, indent=2) + "\n", encoding="utf-8")
print("index.html:", round(len(html) / 1e6, 2), "MB ->", sal, "·", len(docs), "documentos")
