"""Web de manuales del Portal de Valoración UCR. © 2026 Óscar Plana Cases. Todos los derechos reservados.

Genera index.html cifrado con los dos manuales en PDF:
  - Manual de uso: se abre con la contraseña de administración o con la de solo lectura.
  - Manual interno: solo con la contraseña de administración.
Los PDF nunca se publican en claro. Las contraseñas no se guardan en ningún archivo publicado.

Uso:
  python3 construir_manuales.py --claves /ruta/privada/claves_app.env \
      --uso Manual_de_uso_Portal_UCR.pdf --interno Manual_interno_Portal_UCR.pdf \
      --salida /ruta/al/repo/oscarplana-cpu.github.io/ucr-manuales

La conexión con la herramienta UCR se activa o desactiva en config.json (no hace falta volver a construir).
"""
import argparse, base64, json, pathlib, secrets, datetime
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ITER = 310000
AQUI = pathlib.Path(__file__).resolve().parent
b64 = lambda b: base64.b64encode(b).decode()

ap = argparse.ArgumentParser()
ap.add_argument("--claves", required=True)
ap.add_argument("--uso", required=True)
ap.add_argument("--interno", required=True)
ap.add_argument("--salida", required=True)
a = ap.parse_args()

env = dict(l.strip().split("=", 1) for l in pathlib.Path(a.claves).read_text().splitlines() if "=" in l)
if not env.get("UCR_PWD_ADMIN") or not env.get("UCR_PWD_LECTURA"):
    raise SystemExit("Faltan UCR_PWD_ADMIN o UCR_PWD_LECTURA en el archivo de claves.")

k_uso, k_int = AESGCM.generate_key(256), AESGCM.generate_key(256)

def cifrar(clave, datos):
    iv = secrets.token_bytes(12)
    return {"iv": b64(iv), "ct": b64(AESGCM(clave).encrypt(iv, datos, None))}

def envolver(pwd, carga):
    sal = secrets.token_bytes(16)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=sal, iterations=ITER)
    d = cifrar(kdf.derive(pwd.encode()), carga); d["sal"] = b64(sal); return d

datos = {
    "iter": ITER,
    "llaves": [envolver(env["UCR_PWD_ADMIN"], k_uso + k_int), envolver(env["UCR_PWD_LECTURA"], k_uso)],
    "uso": cifrar(k_uso, pathlib.Path(a.uso).read_bytes()),
    "interno": cifrar(k_int, pathlib.Path(a.interno).read_bytes()),
    "fecha": datetime.date.today().strftime("%d/%m/%Y"),
}
html = (AQUI / "plantilla.html").read_text(encoding="utf-8").replace("/*DATOS*/null", json.dumps(datos, separators=(",", ":")))
sal = pathlib.Path(a.salida); sal.mkdir(parents=True, exist_ok=True)
(sal / "index.html").write_text(html, encoding="utf-8")
if not (sal / "config.json").exists():
    (sal / "config.json").write_text((AQUI / "config.json").read_text(encoding="utf-8"), encoding="utf-8")
for t in (env["UCR_PWD_ADMIN"], env["UCR_PWD_LECTURA"]):
    assert t not in html, "Una contraseña ha acabado en el HTML"
print("index.html:", round(len(html) / 1e6, 2), "MB ->", sal)
