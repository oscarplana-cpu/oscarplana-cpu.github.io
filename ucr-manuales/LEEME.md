# Manuales · Portal de Valoración UCR

© 2026 Óscar Plana Cases. Todos los derechos reservados.

Web aparte de la herramienta, para tener siempre a mano los dos manuales en PDF.

- Dirección: https://oscarplana-cpu.github.io/ucr-manuales/
- Todo va cifrado (AES-256-GCM). En el repositorio no hay ningún PDF en claro.
- Contraseña de administración de la web: abre los dos manuales. Es propia de esta web, distinta de la de la app.
- Contraseña de solo lectura: abre solo el Manual de uso. Es la misma que la de lectura de la app.
- Se guardan en `claves_manuales.env`, fuera del proyecto y del repositorio, o en las variables de entorno `UCR_MANUALES_PWD_ADMIN` y `UCR_MANUALES_PWD_LECTURA` (la tarea de cada noche usa estas). Si cambian, hay que volver a construir la web.

## Actualizar los manuales

Regla: los dos manuales, sus PDF y esta web se actualizan como mínimo al final de cada día en que cambie la herramienta. Una tarea programada lo revisa cada noche.

1. Exportar cada doc a PDF (A4).
2. `python3 construir_manuales.py --claves <ruta privada>/claves_manuales.env --uso Manual_de_uso_Portal_UCR.pdf --interno Manual_interno_Portal_UCR.pdf --salida <repo>/ucr-manuales --commit <commit de herramienta-ucr>`
3. Commit y push del repositorio `oscarplana-cpu.github.io`.

Los PDF en claro se guardan solo en tu equipo o en tu Drive, nunca en el repositorio.

## Conexión con la herramienta UCR (apagada)

En `config.json`, `conexion_ucr` en `true` muestra en la web el botón "Abrir la herramienta UCR". No hace falta volver a construir: basta con cambiar el valor y subirlo.

En la herramienta, `config/manuales.json` del proyecto UCR hace lo contrario: con `activo` en `true` aparece el botón "Manuales" en la cabecera del portal. Ese sí exige volver a construir y publicar la app.
