"""
Agente de control remoto para PC (Windows) - version solo WiFi local
-----------------------------------------------------------------------
Este programa corre en segundo plano en tu PC y espera ordenes
enviadas desde tu movil (a traves de la app de Expo), siempre que
el movil este conectado a la MISMA red WiFi que el PC.

NO requiere instalar nada extra: usa solo la libreria estandar de Python.

CONFIGURACION IMPORTANTE:
1) Cambia el valor de TOKEN por una clave secreta tuya (como una contraseña).
2) Guarda este archivo, por ejemplo en: C:\PCAgent\pc_agent.py
3) Necesitas tener Python instalado en Windows (https://www.python.org/downloads/,
   marca la casilla "Add Python to PATH" durante la instalacion).

COMO PROBARLO MANUALMENTE:
   Abre una terminal (cmd) y ejecuta:
        python pc_agent.py
   Deberia decir "Agente activo en el puerto 5757".
   Dejalo esa ventana abierta y prueba desde el navegador del propio PC:
        http://localhost:5757/status?token=TU_TOKEN

COMO SABER LA IP DE TU PC (la necesitaras en la app):
   Abre cmd y escribe "ipconfig", busca "Direccion IPv4" (ej: 192.168.1.34)

COMO HACER QUE ARRANQUE SOLO CON WINDOWS:
   Ver el archivo README.md que acompana a este script.
"""

import http.server
import socketserver
import subprocess
import json
from urllib.parse import urlparse, parse_qs

PORT = 5757

# --------------------------------------------------------------
# CAMBIA ESTO por una clave secreta larga y dificil de adivinar.
# Es lo unico que evita que un desconocido pueda apagar tu PC.
# --------------------------------------------------------------
TOKEN = "CAMBIA_ESTE_TOKEN_POR_UNO_SECRETO_Y_LARGO"


class Handler(http.server.BaseHTTPRequestHandler):

    def _send(self, code, message):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({"status": message}).encode("utf-8"))

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.strip("/")
        qs = parse_qs(parsed.query)
        token = qs.get("token", [""])[0]

        if token != TOKEN:
            self._send(401, "token invalido")
            return

        if path == "status":
            self._send(200, "pc encendido y agente activo")

        elif path == "lock":
            subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
            self._send(200, "pc bloqueado")

        elif path == "restart":
            self._send(200, "reiniciando en 5 segundos...")
            subprocess.Popen(["shutdown", "/r", "/t", "5"])

        elif path == "shutdown":
            self._send(200, "apagando en 5 segundos...")
            subprocess.Popen(["shutdown", "/s", "/t", "5"])

        elif path == "cancelar":
            # Por si pulsas apagar/reiniciar sin querer
            subprocess.run(["shutdown", "/a"])
            self._send(200, "apagado/reinicio cancelado")

        else:
            self._send(404, "accion no reconocida")

    def log_message(self, format, *args):
        # Log simple en la consola
        print("%s - %s" % (self.address_string(), format % args))


if __name__ == "__main__":
    with socketserver.ThreadingTCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"Agente activo en el puerto {PORT}")
        print("Dejalo corriendo en segundo plano (o configuralo para que arranque solo).")
        httpd.serve_forever()
