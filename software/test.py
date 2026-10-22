import time
from enviar_tramas import MaraniDSPController

# Configuración de conexión y pruebas
IP_DESTINO = "192.168.0.100"
PUERTO_DESTINO = 1001
PROTOCOLO = "TCP"

# Ponlo en True para enviar las tramas por red al DSP, 
# o en False para verificar solo en consola que las tramas se generan bien.
ENVIAR_POR_RED = False  
PAUSA_ENTRE_TRAMAS = 2  # Segundos de espera entre envíos


def ejecutar_accion(descripcion: str, trama: bytearray, dsp: MaraniDSPController, enviar: bool):
    """Muestra la trama generada y, si está activado, la envía al DSP."""
    hex_str = dsp.formatear_hex(trama)
    print(f"[*] {descripcion:<42} -> {hex_str}")
    
    if enviar:
        try:
            dsp.enviar_trama(trama)
            print("    └── [OK] Enviada al DSP")
        except Exception as e:
            print(f"    └── [ERROR] Fallo de red: {e}")
        time.sleep(PAUSA_ENTRE_TRAMAS)


def test_bateria_completa(dsp: MaraniDSPController, enviar: bool):
    """Recorre los 6 canales probando Subir/Bajar ganancia y Mute/Unmute según el diccionario."""
    print("\n" + "=" * 85)
    print(f" INICIANDO BATERÍA DE TESTS | Destino: {dsp.ip}:{dsp.port} ({dsp.protocol}) | Envío Red: {enviar}")
    print("=" * 85)

    # 1. Prueba de ganancias por canal (+1.0 dB = 0x62 y 0.0 dB = 0x58)
    print("\n--- 1. TEST DE GANANCIA (CANALES 1 AL 6) ---")
    for canal in range(1, 7):
        # Subir ganancia a +1.0 dB (0x62)
        trama_subir = dsp.crear_trama_ganancia(canal=canal, ganancia_db=1.0)
        ejecutar_accion(f"Canal {canal}: Subir ganancia (+1.0 dB / 0x62)", trama_subir, dsp, enviar)

        # Bajar ganancia a 0.0 dB (0x58)
        trama_bajar = dsp.crear_trama_ganancia(canal=canal, ganancia_db=0.0)
        ejecutar_accion(f"Canal {canal}: Bajar ganancia ( 0.0 dB / 0x58)", trama_bajar, dsp, enviar)

    # 2. Prueba de valores personalizados de ganancia en Canal 1
    print("\n--- 2. TEST DE BARRIDO DE GANANCIA (CANAL 1) ---")
    for db in [-6.0, -3.0, -0.5, 0.0, 0.5, 3.0]:
        trama_custom = dsp.crear_trama_ganancia(canal=1, ganancia_db=db)
        ejecutar_accion(f"Canal 1: Ganancia personalizada ({db:+.1f} dB)", trama_custom, dsp, enviar)

    # 3. Prueba de Mute / Unmute estándar (3er byte = 0x01)
    print("\n--- 3. TEST DE MUTE / UNMUTE ESTÁNDAR (CANALES 1 AL 6) ---")
    for canal in range(1, 7):
        trama_mute = dsp.crear_trama_mute(canal=canal, mute=True)
        ejecutar_accion(f"Canal {canal}: MUTE (3er byte 0x01)", trama_mute, dsp, enviar)

        trama_unmute = dsp.crear_trama_mute(canal=canal, mute=False)
        ejecutar_accion(f"Canal {canal}: UNMUTE (3er byte 0x01)", trama_unmute, dsp, enviar)

    # 4. Caso especial del diccionario: Mute/Unmute Canal 1 con 3er byte en 0x03
    print("\n--- 4. TEST ESPECIAL CANAL 1 (COMPROBAR 3ER BYTE = 0x03) ---")
    trama_mute_c1_alt = dsp.crear_trama_mute(canal=1, mute=True, device_byte=0x03)
    ejecutar_accion("Canal 1: MUTE alternativo (3er byte 0x03)", trama_mute_c1_alt, dsp, enviar)

    trama_unmute_c1_alt = dsp.crear_trama_mute(canal=1, mute=False, device_byte=0x03)
    ejecutar_accion("Canal 1: UNMUTE alternativo (3er byte 0x03)", trama_unmute_c1_alt, dsp, enviar)

    print("\n" + "=" * 85)
    print(" BATERÍA DE PRUEBAS FINALIZADA")
    print("=" * 85)


if __name__ == "__main__":
    # Instanciamos el controlador importado del módulo
    controlador = MaraniDSPController(
        ip=IP_DESTINO,
        port=PUERTO_DESTINO,
        protocol=PROTOCOLO,
        timeout=2.0
    )

    print("Selecciona el modo de test:")
    print("  1. Simulación en consola (Dry-Run: verifica las tramas sin conectar al DSP)")
    print("  2. Test real en vivo (Envía la secuencia por red con pausas)")
    
    modo = input("\nOpción [1/2]: ").strip()
    enviar_red = (modo == "2")

    test_bateria_completa(controlador, enviar=enviar_red)