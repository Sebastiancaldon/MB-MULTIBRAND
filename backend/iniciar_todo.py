"""Inicia los tres microservicios REST en paralelo desde una sola terminal."""
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SERVICES = [
    ("Catálogo", "microservicio_catalogo.server"),
    ("Compras", "microservicio_cliente_compras.server"),
    ("Calificaciones", "microservicio_calificaciones.server"),
]

def main():
    processes = []
    print("=" * 64)
    print("MB MULTIBRAND REST - INICIO DE LOS TRES MICROSERVICIOS")
    print("Catálogo: http://127.0.0.1:5001")
    print("Compras:  http://127.0.0.1:5002")
    print("Calificaciones: http://127.0.0.1:5004")
    print("Detén todos con Ctrl+C. Esta terminal muestra sus mensajes.")
    print("=" * 64, flush=True)
    try:
        for name, module in SERVICES:
            p = subprocess.Popen([sys.executable, "-m", module], cwd=ROOT)
            processes.append((name, p))
            print(f"Iniciado {name} (PID {p.pid})", flush=True)
            time.sleep(0.7)
        while True:
            failed = [(name, p.returncode) for name, p in processes if p.poll() is not None]
            if failed:
                for name, code in failed:
                    print(f"AVISO: {name} terminó con código {code}.", flush=True)
                time.sleep(1)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nCerrando los tres microservicios...", flush=True)
    finally:
        for _, p in processes:
            if p.poll() is None:
                p.terminate()
        for _, p in processes:
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()
        print("Todos los procesos se han detenido.", flush=True)

if __name__ == "__main__":
    main()
