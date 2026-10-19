# ACwing Flow rev A – optical flow + ToF height board for ACwing FC rev E

KiCad 7 project (it also opens in KiCad 8/9). A 21 × 25 mm board for indoor flight: it measures ground motion
(optical flow) and height (time of flight). It sits under the battery tray, sensor side down, and connects to the
FC expansion bus (Qwiic) with a standard JST SH 4-pin cable.

## Decisions (2026-10-17)
| Topic | Choice | Why |
|---|---|---|
| Flow sensor | PixArt **PMW3901MB-TXQT** + LN03-ZSZ lens | the de-facto drone flow sensor (80 mm to infinity); no ST part does far-field optical flow |
| Height | ST **VL53L1X** ToF, on the Qwiic bus (0x29) | ST part, 4 m range indoors, standard driver (ULD) |
| Bridge MCU | ST **STM32C011F4U6** (UFQFPN-20) | the PMW3901 needs SPI with exact timing; the bridge reads it at 100 Hz and serves the data over I2C, so the FC needs no extra SPI/CS lines to a cable |
| Link | Qwiic / STEMMA QT (JST SH 4-pin) × 2, pass-through | same bus as the GPS board: flow and GPS boards chain in any order |
| Supply | 3.3 V from the FC expansion LDO (VEXP); 2.0 V for the PMW3901 core from an adjustable LDK130 | the PMW3901 VDD is 1.8–2.1 V |
| Mounting | under the battery tray, sensor side down, 2 × M2 | the FC bottom has no room (1.2 mm limit, frame deck 3 mm below); see the mechanical handoff |

## Contents
| File | What |
|---|---|
| `ACwing_Flow_A.kicad_pro / .kicad_sch / .kicad_pcb` | project, schematic, routed PCB |
| `ACwing_Flow.pretty/`, `3d/` | project footprints (custom PMW3901 COB-28 land pattern from the datasheet), STEP models |
| `ACwing_Flow_A_schematic.pdf`, `ACwing_Flow_A_DRC.rpt` | schematic, DRC report |
| `ACwing_Flow_A.step`, `ACwing_Flow_A_3D.png` | STEP of the assembled board, renders |
| `ACwing_Flow_A_BoM.xlsx` | sheet `BoM` (assembly BoM, every field filled) and sheet `Costing` |
| `ACwing_Flow_A_BoM_JLCPCB.xlsx`, `ACwing_Flow_A_CPL.xlsx` | JLC BoM with LCSC numbers, pick-and-place (30 parts, all on the sensor side) |
| `ACwing_Flow_A_gerber.zip` | Gerber + Excellon, origin at the lower-left corner |
| `ACwing_Flow_A_mech_outline.dxf` | outline, holes, sensor axes and envelopes for the frame design |
| `generator/` | regeneration scripts |

## Circuit
- **J1, J2 (Qwiic).** JST SM04B-SRSS-TB, left and right edges at t = +7.0, wired in parallel: 1 GND, 2 3.3 V,
  3 SDA, 4 SCL. No pull-ups here (they are on the FC).
- **Power.** +3V3 from the bus (FC U11, 300 mA shared with the GPS board). The board draws about 35 mA (flow 9 mA,
  ToF up to 20 mA peak, MCU 3 mA).
  - U2 LDK130PU-R (DFN-6) set to 2.0 V by R5/R6 (15k/10k: 0.8 V × 2.5).
  - PMW3901 VDD through R1 3 Ω with C1/C2 22 µF + C3 100 nF; VDDIO on 3.3 V (C4 10 µF + C5 100 nF); VREG C6 4.7 µF +
    C7 100 nF. This is the datasheet reference circuit (Fig. 8).
- **U1 PMW3901MB.** SPI mode 3, 2 MHz, to the bridge: NCS PA4, SCK PA5, MISO PA6, MOSI PA7, MOTION PA3, NRESET PA2.
  R2/R3/R4 10 k pull-ups keep it deselected and out of reset while the bridge boots.
- **U3 VL53L1X.** On the Qwiic bus at 0x29. XSHUT (PA0) and GPIO1/INT (PA1) go to the bridge, with 10 k pull-ups.
  The bridge can hold the ToF in reset, which allows an address change if a second ToF is ever added.
- **U4 STM32C011F4U6 (flow bridge).** I2C1 target at **0x3B** on PB6/PB7. Planned firmware: read the PMW3901 motion
  burst at 100 Hz, accumulate dX/dY and publish them with SQUAL and shutter, plus a data-ready counter. The register
  map is part of the indoor firmware work.
  - SWD on test pads TP1 SWDIO, TP2 SWCLK, TP3 NRST, TP4 3.3 V, TP5 GND (first programming; later updates through the
    FC are possible with an I2C bootloader).
  - D1 green status LED on PA8 (low = on).
- **Bus map (whole drone).** GPS 0x42, GPS compass 0x1E, ToF 0x29, flow bridge 0x3B: no clash.

## Mechanics
- 21.0 × 25.0 × 1.0 mm, R1.5 corners, 2 layers. Two M2 holes (Ø2.2 NPTH) at (±8.0, +0.4), keep-out r 2.4 mm.
- **All parts on one side** (the sensor side). Tallest: Qwiic connectors ≈ 2.9 mm, PMW3901 lens 2.28 mm, VL53L1X 1.56 mm.
  The back side is flat (board name only).
- Sensor axes (sensor-side view): PMW3901 at (0, −6.2), field of view 42°; VL53L1X at (0, +0.8), 27°.
- Mount it parallel to the propeller plane, no window in front of the sensors. Everything for the frame designer is
  in `ACwing_rev_E_mechanical_handoff.md` and the DXF.

## PCB
- Rules: 0.15 mm tracks / 0.12 mm clearance (Default), 0.3 mm for power; vias 0.45/0.2 mm; copper to edge 0.3 mm.
- GND pours on both layers. Every small GND pad has its own via (the sensor side is crowded and its pour breaks up),
  4 vias at the PMW3901 ground pad corners, GND stitching on a grid, and a final check that joins any isolated
  ground island with a via.
- The LDK130 DFN-6 (0.4 mm pitch) escape is pre-routed and locked: IN/EN joined outside pin 5, GND via, short stubs.
- Routing: 301 tracks, 103 vias (Freerouting + locked escapes).

## Checks
- Netlist: 0 errors (`check_net.py`, 44 nets).
- KiCad DRC (`ACwing_Flow_A_DRC.rpt`): 0 violations, 0 unconnected pads, 0 footprint errors.
- Silkscreen: 35 references on the board (5 with a short leader line), none over pads.

## Fabrication (JLCPCB)
- 2 layers, 1.0 mm FR-4, 1 oz. All parts on the top (sensor) side: single-sided assembly.
- BoM `ACwing_Flow_A_BoM_JLCPCB.xlsx`; every line has an LCSC number (PMW3901 C43496881, VL53L1X C190004,
  STM32C011F4U6TR C5456188, LDK130PU-R C157446).
- **PMW3901 lens.** The LN03-ZSZ lens is a separate item in the PixArt ordering table. Check that the LCSC/JLC part
  includes it; otherwise order the lens separately and press it on after reflow (it is not reflow-safe if it is a
  plastic lens).
- CPL rotations: the corrections learned on the FC are applied (DFN-6 +270°). Check U1 pin 1, U2, U3 and U4 in the JLC
  preview before ordering.
- Cost: about **11.1 USD per board at 10 boards, 9.4 USD at 100** (components only). The PMW3901 is about half of it.

## To check before ordering
1. ERC in KiCad 8/9.
2. PMW3901 land pattern and optical centre against the datasheet drawing (footprint made from it).
3. Lens supply (above).
4. JLC preview of the CPL.
5. The STM32C011 bridge firmware is not written yet: the board can be tested first with the ToF only (direct on the bus).

## Regeneration
`generator/run_sch.sh`, `gen_pcb_flow.py`, `loop_route.sh`, `post_route.sh`. Uses `kisch.py`, `sexp.py`, `silk_refs.py`,
`step_mesh.py` from the FC generator and `make_3d_e.py` for the missing STEP models. Freerouting is not deterministic:
`loop_route.sh` reruns it until the DRC has no unconnected item.
