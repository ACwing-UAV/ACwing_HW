# DimaQuadFC rev C2 – flight controller for frame C (STM32WB55CGU6)

KiCad 7 project (it also opens in KiCad 8/9). Rev C2 keeps the rev C outline, mounting, stack-up, power path,
motor stages, sensor layout and pogo grid, and replaces the parts that are not available:

| Rev C | Rev C2 | Why |
|---|---|---|
| STM32WB5MMGH6TR (module, integrated antenna) | **STM32WB55CGU6** (UFQFPN-48) + discrete RF front end | module out of stock / long lead time |
| LPS22DFTR | **LPS22HBTR** | LPS22DF out of stock; same HLGA-10 footprint and pinout |
| LIS2MDLTR | **IIS2MDCTR** | LIS2MDL out of stock; industrial grade of the same sensor: same LGA-12 footprint, pinout, registers and I2C address (0x1E) |

Kept from rev C, as decided for C2:
- **Battery.** On-board USB-C charging (STC4054) and battery solder pads J2. A BT2.0 / PH2.0 pigtail on the pads gives
  a quick-swap connector without board space.
- **Motors.** Solder pads.
- **Programming.** Pogo grid on the bottom.
- **Barometer.** Kept for altitude hold. No GPS: an external GPS (UART) or optical-flow sensor (I2C) can be added later
  on expansion pads.

## Contents
| File | What |
|---|---|
| `DimaQuadFC_C2.kicad_pro / .kicad_sch / .kicad_pcb` | project, schematic, routed PCB |
| `DimaQuad.kicad_sym`, `DimaQuad.pretty/` | project symbols and footprints (new: `MLPF-WB55-01E3`, `ST_MLPF-WB55-01E3_CSP-6`, `Grommet_PTH_3.2mm_Pad5.0mm`) |
| `3d/` | STEP models, referenced as `${KIPRJMOD}/3d/...` |
| `DimaQuadFC_C2.step`, `DimaQuadFC_C2_3D.png` | full board in STEP; top, isometric and bottom views |
| `DimaQuadFC_C2_routing.png` | F.Cu, In2 and B.Cu overlaid |
| `DimaQuadFC_C2_BoM.xlsx` | sheet `BoM`: assembly BoM (quantity, references, value, MPN, manufacturer, package, description, side, notes); sheet `Costing`: component cost per board for 10 and 100 boards (distributor prices of 2026-10-15) |
| `DimaQuadFC_C2_schematic.pdf`, `DimaQuadFC_C2_DRC.rpt` | schematic, DRC report |
| `DimaQuadFC_C2_BoM_JLCPCB.xlsx` | BoM in the JLCPCB format (Comment, Designator, Footprint, JLCPCB Part #): every line has its LCSC number, so JLC's BOM tool matches it exactly |
| `DimaQuadFC_C2_CPL.xlsx` | pick-and-place file in the JLCPCB format (Designator, Mid X, Mid Y, Layer, Rotation), 90 assembled parts |
| `DimaQuadFC_C2_gerber.zip` | Gerber (4 copper layers, mask, paste, silk, outline) and Excellon drill (PTH/NPTH), same origin as the CPL |
| `DimaQuadFC_C2.kicad_dru` | project DRC rule (thermal spokes, see Checks) |
| `DimaQuadFC_C2_Placement.csv` | placement used for the top side (rev C CSV with the C2 changes) |
| `generator/` | regeneration scripts (`build_all.sh`) |

All documentation, schematic notes, footprint descriptions and PCB texts are in English.

## What changed on the board
### MCU and RF front end (top-left corner, where the module was)
- **U2.** STM32WB55CGU6 rotated 270°, with RF1 (pin 21) facing the left edge.
  - The exposed pad goes to GND (In1 and B.Cu) through a 3 × 3 via array at 1.0 mm pitch.
  - VSSRF (22) and VSSSMPS (32) are tied straight to the exposed pad.
- **Signal chain:**

  RF1 → U8 MLPF-WB55-01E3 (integrated filter and matching) → R34 0 Ω series → C36 DNP shunt at the antenna side →
  AE1 Johanson 2450AT18A0100001E chip antenna (global P/N of the legacy 2450AT18A100E).

- **RF tracks on F.Cu, over the solid In1 GND.**
  - RF1 → MLPF IN: a straight 0.8 mm, 0.25 mm wide track. The MLPF is rotated 180° so that IN faces RF1. It is the
    matched MCU-side port, so the track is kept as short as possible.
  - MLPF OUT → R34 → antenna feed: 0.36 mm, about 50 Ω on the JLC 4-layer stack-up (7628 prepreg, 0.21 mm,
    εr ≈ 4.4). The line runs around the MLPF ground column.
  - Confirm the width with the fab's impedance calculator if you change the stack-up.
- **QFN escape (pre-routed, locked).** The pin row facing the top edge has only a 0.6 mm strip to the edge (copper-edge
  clearance 0.3 mm), so it carries three 0.1 mm lanes per side:
  - east: BOOT0, I2C_SCL, I2C_SDA;
  - west: PWM_M1, VDDA, NRST.

  Each lane ends on a via past the package corner. Pin 1 (VBAT) is tied to pin 48 (VDD) at the corner.
  - The other functions were moved to the left, bottom and right pin rows (pin map below).
  - The west pins 13–15 and the VDD pins 20, 23, 40 and 48 each have a via right outside the pin tip.
- **Antenna keep-out.** Rule area `ANTENNA_AE1`, 3 × 11.5 mm at the left edge, around AE1: no copper pour and no vias
  on any layer.
  - The In1 GND plane and the B.Cu pour end at the keep-out edge.
  - The antenna is ≥ 13 mm from the battery.
- **Clocks.** HSE only: Y1, 32 MHz NX2016SA, with no load capacitors (the STM32WB trims the HSE internally; set
  `HSE tuning` in CubeMX / AN5042).
  - **No LSE crystal.** It was dropped to free the top pin row.
  - The BLE RF wake-up clock is HSE/1024 (`CFG_BLE_LS_SOURCE = SHCI_C2_BLE_INIT_CFG_BLE_LS_CLK_HSE_1024`) and the
    RTC runs from HSE/32.
  - Consequence: with BLE active only SLEEP mode is available (no STOP/STANDBY). This does not matter in flight; it
    costs a few mA when the drone is powered but idle.
  - PC14/PC15 are not connected.
- **SMPS.** VLXSMPS → L1 2.2 µH → L2 10 nH → VFBSMPS, with C29 4.7 µF (DS13252 table 6, 8 MHz option).
  - L1 is a Sunlord MPH201210S2R2MT (2.2 µH, 0805, 1.0 mm high, 420 mA, LCSC C55755). It replaces the 10 µH Murata
    LQM21FN100M70L (4 MHz option), which is NRND, and the Würth 74479774222, which LCSC does not stock. Footprint unchanged.
  - **Firmware:** select the **8 MHz** SMPS clock (RCC_SMPS clock = HSE, prescaler giving 8 MHz). The 4 MHz setting is only for a 10 µH inductor.
  - The network works both in bypass (the reset default) and in SMPS mode.
  - Enable the SMPS in firmware to lower the MCU and radio current.
- **Decoupling.** On the bottom, around the QFN and next to the escape vias: one 100 nF per VDD pin, VDDA 100 nF + 1 µF, VDDRF
  100 nF + 100 pF C0G, VDDUSB 100 nF, NRST 100 nF. C9 is the 4.7 µF bulk.

### Magnetometer
U3 is now IIS2MDCTR on the unchanged LGA-12 footprint and routing (C18 220 nF on C1 as before). Firmware: the
LIS2MDL driver works as is (WHO_AM_I 0x40); operating range −40…+85 °C.

### Barometer
U4 is now LPS22HBTR, a drop-in on the same footprint (pin 3 already to GND).

| | LPS22HB | LPS22DF |
|---|---|---|
| Noise | ~0.0075 hPa RMS | lower |
| Maximum ODR | 75 Hz | 200 Hz |
| FIFO | 32 samples | 128 samples |
| I3C | no | yes |
| Register map / driver | different: use the ST `lps22hb` driver | `lps22df` driver |

I2C address 0x5D is unchanged.

## Firmware pin map (rev C2)
| Function | Pin | Peripheral |
|---|---|---|
| Motor PWM M1 / M2 | PA0 / PB3 | TIM2 CH1 / TIM2 CH2 |
| Motor PWM M3 / M4 | PA6 / PA10 | TIM16 CH1 / TIM1 CH3 (set MOE in TIM1 BDTR) |
| LED front / rear | PE4 / PB1 | GPIO |
| VBUS detect / VBAT sense | PA4 / PA5 | ADC1 IN9 / IN10 |
| I2C to LSM6DSV16X (+ IIS2MDC via the sensor hub, LPS22HB) | PB8 SCL / PB9 SDA | I2C1 |
| IMU INT1 / INT2, MAG DRDY, BARO INT | PA15 / PB4, PB5, PB0 | EXTI |
| UART (pogo TP1/TP2) | PB6 TX / PB7 RX | USART1 |
| USB | PA11 / PA12 | USB FS (DFU) |
| SWD | PA13 / PA14 | – |
| BOOT0 | PH3-BOOT0 (10 k pull-down, TP3) | – |
| HSE | OSC_IN / OSC_OUT | – |

- **Not connected:** pins 2, 3 (PC14/PC15), 10, 11, 12 (PA1–PA3), 16–19 (PA7, PA8, PA9, PB2), 26, 27 (AT0/AT1).
- **Changed from the first C2 draft:** the motor and LED pins changed to free the top pin row.
- **Timer frequencies.** The four motor timers are set separately to the same PWM frequency.
- **Radio stack.** The BLE stack runs on the M0+ core. Flash the wireless coprocessor firmware (`stm32wb5x_BLE_Stack_full_fw.bin`
  or `_light_`) and the FUS with STM32CubeProgrammer over SWD before the application.

## Board (unchanged from rev C)
- **Outline.** 40 × 40 mm with R3 corners and a USB-C chamfer at the right corner. The board is mounted at 45°; the
  front is the top-right corner.
- **Mounting.** 4 grommet holes, **plated in C2**: finished Ø3.2 with an exposed Ø5.0 copper ring on both sides, tied to
  GND (footprint `Grommet_PTH_3.2mm_Pad5.0mm`).
  - The ring is a seat for the grommet flange. It stiffens the hole edge and keeps the glass fibre from fraying.
  - The grommet is rubber, so there is no electrical contact with the frame.
  - The ring (r 2.5) stays inside the r 2.75 track/via keep-out.
- **Stack-up:**

  | Layer | Use |
  |---|---|
  | F.Cu | signals and motor pours |
  | In1 | solid GND |
  | In2 | VBAT ring (open at the front corner) and VDD island |
  | B.Cu | signals and GND pour |

- **Motor stages.** ×4.
- **USB.** USB-C with VBUS detect.
- **Programming.** Pogo grid 2 × 4 on the bottom:

  | | | | | |
  |---|---|---|---|---|
  | row Y 111.73 | SWDIO | SWCLK | NRST | BOOT0 |
  | row Y 114.27 | VDD | GND | TX | RX |

## RF notes – please read
1. **Small ground clearance.** AE1 has about 3 × 11.5 mm of copper-free area. The Johanson reference layout
   (2450AT18A100E evaluation board) uses more. Expect a frequency shift and lower efficiency. Range will still cover a
   ground station or phone at tens of metres, but **tune on the assembled board**:
   - measure S11 at the antenna feed with a VNA (cut the track at R34, or use a pigtail);
   - fit R34 (series L or C) and C36 (shunt) for a return loss below −10 dB at 2.40–2.48 GHz.
2. Without a VNA, leave R34 = 0 Ω and C36 empty; the link works, with reduced margin.
3. Keep the battery and its leads away from the left edge, and do not cover the antenna with carbon parts of the frame.
4. The MLPF footprint uses 0.2 mm NSMD pads, as in the ST package data. Ask the assembler for a stencil
   ≤ 0.1 mm at these pads.

## Deviations from the CSV and the brief (please review)
1. The module placement area now holds U2, U8, AE1, R34, C36 and Y1. The bottom parts (decoupling, L1, L2, C9) were
   placed by script around the MCU, clear of the escape vias.
2. Deviations carried over from rev C: C2–C5 rotated 180°, Ø3.2 holes, J1 0.1 mm inboard, SWO not connected,
   Power netclass 0.3/0.1.

## Checks done
- **Netlist.** The schematic netlist check (`check_net.py`) shows 0 errors. The PCB nets are assigned from that
  netlist.
- **`generator/check_mech.py`: OK.** Grommet keep-outs top r 3.0 / bottom r 3.6, antenna keep-out, courtyards
  ≥ 0.25 mm from the outline, bottom parts ≤ 1.2 mm, pogo clearance.
- **KiCad DRC (`DimaQuadFC_C2_DRC.rpt`): 0 errors, 0 warnings, everything connected**, with the footprint-vs-library
  check active.
  - **Project library.** Every footprint used on the board is stored in `DimaQuad.pretty` exactly as placed (3D
    models in `3d/`, pogo-pad clearance), and the board and schematic link to `DimaQuad:<name>`. KiCad 8/9 therefore
    no longer reports "footprint does not match library": that warning came from the stock KiCad libraries, which
    differ by version and by the 3D model path.
  - **Thermal reliefs.** Ten bottom GND pads (C7, C8, C9, C15, C16, C19, C21, C23, R9, R11) can take only one thermal
    spoke into the B.Cu pour. They are already tied to a GND via by their own track. The project rule file
    `DimaQuadFC_C2.kicad_dru` accepts one spoke for GND pads in the B.Cu pour (KiCad 8/9 reports the two-spoke default as
    an error).
  - **In2.** An unconnected 1.6 mm² VDD fragment near the rear corner has been removed.
- **Routing.** 1034 tracks, 219 vias.
- **RF line lengths:**

  | Segment | Length |
  |---|---|
  | RF1 → MLPF IN | 1.2 mm (pad centre to pad centre) |
  | MLPF OUT → R34 | 4.4 mm |
  | R34 → antenna / C36 | 2.6 mm |

- **USB.** D− 45.9 mm, D+ 47.8 mm, 0.20 mm wide, full speed.
- **Silkscreen.** Every assembled part has its reference on the silkscreen (0.8 mm text, 0.15 mm stroke), on its own side.
  - Labels are inside the board, clear of pads and of other parts' bodies and silk, and nearer to their own part than to
    any other.
  - In the crowded areas, twelve labels are placed in free space nearby with a 0.12 mm leader line to the part: D1, D10,
    U3, U8 (top) and C11, C18, C19, R6, R8, R10, R13, R33 (bottom).
  - R34/C36 (stacked 0402s in the RF corner) and C24/C10 sit right next to a neighbour: check them on the assembly
    drawing if in doubt.

## Fabrication files (JLCPCB)
- **BoM for JLC.** Upload `DimaQuadFC_C2_BoM_JLCPCB.xlsx`, not the detailed BoM.
  - JLC's tool guesses badly from free-text descriptions (it matched a MOSFET for 100 nF and a terminal block for the
    green LED). With the "JLCPCB Part #" column every line is matched exactly.
  - Where the original MPN is not stocked by LCSC/JLC, an equivalent was chosen (column "Notes" of the detailed BoM):
    - Samsung/FH MLCCs instead of Murata, as JLC Basic parts where possible, same or higher voltage;
    - UNI-ROYAL resistors (JLC Basic);
    - XINGLIGHT 0402 LEDs;
    - SS34F (SMAF = DO-221AC, 40 V 3 A) instead of STPS3L45AF;
    - Sunlord 2.2 µH for L1;
    - Murata LQG15HS10N for L2;
    - NDK NX2016SA-32MHZ-STD-CZS-5 (8 pF, the same as the ST-listed crystal) for Y1.
  - **U4 LPS22HBTR is out of stock at LCSC/JLC** (2026-10-16). Use JLC Global Sourcing, or send the parts you found
    as consigned parts.
  - Stock changes daily: re-match the BoM on the day you order.
- **Origin.** The drill/place origin is at the board's lower-left corner (KiCad 130, 120 mm), with X to the right and
  Y up. The Gerbers, drill files and CPL all use it, so JLC's viewer aligns the parts with the board.
  - If you plot the Gerbers again from KiCad, tick "Use drill/place file origin".
- **CPL contents.** Only the assembled parts are in the CPL. Battery/motor pads, pogo pads, mounting holes and C36
  (DNP) are left out.
  - Rotation is the KiCad footprint rotation; bottom parts use KiCad's bottom-side convention.
- **JLC rotation corrections (applied in the CPL).** JLC's library uses a different zero orientation for some packages,
  read from JLC's placement preview of this board. The CPL rotation is the KiCad rotation plus:
  - +270°: U2 (QFN-48), U5 (DFN-6), U8 (MLPF), U7 (SOT-23-6), Q1–Q4 (AON7524);
  - +180°: U1 (LGA-14), Q5 (SOT-23), U6 (TSOT-23-5), C1 (tantalum: polarity), D5–D8 (SMAF: cathode band).

  All other parts (LEDs, D9, Y1, U3, U4, Q6, AE1, J1, passives) were already right. The rule is in
  `generator/cpl.py`.
- **Final check.** Check the JLC preview once more, top and bottom: pin 1 dots, the tantalum "+", and the diode
  bands.
  - J1 is placed by its KiCad footprint origin, about 1.2 mm from the centre of its pad array; in the preview the
    receptacle sits correctly with its mouth at the chamfer.

## To check before ordering
1. ERC in KiCad 8/9.
2. CubeMX pin assignment for the STM32WB55CGU6 (table above) and the HSE tuning value.
3. MLPF-WB55-01E3 land pattern against the latest ST datasheet.
4. Antenna tuning on the first article (RF notes).
5. Points carried over from rev C: the AON7524 footprint (approximated with PowerPAK 1212-8) and SMAflat, the USB-C
   plug against the frame, the compressed grommet height.

## 3D models
STEP files inside the project (`3d/`).
- The MLPF and the 32 MHz crystal have models made for this project.
- The QFN-48 uses the KiCad 7 × 7 mm body.
- The motors sit in the frame ducts, so the motor pads have no model.

## Regeneration
`generator/build_all.sh` (Freerouting is not deterministic: if a connection is left open, rerun `routeall.sh`).
