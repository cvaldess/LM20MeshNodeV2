"""Hoja 03 · LoRa — MinewSemi MS21SF1-SX1262 (rev 0.2) (docs/03_lora.svg). Referencias 3xx.
Fuentes: MS21SF1 datasheet K (§3-4 pinout, §6.3.2 conmutador por DIO2, p. 9 esquema interno: cristal pasivo Y1
a XTA/XTB, R1/R2 de la pata 14; §8.2-8.5 diseño de PCB) y respuestas de Minew (19-11 sleep 0,9 µA; un solo
hardware EU868/US915). Pinout = simbolos_lib.ms21sf1()."""
import os

from svgkit import *  # noqa: F401,F403

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "03_lora.svg"))


def dibujar():
    W, H = 1720, 1000
    nueva(W, H, "03 · LoRa — MinewSemi MS21SF1 (SX1262, 22 dBm)",
          "nrf54lm20-meshnode rev 0.2 · hoja 3 · referencias 3xx · intención de 03_lora.kicad_sch")
    leyenda(760, 40)

    # ---------------------------------------------------------------- A · módulo
    frame(20, 76, 860, 604, "A · U301 MS21SF1-SX1262 — conmutador de RF y U.FL dentro del módulo")
    L = [("8", "VDD"), None, ("9", "SX_NRESET"), None, ("13", "NSS"), ("12", "SCK"), ("11", "MOSI"), ("10", "MISO"),
         None, ("1", "GND"), ("7", "GND"), ("15", "GND")]
    R = [("16", "ANT"), None, ("6", "BUSY"), ("4", "DIO1"), ("5", "DIO3"), None, ("2", "NC"), ("3", "NC"),
         ("14", "NC")]
    e, h = ic2(320, 150, 190, "U301", "MS21SF1-SX1262 · MinewSemi", L, R, pitch=28)
    pin_labels(e, {"8": ("VDD_LORA", "loc"), "9": ("LORA_NRST", "sig"), "13": ("LORA_NSS", "sig"),
                   "12": ("LORA_SCK", "sig"), "11": ("LORA_MOSI", "sig"), "10": ("LORA_MISO", "sig"),
                   "1": ("", "gnd"), "7": ("", "gnd"), "15": ("", "gnd"), "16": ("", "nc"),
                   "6": ("LORA_BUSY", "sig"), "4": ("LORA_DIO1", "sig"), "5": ("", "nc"),
                   "2": ("", "nc"), "3": ("", "nc"), "14": ("", "nc")})
    x16, y16 = e["16"]
    T(x16 + 12, y16 + 4, "sin pista: la antena va al U.FL del módulo", "ts")
    notes(40, 150 + h + 40, [
        "Conmutador de RF interno gobernado por DIO2 (V1 = ANT_SW1 = DIO2, p. 9); DIO2 no sale del módulo.",
        ("⇒ variante: SX126X_DIO2_AS_RF_SWITCH y SIN SX126X_RXEN / SX126X_TXEN (P1.12 y P1.13 quedan libres).", "tw"),
        "Cristal PASIVO de 32 MHz (Y1 a XTA/XTB en el esquema interno, p. 9): DIO3 al aire.",
        ("⇒ la variante NO define SX126X_DIO3_TCXO_VOLTAGE (igual que con el E22-900MM22S).", "tw"),
        "Patas 2, 3 y 14 NC (pedido estándar: R1 0 Ω / R2 NC dentro del módulo ⇒ 14 = NC).",
        "NRST con pull-up interno del SX1262: lo mueve el MCU (LORA_NRST). SPI hasta 16 MHz (P1 limita a 8).",
        "Pedir la versión SX1262 (3N62AI-X): el LLCC68 no hace SF11/BW250 (LongFast). Mismo hardware EU868/US915."],
        dy=19)

    # ---------------------------------------------------------------- B · alimentación (π)
    frame(900, 76, 800, 300, "B · Alimentación del módulo (Minew §8.3: π reservada con fuente conmutada)")
    label(950, 140, "3V3", "pwr", "end"); P([(950, 140), (1040, 140)], "pw"); dot(1000, 140)
    cap_v(1000, 140, "C303", "10 µF", 44, "l"); gnd(1000, 184)
    res_h(1040, 140, "FB301", "0 Ω (o ferrita 600 Ω)", 90, sym="symp")
    P([(1130, 140), (1290, 140)], "pw"); dot(1180, 140); dot(1240, 140)
    cap_v(1180, 140, "C301", "22 µF", 44); gnd(1180, 184)
    cap_v(1240, 140, "C302", "100 nF", 44); gnd(1240, 184)
    label(1290, 140, "VDD_LORA", "loc")
    notes(920, 240, ["FB301 = π que pide Minew (3V3 sale del BUCK2): 0 Ω de serie; ferrita CBW160808U601T",
                     "(#4: 1 A, 0,4 Ω ⇒ 50 mV en TX) si el buck se cuela en la recepción. Igual que FB201.",
                     "C301/C302 a ≤ 0,5 mm de la pata 8, con dos vías a GND (§8.3).",
                     "Consumo a 3,3 V (p. 9): TX 22 dBm 112–123 mA de pico · RX 4,76 mA · sleep ≈ 0,9 µA."], dy=19)

    # ---------------------------------------------------------------- C · cambios frente a la rev 0.1
    frame(900, 390, 800, 246, "C · Qué cambia respecto a la rev 0.1 (E22-900MM22S)")
    notes(920, 430, [
        "Fuera: J301 (U.FL), π de antena R304/C304, R301/R302 (TXEN) y R303 (pull-down de RXEN).",
        "C303 cambia de función: ahora es la entrada de la π de alimentación (10 µF).",
        ("Desaparecen LORA_RXEN (P1.13) y LORA_TXEN (P1.12): fuera de la hoja 02 y de la raíz.", "tw"),
        "Igual que antes: LORA_SCK/MOSI/MISO/NSS/BUSY/DIO1/NRST en los mismos puertos (castellados",
        "12-18 del ME54BS13) y 3V3 siempre vivo (mismo raíl que el MCU: sin estado parcial).",
        "Huella meshnode:MS21SF1 (la de Minew, 16 castellados paso 1,8) y STEP MS21SF1_PCB_V1.0 ya en libs/.",
        "El módulo es 16,4 × 15 × 3 mm (el E22 era 10 × 10): la colocación de la franja LoRa cambia."], dy=21)

    # ---------------------------------------------------------------- D · colocación
    frame(20, 694, 860, 296, "D · Notas de colocación (Minew §8.2–8.5)")
    notes(36, 734, [
        "• U.FL del módulo hacia un canto, con el cable de antena saliendo por fuera; nada metálico encima.",
        "• 0,5 mm alrededor del módulo sin pistas ni piezas que no sean GND; plano GND continuo debajo",
        "    (In1 entero) y una vía a GND junto a cada pad de GND (1, 7, 15).",
        "• Pata 16 (ANT) sin pista y rodeada sólo de GND: es RF aunque aquí no se use.",
        "• Minew pide 20 mm a bucks/inductores, 25 mm a pantallas y 50 mm entre módulos: en 40 × 86 mm no",
        "    cabe ⇒ como en la rev 0.1: planos GND continuos, módulos en zonas distintas y L101/L102 lejos.",
        "• ≥ 5 mm a tornillos (H1–H4, M2) y ~4 mm libres alrededor para soldar y retrabajar.",
        ("• Plantilla: Minew recomienda 0,2 mm escalonada (+0,8 mm) en el módulo y la placa usa 0,10 mm", "tp"),
        ("    ⇒ revisar la pasta de los castellados en la huella antes de pedir el stencil.", "tp")], dy=21)

    rows = [("U301", "módulo LoRa SX1262", "MinewSemi MS21SF1-SX1262", "SMD 16,4×15", "—", "patrocinio Minew"),
            ("FB301", "0 Ω (o ferrita)", "0 Ω / FH CBW160808U601T", "0603", "C139183", "#137 / ferrita #4"),
            ("C301", "22 µF 10 V X7R", "—", "0603", "—", "cajón #146"),
            ("C302", "100 nF 16 V X7R", "Samsung CL05B104KO5NNNC", "0402", "C1525", "cajón #22"),
            ("C303", "10 µF 10 V X7R", "—", "0603", "—", "cajón #147")]
    frame(900, 650, 800, 340, "Piezas de la hoja")
    tabla(900, 690, 800, [920, 1010, 1150, 1350, 1440, 1530], ["Ref.", "Qué es", "Pieza", "Encaps.", "LCSC", "Stock"],
          rows, dy=24, mono=(0, 4))
    notes(920, 860, ["Todo del cajón; el módulo lo manda Minew. Antena 868 MHz con U.FL (IPEX1) aparte.",
                     "VDD_LORA = red local entre FB301 y la pata 8 (en la rev 0.1 la pata iba directa a 3V3)."], dy=19)
    guardar(OUT)


if __name__ == "__main__":
    dibujar()
