# Rev C2: explicit escape routing of the STM32WB55 QFN-48 (U2 at KiCad (138.6, 84.8), rot 270) and of the RF chain.
# KiCad absolute coordinates (mm). Used by gen_pcb.py (vias are keep-outs for the bottom parts) and route.py.
#   * pins 1-12 face the top board edge: only a 0.6 mm strip is left, enough for three 0.1 mm lanes per side.
#     East lanes: BOOT0 (4), I2C_SCL (5), I2C_SDA (6). West lanes: PWM_M1 (9), VDDA (8), NRST (7). Pin 1 (VBAT)
#     is tied to pin 48 (VDD) at the package corner. Pins 2, 3, 10, 11, 12 are not connected.
#   * west pins 13-15 and the VDD pins 20, 23, 40, 48 get a via right outside the pin tip.
#   * RF1 (21) -> MLPF IN (A3) straight, 0.25 mm; MLPF OUT (A1) -> R34 -> antenna feed, 0.36 mm, with C36 at the
#     antenna side.

NX = lambda n: 141.35 - 0.5 * (n - 1)          # north row, pins 1-12, y 81.3625
WY = lambda n: 82.05 + 0.5 * (n - 13)          # west column, pins 13-24, x 135.1625
EY = lambda n: 87.55 - 0.5 * (n - 37)          # east column, pins 37-48, x 142.0375
YN, XW, XE = 81.3625, 135.1625, 142.0375
L1, L2, L3 = 80.76, 80.56, 80.36               # lanes in the top-edge strip (edge at y 80.0, copper-edge 0.3)

# (net, width, [points]); the first point is the pad centre
TRACKS = [
    # east lanes
    ('BOOT0', 0.1, [(NX(4), YN), (NX(4), L1), (143.05, L1), (143.05, 81.30)]),
    ('I2C_SCL', 0.1, [(NX(5), YN), (NX(5), L2), (143.65, L2), (143.65, 81.00)]),
    ('I2C_SDA', 0.1, [(NX(6), YN), (NX(6), L3), (144.25, L3), (144.25, 80.62)]),
    # west lanes
    ('PWM_M1', 0.1, [(NX(9), YN), (NX(9), L1), (135.30, L1), (135.30, 81.25)]),
    ('VDD', 0.1, [(NX(8), YN), (NX(8), L2), (134.70, L2), (134.70, 80.95)]),
    ('NRST', 0.1, [(NX(7), YN), (NX(7), L3), (134.10, L3), (134.10, 80.62)]),
    # VBAT pin 1 -> VDD pin 48 at the corner, then pin 48 -> via
    ('VDD', 0.15, [(NX(1), 81.60), (141.80, EY(48)), (XE, EY(48))]),
    ('VDD', 0.2, [(XE, EY(48)), (142.95, EY(48))]),
    ('VDD', 0.2, [(XE, EY(40)), (142.95, EY(40))]),
    # west column
    ('VBUS_DET', 0.15, [(XW, WY(13)), (134.35, WY(13))]),
    ('VBAT_SNS', 0.15, [(XW, WY(14)), (133.85, WY(14))]),
    ('PWM_M3', 0.15, [(XW, WY(15)), (134.35, WY(15))]),
    ('VDD', 0.2, [(XW, WY(20)), (134.62, WY(20)), (134.35, 85.30)]),
    ('VDD', 0.2, [(XW, WY(23)), (134.62, WY(23)), (134.39, 86.90)]),
]
VIAS = [
    ('BOOT0', 143.05, 81.30), ('I2C_SCL', 143.65, 81.00), ('I2C_SDA', 144.25, 80.62),
    ('PWM_M1', 135.30, 81.25), ('VDD', 134.70, 80.95), ('NRST', 134.10, 80.62),
    ('VDD', 142.95, EY(48)), ('VDD', 142.95, EY(40)),
    ('VBUS_DET', 134.35, WY(13)), ('VBAT_SNS', 133.85, WY(14)), ('PWM_M3', 134.35, WY(15)),
    ('VDD', 134.35, 85.30), ('VDD', 134.39, 86.90),
    ('GND', 133.70, 85.40),                    # MLPF ground
    ('GND', 133.05, 81.55),                    # C36 ground
]
