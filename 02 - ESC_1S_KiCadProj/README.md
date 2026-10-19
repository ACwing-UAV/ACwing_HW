# ACwing ESC1S rev B – ACwing 1S power board (brushed) for ACwing FC rev H

KiCad 7 project (it also opens in KiCad 8/9). The power board of the 1S mini drone: battery entry, current sensor,
four brushed motor stages, and (new in rev B) a **USB-C charge port with a 1S charger**. To the FC it looks like any
4-in-1 ESC: VBAT (1S) and CUR on the standard JST SH 8-pin cable. On larger drones a commercial 4-in-1 ESC replaces
this board on the same cable.

## Rev B changes (from rev A)
| Item | Rev B | Why |
|---|---|---|
| **Charge port (new)** | J4 USB-C (HRO TYPE-C-31-M-12), power only, CC1/CC2 5.1 k (R12/R13), C8 1 µF; top side, **45° at a new front-left chamfer** (the FC USB corner mirrored about u = v) | charging moves off the FC; the edges are full (motor stages at the midpoints, holes at ±10), the corners are the only free edge spots |
| **1S charger (new)** | U2 STC4054GR, 4.2 V, **455 mA** (R14 2.2 k); D6 green LED (on = charging) + R15; R16 1 Ω + C9 4.7 µF on BAT; BAT straight to the battery terminal | ≈ 1C for a 450 mAh pack; thermal regulation in the IC |
| **Charge switch (new)** | Q5 AON7423 P-MOSFET (20 V, 4.9 mΩ @ −2.5 V) between the shunt and VBAT; R11 100 k gate pull-down (on), D5 RB521S30 from VBUS lifts the gate (off) | with USB plugged in, FC and motors are unpowered: no motor can spin while charging, and the charger terminates on the battery current alone |
| Current sensor | R9 2 mΩ + U1 TSC213 as rev A; the sensed node is now VBAT_SH (battery → R9 → Q5 → VBAT); U1 supplied from VBAT | charge current does not pass R9 (CUR reads 0 while charging) |
| Battery connection | J2 solder pads as rev A + a **JST PH 2.0 pigtail** soldered to them (BoM item, not assembled) | a board-mounted PH 2.0 does not fit: 9 mm deep against 7.3 mm between the holes and the edges (checked at every edge and corner) |
| Outline | frame C + front-left chamfer v − u = 36.2 with 0.8 mm steps at the edges | charge port |

Unchanged: motor stages Q1–Q4 / D1–D4 / R1–R8 / C2–C5, C1 470 µF bulk, J1 ESC link (rear edge, u = +6.1 … +13.1), holes,
4 layers 1.0 mm, In1 GND / In2 VBAT planes.

## Power path
```
battery (J2 pads / PH 2.0 pigtail) ─ VBAT_RAW ─ R9 2 mΩ ─ VBAT_SH ─ Q5 ─ VBAT ─ motor stages, C1, J1 pin 2 (FC)
        └─ U2 STC4054 BAT (charge in)                              ▲ gate: R11 to GND (on) / D5 from VBUS (off)
USB-C J4 VBUS ─ U2 VCC, D6 LED, D5
```
- Charging with the drone plugged together: the FC goes off (Q5 off). For configuration while charging, power the FC
  from its own USB-C.
- Q5 conduction loss at 4 A (hover): ≈ 80 mW; at 8 A peak ≈ 0.3 W.

## ESC link J1 (unchanged)
1 GND, 2 VBAT, 3 CUR (0.1 V/A), 4 TLM (n.c.), 5–8 M1–M4. 1:1 JST SH 8-pin cable to FC rev H J2.

## Placement (board frame, FC top view: front = +u +v)
| Part | Where |
|---|---|
| J4 USB-C | top, (−15.77, +15.77), axis at 45°, mouth at the front-left chamfer |
| U2, C8, C9, D6 | top, front-left, next to J4 (U2 at (−16.0, +6.6)); R12–R16 bottom |
| Q5 | top, left edge, (−17.1, −6.5), source pins toward the shunt; 7 + 7 vias for VBAT_SH / VBAT |
| R11, D5 | top, east of Q5 |
| R9, U1 | bottom, as rev A |

## Checks
- Netlist: 0 errors (`check_net.py`, 33 nets).
- KiCad DRC (`ACwing_ESC1S_B_DRC.rpt`): **0 violations, 0 unconnected pads, 0 footprint errors**.
- Routing: 133 tracks, 248 vias (power pours and fixed paths + Freerouting for the charger signals).

## Stack check (ESC B + FC H + GPS C)
Interactive 3D page: "ACwing Stack Check". Every part is a prism (courtyard × datasheet height), every connector gets
a mated-plug envelope. Results:
- **6 mm FC → GPS standoffs (as designed): 5 clashes.** The GPS board connector J1 (bottom side, right edge) sits right
  above FC J3/J4: with plugs inserted they overlap by 0.6 mm (plugs) and 0.2 mm (plug on receptacle). GPS J2 (unused
  in rev H) would hit the FC ESC-A plug.
- **8 mm standoffs: no clash**, nothing under 0.39 mm (charge port and FC USB next to the grommet hardware).
- Charge port plug vs FC board: solved by chamfering the FC rev H front-left corner (v − u = 36.6); before, the plug
  overmold ran 0.1 mm under the FC corner.

## Fabrication (JLCPCB)
- 4 layers, 1.0 mm FR-4, parts on both sides (top 30, bottom 10).
- New LCSC parts: AON7423 C99711, STC4054GR C262930, TYPE-C-31-M-12 C165948, RB521S30T1G C8523, XL-1005UGC C965793.
- CPL: corrections as rev A (PowerPAK +270°, 7343 +180°, SMAF +180°), TSOT-23-5 +180° as the FC charger. Check Q5 pin 1,
  U2 and J4 in the JLC preview.
- **Cost:** about **6.4 USD per board at 10 boards, 5.1 USD at 100** (components only; rev A 3.8 / 3.0).
- Off-board: PH 2.0 pigtail (30–40 mm, 24 AWG) soldered to J2; check the battery plug polarity (not standardised).

## To check before ordering
1. ERC in KiCad 8/9.
2. AON7423 land pattern (Vishay PowerPAK 1212-8 footprint, as Q1–Q4) against the AOS drawing.
3. Frame: new front-left chamfer on both the power board and the FC; USB-C access at that corner.
4. Charger temperature at 455 mA (raise R14 to 3.3 k for 300 mA if it runs hot).

## Contents
| File | What |
|---|---|
| `ACwing_ESC1S_B.kicad_pro / .kicad_sch / .kicad_pcb` | project, schematic, routed PCB |
| `ACwing.pretty/`, `3d/`, `ACwing.kicad_sym` | project footprints, STEP models, symbols |
| `ACwing_ESC1S_B.step`, `ACwing_ESC1S_B_3D.png` | STEP and board views |
| `ACwing_ESC1S_B_BoM.xlsx` | sheets `BoM` and `Costing` |
| `ACwing_ESC1S_B_BoM_JLCPCB.xlsx`, `ACwing_ESC1S_B_CPL.xlsx` | JLC BoM (LCSC numbers) and pick-and-place (40 parts) |
| `ACwing_ESC1S_B_gerber.zip` | Gerber (4 copper layers) + Excellon |
| `ACwing_ESC1S_B_schematic.pdf`, `ACwing_ESC1S_B_DRC.rpt` | schematic, DRC report |
| `generator/` | regeneration scripts (`build_all_esc.sh`), stack check (`stack_check.py`) |
