"""
Cálculo del nivel sonoro en dBA (ponderación A) a partir del micrófono,
con un offset de calibración.

El offset NO se calcula aquí: se lee del archivo calibracion.json, que se
genera una sola vez al calibrar el sensor. Ejemplo de calibracion.json:
 
    { "offset_db": 117.01 }
 
Si el archivo no existe, el resultado son dBFS (sin calibrar), no dB SPL reales.
 
Requisitos:  pip install numpy scipy sounddevice
 
Ejemplo:
    python spl_dba.py --duracion 5
 
Uso como módulo:
    from spl_dba import cargar_offset, grabar_mic, calcular_spl
    senal, fs = grabar_mic(1.0)
    nivel = calcular_spl(senal, fs, cargar_offset())
"""
 
import argparse
import json
import os
 
import numpy as np
from scipy.signal import bilinear_zpk, sosfilt, zpk2sos
 
ARCHIVO_CALIBRACION = "calibracion.json"
 
 
# ---------- FILTRO DE PONDERACIÓN A ----------
 
def ponderar_a(senal, fs):
    """Aplica la ponderación A (IEC 61672) a la señal."""
    f1, f2, f3, f4 = 20.598997, 107.65265, 737.86223, 12194.217
    w1, w2, w3, w4 = (2 * np.pi * f for f in (f1, f2, f3, f4))
 
    ceros = [0, 0, 0, 0]
    polos = [-w1, -w1, -w2, -w3, -w4, -w4]
    ganancia = w4 ** 2 * 10 ** (1.9997 / 20)          # 0 dB a 1 kHz
 
    z, p, k = bilinear_zpk(ceros, polos, ganancia, fs)  # de analógico a digital
    return sosfilt(zpk2sos(z, p, k), senal)
 
 
# ---------- NIVEL ----------
 
def nivel_db(senal, offset_db):
    """Nivel RMS de la señal en dB, más el offset de calibración."""
    rms = np.sqrt(np.mean(senal ** 2))
    return 20 * np.log10(rms + 1e-12) + offset_db      # 1e-12 evita log(0)
 
 
def calcular_spl(senal, fs, offset_db):
    """Nivel en dBA de una señal (normalizada a +-1)."""
    return nivel_db(ponderar_a(np.asarray(senal, dtype=np.float64), fs), offset_db)
 
 
def cargar_offset(ruta=ARCHIVO_CALIBRACION):
    """Lee el offset de calibración. Devuelve None si no hay archivo."""
    if not os.path.exists(ruta):
        return None
    with open(ruta, encoding="utf-8") as f:
        return float(json.load(f)["offset_db"])
 
 
# ---------- ENTRADA DE SEÑAL ----------
 
def grabar_mic(duracion, fs=48000, dispositivo=None):
    """Graba 'duracion' segundos del micrófono (un canal)."""
    import sounddevice as sd
    audio = sd.rec(int(duracion * fs), samplerate=fs, channels=1,
                   dtype="float64", device=dispositivo)
    sd.wait()
    return audio[:, 0], fs
 
 
# ---------- PROGRAMA PRINCIPAL ----------
 
def main():
    ap = argparse.ArgumentParser(description="Nivel sonoro en dBA desde el micrófono")
    ap.add_argument("--duracion", type=float, default=5.0, help="segundos a grabar")
    ap.add_argument("--ventana", type=float, default=1.0, help="segundos por bloque")
    ap.add_argument("--dispositivo", type=int, default=None, help="índice del dispositivo de audio")
    args = ap.parse_args()
 
    senal, fs = grabar_mic(args.duracion, dispositivo=args.dispositivo)
 
    offset = cargar_offset()
    if offset is None:
        print(f"Aviso: no existe {ARCHIVO_CALIBRACION}, sin calibrar (valores en dBFS)\n")
        offset = 0.0
 
    ponderada = ponderar_a(senal, fs)          # se filtra una vez y luego se corta
    n = int(args.ventana * fs)
    for i in range(0, len(ponderada) - n + 1, n):
        print(f"{i / fs:6.1f} s: {nivel_db(ponderada[i:i + n], offset):6.1f} dBA")
    print(f"\nNivel equivalente (Leq): {nivel_db(ponderada, offset):.1f} dBA")
 
 
if __name__ == "__main__":
    main()