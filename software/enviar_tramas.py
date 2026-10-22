import socket
import argparse
import sys

# Configuración de red por defecto
DSP_IP = "192.168.0.100"
DSP_PORT = 1001
PROTOCOLO = "TCP"


class MaraniDSPController:
    
    HEADER_START = 0xF0
    MANUFACTURER_ID = 0x91
    FOOTER_END = 0xF7
    
    CMD_MUTE = 0x03
    CMD_GAIN = 0x04

    def __init__(self, ip: str = DSP_IP, port: int = DSP_PORT, protocol: str = PROTOCOLO, timeout: float = 3.0):
        self.ip = ip
        self.port = port
        self.protocol = protocol.upper()
        self.timeout = timeout

    @staticmethod
    def _validar_canal(canal: int) -> int:
        """
        Convierte el número de canal (1 a 6) al índice hexadecimal de trama (canal - 1).
        """
        if not (1 <= canal <= 6):
            raise ValueError(f"El canal debe estar entre 1 y 6 (recibido: {canal}).")
        return canal - 1

    @classmethod
    def crear_trama_ganancia(cls, canal: int, ganancia_db: float, device_byte: int = 0x01) -> bytearray:
        """
        Construye la trama de 13 bytes para ajustar la ganancia de un canal.
        Estructura: F0 | 91 | 01 | 04 | 01 | CH | 02 | VAL | 00 | 00 | 00 | 00 | F7
        0 dB = 88 (0x58), pasos de 0.1 dB = 1 entero.
        """
        ch_byte = cls._validar_canal(canal)
        
        # Ecuación: 88 + (Ganancia * 10)
        byte_ganancia = int(round(88 + (ganancia_db * 10)))
        byte_ganancia = max(0, min(255, byte_ganancia))

        return bytearray([
            cls.HEADER_START,
            cls.MANUFACTURER_ID,
            device_byte,
            cls.CMD_GAIN,
            0x01,
            ch_byte,
            0x02,
            byte_ganancia,
            0x00, 0x00, 0x00, 0x00,
            cls.FOOTER_END
        ])

    @classmethod
    def crear_trama_mute(cls, canal: int, mute: bool, device_byte: int = 0x01) -> bytearray:
        """
        Construye la trama de 13 bytes para silenciar (mute) o activar (unmute) un canal.
        Estructura: F0 | 91 | 01 | 03 | 01 | CH | ESTADO | 00 | 00 | 00 | 00 | 00 | F7
        Estado: 0x01 = Mute, 0x00 = Unmute.
        Nota: Permite modificar device_byte (3er byte, por defecto 0x01, o 0x03 para pruebas en canal 1).
        """
        ch_byte = cls._validar_canal(canal)
        estado_byte = 0x01 if mute else 0x00

        return bytearray([
            cls.HEADER_START,
            cls.MANUFACTURER_ID,
            device_byte,
            cls.CMD_MUTE,
            0x01,
            ch_byte,
            estado_byte,
            0x00, 0x00, 0x00, 0x00, 0x00,
            cls.FOOTER_END
        ])

    @staticmethod
    def formatear_hex(trama: bytearray) -> str:
        """Devuelve la representación hexadecimal legible de una trama."""
        return " ".join(f"{b:02X}" for b in trama)

    def enviar_trama(self, trama: bytearray) -> None:
        """Abre el socket según el protocolo configurado, envía los bytes crudos y cierra la conexión."""
        if self.protocol == "UDP":
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.sendto(trama, (self.ip, self.port))
        elif self.protocol == "TCP":
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.timeout)
                s.connect((self.ip, self.port))
                s.sendall(trama)
        else:
            raise ValueError(f"Protocolo no soportado: {self.protocol}. Usa 'TCP' o 'UDP'.")

    # --- Métodos de alto nivel para uso directo ---

    def set_ganancia(self, canal: int, ganancia_db: float, enviar: bool = True) -> bytearray:
        trama = self.crear_trama_ganancia(canal, ganancia_db)
        if enviar:
            self.enviar_trama(trama)
        return trama

    def set_mute(self, canal: int, mute: bool, device_byte: int = 0x01, enviar: bool = True) -> bytearray:
        trama = self.crear_trama_mute(canal, mute, device_byte=device_byte)
        if enviar:
            self.enviar_trama(trama)
        return trama