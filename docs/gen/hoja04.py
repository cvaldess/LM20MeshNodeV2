"""Hoja 04 · GNSS — MinewSemi ME31GR02 (rev 0.2) y U.FL para antena activa o pasiva (docs/04_gnss.svg). Refs 4xx.
Fuentes: ME31GR02 datasheet V1.0.0 (§2.9 modos, §3.2 V_BCKP 2,5-3,6 V, §3.3 consumo, §4.1 pinout LCC-18, §5.1
referencia: L 47 nH desde VCC_RF, 47 pF y pila BAT tras diodo + 100 Ω, §5.2-5.5 layout/alimentación/antena/UART,
§5.6 arranque) y respuestas de Minew (19-11: V_BCKP 12 µA, chip Beken BK166X; 20-11: RESET con pull-up interno).
Pila de respaldo: Seiko MS621FE FL11E, especificación STDE-B-MS0621E-5ATFL11E (§4 carga 2,8-3,3 V, 3,1 recomendada,
máx. 0,5 mA a 3,1 V y 10 mA a 0 V; §8 sólo soldador, sin reflujo; plano E65 FL11E: + arriba en vista superior).
Pinout = simbolos_lib.me31gr02()."""
import os

from svgkit import *  # noqa: F401,F403

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "04_gnss.svg"))


def dibujar():
    W, H = 1720, 1040
    nueva(W, H, "04 · GNSS — MinewSemi ME31GR02 (L1, 4 constelaciones)",
          "nrf54lm20-meshnode rev 0.2 · hoja 4 · referencias 4xx · intención de 04_gnss.kicad_sch")
    leyenda(760, 40)

    # ---------------------------------------------------------------- A · módulo
    frame(20, 76, 860, 610, "A · U401 ME31GR02 — Beken BK1661, LCC-18 10,5 × 9,7 (pinout tipo u-blox MAX)")
    L = [("8", "VCC"), ("6", "V_BCKP"), None, ("3", "RXD"), ("2", "TXD"), None, ("9", "RESET"), ("4", "PPS"), None,
         ("1", "GND"), ("10", "GND"), ("12", "GND")]
    R = [("11", "RF_IN"), ("14", "VCC_RF"), None] + [(n, "NC") for n in ("5", "7", "13", "15", "16", "17", "18")]
    e, h = ic2(360, 150, 180, "U401", "ME31GR02 · MinewSemi", L, R, pitch=26)
    pin_labels(e, {"8": ("V_GNSS", "pwr"), "6": ("V_BCKP", "loc"), "3": ("GNSS_RXD", "loc"),
                   "2": ("GNSS_TXD", "loc"), "9": ("GNSS_RESET", "loc"), "4": ("GNSS_PPS", "sig"),
                   "1": ("", "gnd"), "10": ("", "gnd"), "12": ("", "gnd"), "11": ("GNSS_RFIN", "loc"),
                   "14": ("VCC_RF", "loc"), **{n: ("", "nc") for n in ("5", "7", "13", "15", "16", "17", "18")}})
    notes(40, 150 + h + 36, [
        "UART 115200 por defecto, NMEA 4.1 (§5.5). Consumo (§3.3): 19 mA captura · 17,5 mA seguimiento.",
        "V_BCKP (2,5–3,6 V, 12 µA): pila BT401 cargada desde 3V3 (marco D) ⇒ RTC + efemérides vivos también",
        "con la placa apagada (ship mode o LiPo agotada) ⇒ arranque en caliente (~1 s) al volver a encender.",
        "RESET: pull-up interno (Minew 20-11) ⇒ al aire; R405 0 Ω DNP a GNSS_RST (P1.00) por si hiciera falta.",
        "PPS a 3,3 V directo a GNSS_PPS (P1.04). NC 5, 7, 13, 15–18 al aire (§4.1). Sin SAFEBOOT: actualiza por UART.",
        ("Meshtastic no lo reconoce: hace falta sonda nueva en GPS.cpp ($POLCFGPTVER → $POLRS; al arrancar", "tw"),
        ("saca $POLRS o $BKCHIP). Comandos $POLCFG… en datasheets/BK166X_Series_Interface_Description.", "tw"),
        "Frente a la rev 0.1 (E108-GN04S): fuera C404 56 pF en serie y TP401 SAFEBOOT; L401 82 → 47 nH; C404 = 47 pF",
        "de VCC_RF a GND; nuevos R405 (RESET), TP401/TP402 (UART) y pila de respaldo BT401 + D401."], dy=19)

    # ---------------------------------------------------------------- B · UART, reset, TP
    frame(900, 76, 800, 330, "B · UART, reset y puntos de prueba")
    label(990, 140, "GNSS_TX", "sig", "end"); res_h(990, 140, "R402", "1 kΩ", 80); label(1070, 140, "GNSS_RXD", "loc")
    label(990, 185, "GNSS_RX", "sig", "end"); res_h(990, 185, "R403", "1 kΩ", 80); label(1070, 185, "GNSS_TXD", "loc")
    label(990, 230, "GNSS_RST", "sig", "end"); res_h(990, 230, "R405", "0 Ω DNP", 80, sym="dnp")
    label(1070, 230, "GNSS_RESET", "loc")
    tp(1340, 140, "TP401"); label(1400, 140, "GNSS_TXD", "loc")
    tp(1340, 185, "TP402"); label(1400, 185, "GNSS_RXD", "loc")
    notes(920, 300, [
        "R402/R403 1 kΩ en serie (Minew pone 100 Ω): además limitan lo que entra por RXD con el GNSS apagado.",
        ("§2.9/§5.5: con VCC cortado ninguna línea en alto ⇒ FIRMWARE: al apagar, TX del MCU en entrada + pull-down.", "tw"),
        "R405 sin montar: RESET queda con su pull-up y el MCU no puede dejarlo en alto con el GNSS apagado.",
        "TP401/TP402: la UART del GNSS a mano para probar los $POLCFG… o actualizar su firmware (con el nRF en reset).",
        "Con BT401 el GNSS está en backup aunque la placa esté apagada: tampoco entonces se le mete nada por la UART."],
        dy=19)

    # ---------------------------------------------------------------- C · antena
    frame(900, 420, 800, 266, "C · Antena 1575 MHz por U.FL — activa o pasiva (Minew §5.1)")
    ej, _ = ic2(940, 500, 110, "J401", "BWU.FL-IPEX1", [], [("1", "SIG"), ("2", "GND"), ("3", "GND")], pitch=24)
    for k in ("2", "3"):
        x, y = ej[k]; P([(x, y), (x + 10, y)]); gnd(x + 10, y)
    x0, y0 = ej["1"]
    P([(x0, y0), (1300, y0)], "rf"); dot(1200, y0); label(1300, y0, "GNSS_RFIN", "loc")
    P([(1200, y0), (1200, y0 + 12)])
    ind_v(1200, y0 + 12, "L401", "47 nH (activa)", 60)
    yb = y0 + 72
    dot(1200, yb); P([(1200, yb), (1250, yb)]); cap_v(1250, yb, "C404", "47 pF C0G", 40); gnd(1250, yb + 40)
    P([(1180, yb), (1200, yb)]); label(1180, yb, "VCC_RF", "loc", "end")
    notes(1320, 556, ["L401 desde VCC_RF (3,3 V) alimenta una antena",
                      "activa por el coaxial; C404 desacopla VCC_RF.",
                      "Sin condensador serie: como la referencia,",
                      "la polarización entra por RF_IN.",
                      "Pasiva: L401 no estorba si la antena no",
                      "está en corto en DC. Activa: G < 25 dB, NF < 1,5."], dy=17)
    notes(920, 668, ["Pista 50 Ω coplanar de RF_IN al U.FL, corta, referida a In1 (GND) como en la rev 0.1 (§5.2)."])

    # ---------------------------------------------------------------- D · alimentación y respaldo
    frame(20, 700, 860, 330, "D · Alimentación del GNSS y pila de respaldo de V_BCKP")
    caps_to_gnd(120, 760, "V_GNSS", "pwr", [("C401", "10 µF"), ("C402", "100 nF")], dx=90)
    label(500, 760, "3V3", "pwr", "end"); res_h(500, 760, "R404", "0 Ω DNP", 80, sym="dnp"); label(580, 760, "V_GNSS", "pwr")
    yk = 850
    label(100, yk, "3V3", "pwr", "end"); diode_h(100, yk, "D401", "BAT54WS", 70); P([(170, yk), (190, yk)])
    res_h(190, yk, "R401", "1 kΩ", 80); P([(270, yk), (440, yk)]); dot(320, yk); dot(400, yk)
    bat_v(320, yk, "BT401", "MS621FE-FL11E", 48, side="l"); gnd(320, yk + 48)
    cap_v(400, yk, "C403", "100 nF", 40); gnd(400, yk + 40)
    label(440, yk, "V_BCKP", "loc")
    notes(520, 822, ["BT401: Li-Mn recargable 3 V, 5,5 mAh, Ø 6,8 × 2,1 mm.",
                     "Carga 2,8–3,3 V (3,1 recomendada): 3V3 − BAT54 ≈ 3,15 V;",
                     "R401 limita a ≤ 3 mA con la pila a 0 V (Seiko: máx. 10).",
                     "D401 impide que la pila alimente el 3V3 apagado (fuga",
                     "< 1 µA a 3 V). Sin BT401 funciona igual que la rev 0.1.",
                     "Autonomía estimada ≈ 1–2 semanas de RTC a 12 µA.",
                     ("Sin reflujo: soldar a mano al final (≤ 5 s, pila < 85 °C).", "tw")], dy=17)
    notes(40, 950, ["V_GNSS = BUCK1 del nPM1300 (200 mA, sólo para el GNSS), conmutado con PIN_GPS_EN (GNSS_EN): lejos de los",
                    "picos de TX del MS21SF1. Minew §5.3 pide fuente limpia > 100 mA. C401/C402 junto a la pata 8, C403 junto a la 6.",
                    "R404 sin montar: GNSS siempre encendido desde 3V3 si BUCK1 diera guerra (dormiría por comando).",
                    ("🚨 Con R404 montada, BUCK1 debe quedar APAGADO (dos fuentes unidas).", "tw")], dy=19)

    rows = [("U401", "GNSS L1 (4 constel.)", "MinewSemi ME31GR02", "LCC-18 10,5×9,7", "—", "patrocinio Minew"),
            ("J401", "conector antena", "BWU.FL-IPEX1", "SMD", "C5137195", "cajón #210"),
            ("L401", "47 nH (antena activa)", "Murata LQW15AN47NJ00D", "0402", "C192855", "cajón #207"),
            ("C404", "47 pF C0G", "FH 0402CG470F500NT", "0402", "C42563629", "cajón #208"),
            ("BT401", "pila recargable 3 V", "Seiko MS621FE-FL11E", "Ø6,8 tags", "—", "COMPRAR"),
            ("D401", "Schottky baja fuga", "Diodes BAT54WS-7-F", "SOD-323", "C124205", "COMPRAR"),
            ("R401-R403", "1 kΩ 1 %", "UNI-ROYAL 0402WGF1001TCE", "0402", "C11702", "cajón #31"),
            ("R404 R405", "0 Ω (DNP)", "—", "0402", "—", "—"),
            ("C401", "10 µF 10 V X7R", "—", "0603", "—", "cajón #147"),
            ("C402 C403", "100 nF 16 V X7R", "Samsung CL05B104KO5NNNC", "0402", "C1525", "cajón #22"),
            ("TP401 TP402", "punto de prueba", "TestPoint_Pad_D1.0mm", "Ø1 mm", "—", "—")]
    frame(900, 700, 800, 330, "Piezas de la hoja")
    tabla(900, 740, 800, [920, 1010, 1160, 1350, 1450, 1545], ["Ref.", "Qué es", "Pieza", "Encaps.", "LCSC", "Stock"],
          rows, dy=23, mono=(0, 4))
    notes(920, 1019, ["BT401: huella Battery:BatteryHolder_Seiko_MS621F (pad 1 = +, plano Seiko E65 FL11E)."])
    guardar(OUT)


if __name__ == "__main__":
    dibujar()
