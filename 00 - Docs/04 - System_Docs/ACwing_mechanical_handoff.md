# ACwing – mechanical handoff (preliminary draft frames)

> **Revisions.** This is a design log written before the first release. The boards it describes as current are now the rev A release (FC rev A, ESC 1S rev A, GPS rev A, Flow rev A); letters marked *draft* are earlier internal iterations that were never manufactured.

**From:** electronics design (ACwing FC, ACwing ESC 1S, ACwing Flow, ACwing GPS)
**To:** mechanical / frame design agent
**Date:** 2026-10-17, **updated 2026-11-07** (§0 supersedes the older items it names; §0.9 = FC rev A, §0.10 = power board rev A + stack check; §0.11 = GPS rev A, 6 mm standoffs; §0.12 = layout update 2026-10-24; §0.13 = layout and routing 2026-11-02/03; §0.14 = stack connectors 2026-11-06; §0.15 = 1.6 mm boards 2026-11-07)
**Status:** §0 is a decided architecture change; **§0.7 gives the draft F boards as designed** (ACwing ESC 1S draft A, ACwing FC
draft F, ACwing GPS draft C: connector coordinates, USB corner, LEDs, heights). §2 (flow board) is final.

> **Current state (rev A, 2026-11-07).** Read §0.13–§0.15 first: they override the connector positions, hole types,
> board thickness and heights given in the older sections. §2–§5 are updated to rev A. All boards are **1.6 mm**.
> Stack heights in the frame A1 (frame z, ESC 1S bottom at −2.0 on the bosses): **ESC 1S −2.0 … −0.4, FC 4.6 … 6.2,
> GPS 12.2 … 13.8, SAM-M10Q top 20.1** (same as ESC bottom = 0 → 0 … 1.6 / 6.6 … 8.2 / 14.2 … 15.8 / 22.1, §0.15).

## 0. Update 2026-10-18 – new stack: motor board + FC, 20 × 20 mm holes

The draft E FC was not ordered. Its microcontroller sat in a corner with one pin row 0.6 mm from the board edge, and the
four motor stages filled the edge midpoints, so routing was at its limit. The decision is:

| # | Change | What it means for the frame |
|---|---|---|
| 0.1 | **Mounting holes 20.0 × 20.0 mm** (was 16 × 16), centred, on every stacked board | frame bosses move to the 20 × 20 pattern (the FPV standard for M2 stacks); off-the-shelf 20 × 20 brushless 4-in-1 ESCs and FCs fit the same frame later |
| 0.2 | **New motor board "ACwing ESC 1S"** under the FC | it takes the place of today's FC in the preliminary draft frame (see 0.4) |
| 0.3 | FC without motor stages, battery pads or shunt | the FC becomes a "logic" board soft-mounted above the motor board |
| 0.4 | **Four RGB status LEDs**, symmetric about the board centre: two at the front end and two at the rear end of the front–rear diagonal (navigation lights) | leave both ends of the diagonal visible from outside |

### 0.1 Hole pattern
- 4 holes at (u, v) = (±10.0, ±10.0), Ø3.2 mm, for M2 anti-vibration grommets (same grommet type as the preliminary draft frame).
- Component keep-out unchanged: r 3.0 mm on the top, r 3.6 mm on the bottom (frame boss Ø5.2 + flange).
- Minimum board for this pattern with these keep-outs: about 28.5 × 28.5 mm.

### 0.2 Motor board – ACwing ESC 1S draft A (new)
- **Outline and place in the frame: identical to today's FC in the preliminary draft frame** – 40 × 40 mm, R3 corners, mounted at 45°,
  front = top-right corner (+20, +20). It sits where the FC sits today: 3 mm above the deck, battery under the deck.
- Carries the parts that drove the preliminary draft frame layout:
  - motor pads at the four edge midpoints, same positions, same motor-lead slots on the CCW side;
  - battery pads at the rear corner, same lead exit through the deck notch;
  - bulk capacitor, current shunt.
- **Hard-mounted** on the 20 × 20 bosses with M2 screws or nylon standoffs (it carries the battery current; no
  grommets needed).
- Heights: top side ≤ 3.0 mm (470 µF bulk capacitor, 2.8 mm); bottom side ≤ 1.2 mm (deck 3 mm below, as today).
- 4 layers, 1.0 mm thick as designed (see §0.7); **1.6 mm since 2026-11-07** (§0.15).
- Brushless upgrade: an off-the-shelf **20 × 20 1S brushless 4-in-1 ESC** replaces this board on the same holes and
  the same FC cable. It needs brushless motors and its own frame mounts for them, so that variant is a later frame.

### 0.3 FC above the motor board
- **FC outline stays 40 × 40 mm** (no enlargement needed, see below), same 45° orientation and front corner.
- **Mounting:** on M2 grommets on the 20 × 20 pattern, above the motor board.
- **Gap motor board top surface → FC bottom surface ≥ 4.5 mm**, so that the 2.8 mm capacitor clears the FC bottom
  parts (≤ 1.2 mm) with margin. Recommended: 5 mm grommet/spacer stack.
- The FC therefore sits about **6 mm higher** than in the preliminary draft frame (5 mm gap + 1.0 mm motor board). Please re-check:
  - the propeller-disc clearance above the board outline;
  - the duct/cage height;
  - the USB-C plug access at the right corner (its exact position may move in draft F; it stays on the right corner).
- **FC–motor board link:** standard 4-in-1 ESC cable, JST SH 8-pin, 1:1, 25–35 mm, both ends top side. Leave about
  8 mm beside the stack at one edge for the plug and a small loop (edge to be fixed in the draft F placement; not the
  left edge, which holds the BLE antenna). The FC floats on grommets: the cable must not be tight.
- BLE chip antenna: still on the FC left edge. Nothing conductive (carbon, metal) beside it; the motor board under
  it will have a copper keep-out (electronics side).
- FC bottom side: parts ≤ 1.2 mm (unchanged).

**Does the FC need to grow? No – except a 0.8 mm step at the USB corner (§0.7).** Removing the four motor stages, the battery pads, the shunt and the 470 µF capacitor
frees about 40 % of the board. The 20 × 20 holes then leave a 14 mm wide free cross in the centre: the 7 × 7 mm
microcontroller goes there with room to escape on all four sides; the IMU sits next to it, also on the top side
(draft F as designed: the In1 ground plane shields it from the motor board).
- The pattern alone would allow a ~30 × 30 mm FC.
- We keep 40 × 40 for four reasons:
  - a larger ground plane for the BLE antenna;
  - room for the connectors at the edges;
  - the same outline as the motor board (one stack envelope for the frame);
  - no change to the frame's footprint.
- To limit the added weight, the FC may go from 1.6 mm to 1.0 mm thickness (about −1.7 g).

**Weight:** the motor board, stack hardware and cable add about +3 to +4 g; a 1.0 mm FC recovers about 1.7 g.

### 0.4 RGB status LEDs
- **Four** WS2812B-2020 (2.0 × 2.0 × 0.84 mm) on the FC top side, one chain from one MCU pin.
- Two near the front corner (+20, +20) and two near the rear corner (−20, −20), placed as mirror images about the board
  centre, one each side of the diagonal (navigation lights: e.g. green/red at the front, white at the rear).
- Both ends must be visible from outside the frame (open area or light pipe).

### 0.5 Other boards
- **GPS board:** holes move to 20 × 20, so the board grows from 26 × 26 to about **30 × 30 mm**. It still sits inside
  the FC outline. The 6 mm M2 standoffs and the SAM-M10Q height are unchanged; the stack top rises with the FC (0.3).
- **Flow board:** unchanged (§2).

### 0.6 Superseded items
- §5 "16 × 16 mm pattern" and "26 × 26 board": replaced by 0.1 / 0.5.
- §3 and §4 connector coordinates (FC J3 at (+16.9, +7.8), J5 at (+9.2, +16.85)): they move in draft F, coordinates follow
  with the new placement. Edges and plug-zone sizes stay as described.
- §7 RGB LED positions: replaced by 0.4.
- §7 "no change to outline, grommet holes and keep-outs, motor pads, battery pads": the outline, motor pads, battery pads,
  lead exits and keep-out radii now belong to the motor board (0.2); the hole pattern changes (0.1).
- Unchanged: §1, §2 (flow board), §6 (larger battery), §8 (what we need back) plus the new items in §8.

### 0.7 Draft F boards as designed (2026-10-18)
Same (u, v) frame as §1 (FC top view, front = (+20, +20)). Heights are above the board surface on the side named.

**ACwing ESC 1S draft A (motor board)**
| Item | Value |
|---|---|
| Outline | identical to the draft E FC: 40 × 40 mm, R3 corners, 5 mm chamfer at the rear-right corner (no USB on this board; kept for one outline in the frame) |
| Board | 4 layers, 1.0 mm; mass ≈ 5 g with parts (rev A: 1.6 mm, ≈ 6.8 g with parts, §0.15) |
| Holes | 4 × Ø2.2 mm NPTH (M2) at (±10, ±10); keep-out r 2.6 mm both sides. Hard mount (screws or nylon standoffs) |
| Motor pads, battery pads | same positions as the preliminary draft frame (edge midpoints; rear corner, leads off the corner tip) |
| **J1 ESC link** | JST SH 8-pin side entry, **top side, rear edge**: pins at u = +6.1 … +13.1, v = −14.9; body u +4.0 … +15.0, v −15.5 … −19.7; mouth toward −v at the edge; height 2.9 mm |
| Heights | top ≤ 2.9 mm (J1 2.9, C1 2.8 at u −11 … −4, v −19.5 … −15.2); bottom ≤ 1.1 mm (shunt corner only) |

**ACwing FC draft F**
| Item | Value |
|---|---|
| Outline | preliminary-draft frame outline 40 × 40 (R3) **plus a 0.8 mm step at the USB corner**: right edge u = +20.8 from v = −12.3 down to the chamfer, rear edge v = −20.8 from u = +12.3 to the chamfer (45° steps from (+20, −11.5) and (+11.5, −20)); chamfer line u − v = 36.2 from (+20.8, −15.4) to (+15.4, −20.8) (draft E: u − v = 35). DXF: `ACwing_FC_F_outline.dxf` |
| Why the step | the (+10, −10) grommet of the 20 × 20 pattern reached the USB-C pads at the draft E position: the receptacle moved 0.85 mm outward along the diagonal and its front shell legs need the edge to follow |
| Board | 4 layers, 1.0 mm; mass ≈ 4 g bare (rev A: 1.6 mm, ≈ 5.8 g bare, §0.15) |
| Holes | 4 × Ø3.2 mm plated at (±10, ±10) for M2 grommets; copper keep-out r 2.75, components r 3.0 top / 3.6 bottom (as §0.1) |
| **J1 USB-C** | top side, centre (+15.77, −15.77), axis at 45° toward the corner, mouth at the chamfer (0.35 mm beyond it, as draft E); plug zone: 10 mm wide × 15 mm along the diagonal beyond the chamfer |
| **J2 ESC link** | JST SH 8-pin side entry, **top side, rear edge**: pins u = −2.0 … +5.0, v = −14.9; body u −4.1 … +7.1, v −15.5 … −19.7; mouth toward −v; height 2.9 mm |
| ESC cable | JST SH 8-pin, 1:1, ≈ 50 mm. From the motor-board J1 (top, rear edge) up and back into the FC J2 (top, rear edge, 8 mm to the left): an S behind the stack. Keep free behind the rear edge: u −5 … +16, 8 mm out, from the motor-board top to 4 mm above the FC top |
| J3 Qwiic | top side, right edge, (+16.9, +2.8), mouth +u |
| J5 ELRS | top side, top edge, (+2.0, +16.85), mouth +v |
| RGB LEDs D1–D4 | top side, 2.0 × 2.0 × 0.84 mm: D1 (−11.0, −18.4) rear-right edge, D2 (−18.4, −11.0) rear-left edge, D3 (+11.0, +18.4) front-left edge, D4 (+18.4, +11.0) front-right edge. Mirror pairs about the u = v diagonal; light visible over the edges |
| Antenna | BLE chip antenna unchanged: left edge, keep-out u −20.5 … −17.5, v +9 … +20.5 |
| Heights | top ≤ 3.2 mm (USB-C 3.2, J2/J3/J5 2.9); bottom ≤ 1.0 mm (passives, flash; USB-C shell legs protrude ≈ 0.8 mm under the USB corner) |

**Stack**
- Motor board top surface → FC bottom surface **≥ 4.5 mm (5 mm recommended)**: under the FC only passives (≤ 1.0 mm);
  the tallest motor-board parts (J1, C1) are not under FC bottom parts taller than 1 mm.
- FC on grommets → 6 mm M2 nylon standoffs → GPS draft C (as §5, new pattern).

**ACwing GPS draft C**
| Item | Value |
|---|---|
| Outline | 30 × 30 mm, R2 corners, centred on the FC, 1.0 mm (rev A: 1.6 mm), 2 layers |
| Holes | 4 × Ø2.2 mm NPTH at (±10, ±10), keep-out r 2.6 mm both sides |
| J1 / J2 Qwiic | bottom side; J1 right edge mouth +u, J2 rear edge mouth −v (as draft B, on the larger board) |
| Height | SAM-M10Q on top: stack top ≈ 13.5 mm above the FC top (6 mm standoffs + 1.0 mm + 6.3 mm); rev A 1.6 mm: ≈ 13.9 mm (§0.15) |

### 0.8 FC draft G: commercial brushless 4-in-1 ESC option (2026-10-18)
- FC draft G = draft F mechanics (same outline, holes, connector positions, heights). New on the FC: two solder pads
  TP9 / TP10 on the bottom at the left edge, (−17.6, −3.6) / (−17.6, −6.4), for an optional external current sensor
  wire pair.
- The FC now takes **1S–3S** on the ESC link, so a commercial 20 × 20 brushless 4-in-1 ESC can replace ACwing ESC 1S.
  Stand-alone 4-in-1 ESCs start at 2S (1S brushless exists only as all-in-one FC boards). Envelope to plan for:
  boards 29 × 31 to 40 × 33 mm on the 20 × 20 holes (M2 or M3), 5–12 g, ≈ 5–6 mm tall with parts, battery leads
  14–18 AWG soldered to the ESC, often a separate low-ESR capacitor (Ø6–8 × 10–12 mm) on the battery leads.
- Brushless motors need their own mounts (a later frame variant, as §0.2 says); the FC stack is unchanged.

### 0.9 FC rev A: universal FC, 1S–6S, two ESC links, two Qwiic ports (2026-10-18)
FC rev A keeps the drafts F/G outline, holes, grommets, J1 USB-C, J2 ESC A, J5 ELRS, LEDs and antenna. Changes visible
to the frame:
| Item | Value |
|---|---|
| **J6 ESC link B** (new) | JST SH 8-pin side entry, **top side, left edge**, centre (−16.9, −3.4), mouth toward −u; body u −20.2 … −13.6, v −9.3 … +2.5; height 2.9 mm. Second 4-in-1 ESC (motors M5–M8) for hexa / octo frames; keep 8 mm free beyond the left edge for the plug and cable |
| **J7 / J8 battery pads** (new) | 2 × 2 mm solder pads, top side, left edge: VBAT+ (−18.4, +7.2), GND (−18.4, +4.1). FC supply only (thin wires, AWG 24–26) |
| J3 Qwiic | moved 0.8 mm forward: (+16.9, **+3.6**), mouth +u (GPS board cable) |
| **J4 Qwiic** (new) | top side, right edge, (+16.9, −4.3), mouth +u (flow board cable, down through the deck). GPS J2 is no longer needed: the draft F note about its plug above the FC J2 does not apply |
| Input buck | top, rear-left corner: L3 5 × 5 × **4.0 mm** at (−15.3, −15.4) – the tallest FC part after the USB-C; nothing above it except the GPS board (6 mm standoffs: 2 mm clear) |
| Heights | top ≤ 4.0 mm (L3), connectors 2.9 mm, USB-C 3.2 mm; bottom ≤ 1.0 mm (unchanged) |
| Power stage | ACwing 1S power board (ACwing ESC 1S rev A, next) or commercial 20 × 20 4-in-1 ESCs (2S–6S). Battery voltage up to 6S reaches the FC through the ESC A cable |
| Board files | `ACwing_FC_A_outline.dxf` (same outline as drafts F/G) |

### 0.10 Power board rev A and stack check (2026-10-18)
| Item | Value |
|---|---|
| **ACwing ESC 1S rev A outline** | preliminary-draft frame outline with a **new front-left chamfer** v − u = 36.2 and 0.8 mm steps (left edge u = −20.8 from v = +12.3 to +15.4, front edge v = +20.8 from u = −12.3 to −15.4), i.e. the FC USB corner mirrored about u = v. The rear-right chamfer stays |
| **Charge port** | USB-C on the power board top, centre (−15.77, +15.77), axis at 45°, mouth at the front-left chamfer. Plug zone: 12.5 mm wide × 25 mm along the diagonal, from 1.7 mm below to 4.9 mm above the power-board top |
| **FC rev A outline** | front-left corner now chamfered too: v − u = 36.6, from (−20, +16.6) to (−16.6, +20) (was R3). Keeps the charge-port plug out from under the FC |
| Battery | solder pads at the rear-left corner as draft A + a JST PH 2.0 pigtail (30–40 mm) soldered to them; no board-mounted battery connector |
| Heights | power board top ≤ 3.3 mm (USB-C 3.26, J1 2.9, C1 3.1) |
| **FC → GPS standoffs: 8 mm** (was 6 mm) | stack check with mated plugs: at 6 mm the GPS J1 plug (GPS bottom, right edge) hits FC J3/J4 and their plugs (−0.6 mm); at 8 mm no clash. Stack top ≈ 15.5 mm above the FC top |

### 0.11 GPS rev A: back to 6 mm standoffs (2026-10-19)
| Item | Value |
|---|---|
| **ACwing GPS rev A** | same 30 × 30 mm outline and M2 holes as draft C; **Qwiic J1 / J2 now on the top side**: J1 right edge (+11.88, 0), mouth +u; J2 rear edge (0, −11.88), mouth −v; height 2.9 mm |
| GNSS module | SAM-M10Q axis-aligned (was 45°), centred; top 6.3 mm |
| Bottom side | ≤ 1.1 mm (compass, backup capacitor, test pads) |
| **FC → GPS standoffs: 6 mm** | replaces the 8 mm of §0.10 (that value only applies to GPS draft C). Stack check: no clash with all plugs mated |
| Cables | FC J3 → GPS J1: loop outside the right edge from the FC top up to the GPS top. Keep 8 mm free beyond the right edge from the FC top to 4 mm above the GPS top |

---

### 0.12 Layout update (2026-10-24, boards still rev A)
| Item | Value |
|---|---|
| **FC J6 ESC link B** | moved from the left edge to the **front edge**, next to J5: centre (−8.2, +16.85), mouth +v; pins v = +14.85, u = −4.7 (pin 1) … −11.7 (pin 8); body u −14.1 … −2.3. Used only with a second 4-in-1 ESC (hexa / octo) |
| FC J5 ELRS | unchanged, (+2.0, +16.85), mouth +v: J5 and J6 side by side on the front edge |
| **FC input buck** | L3 (5 × 5 × **4.0 mm**, tallest FC part after the USB-C) now on the **left edge** at (−16.9, −4.6); U12 (−12.1, −5.0). The rear-left corner keeps only D1 / D2 and small capacitors (≤ 1.45 mm) |
| FC MCU / IMU | MCU at (0, 0); IMU at (0, −7.6) (top). Frame: nothing changes (both are low parts) |
| FC LEDs D3 / D4 | same positions, rotated 180° (light output unchanged) |
| **GPS J1** | moved to (+11.88, **+3.6**), right above FC J3: cable B goes straight up at the right edge |
| ESC 1S, Flow | unchanged |
| Stack check (ESC 1S A + FC A + GPS A, 6 mm) | 0 clashes, closest items 0.39 mm (grommet hardware, unchanged) |

### 0.13 Layout and routing update (2026-11-02, boards still rev A)
| Item | Value |
|---|---|
| **FC J2 ESC link A** | moved from the rear edge to the **front edge**, next to J6: centre (+3.6, +16.85), mouth +v (same body and height as J6). Both ESC cables now leave the FC from the front edge |
| **FC J5 ELRS** | moved to J2's old place on the **rear edge**: (+1.5, −16.9), mouth −v |
| **Cable A (FC J2 → ESC 1S J1)** | superseded by §0.14: ESC 1S J1 moved to the front edge too (short U-loop) |
| **ELRS lead** | now leaves from the FC rear edge (J5) |
| **GPS J2 (Qwiic OUT)** | moved from the rear edge to the **right edge**, under J1: (+11.88, −4.05), mouth +u. J1 IN (+11.88, +3.85), mouth +u (0.25 mm from the 2026-10-24 position) |
| **Flow J1 / J2 (Qwiic IN / OUT)** | moved from the left / right edges to the **top edge** (sensor-side view): J1 (−6.3, +8.95), J2 (+6.3, +8.95), both mouth +t. **Cable C (FC J4 → flow J1)** enters from the top edge now |
| Flow test pads | moved to the **back side** on 2026-11-03, top edge behind the Qwiic connectors: TP1 (−8.4, +7.9), TP2 (−5.6, +10.9), TP3 (0, +10.9), TP4 (+5.2, +10.9), TP5 (+8.3, +7.8), flat pads, no height; programming with the board off the drone |
| **Mounting holes (ESC 1S, GPS, Flow)** | 2026-11-03: Ø2.2 mm **plated**, 3.6 mm copper ring on both sides tied to GND (as the FC grommet holes). Same position and drill; metal screws / standoffs touch board GND |
| Heights, outlines | unchanged on 2026-11-02/03 (board thickness changed later, §0.15) |

### 0.14 Stack connectors (2026-11-06, boards still rev A)
Check of every inter-board link with the boards stacked (ESC 1S top = 0, FC bottom at +5.0, GPS bottom at +12.6 mm with the 1.6 mm boards, see §0.15):
| Link | From | To | Result |
|---|---|---|---|
| **Cable A (ESC)** | FC J2, front edge, (+3.64, +16.85), mouth +v | **ESC 1S J1 moved to the front edge**: (+9.6, +16.88), mouth +v | short 1:1 U-loop, ≈ 25–30 mm (was ≈ 100 mm around the stack with J1 at the rear). Pin 1 at the +u end on both. J1 is 6 mm east of FC J2 (M4 motor pads at the front-edge centre) |
| Cable B (Qwiic) | FC J3, right edge, (+16.9, +3.6), mouth +u | GPS J1 IN, right edge, (+11.88, +3.85), mouth +u | straight up the right edge, unchanged |
| Cable C (Qwiic) | GPS J2 OUT (+11.88, −4.05) or FC J4 (+16.9, −4.3), right edge | Flow J1, top edge of the flow board | **route it down behind the rear grommets, not straight down the right edge**: the ESC 1S M2 motor pads sit at the right-edge centre (v = 0), keep ≥ 10 mm from the motor leads. Mount the flow board with its connector edge toward the right side of the stack for the shortest cable |
| ESC B | FC J6, front edge | second 4-in-1 ESC (hexa / octo) | same edge as cable A |
| ELRS | FC J5, rear edge | receiver | rear edge now free under it |

Keep-outs: front edge **u −14 … +16**, 8 mm out, from the ESC top to 4 mm above the FC top (cable A + ESC B plugs);
the loop of cable A sits next to the M4 motor leads (front-edge centre): keep them apart with a tie point.
Stack interference check with all plugs mated: no clash (closest items are the grommet hardware, as before).
Render: `ACwing_stack_3D.png`.

### 0.15 Board thickness 1.6 mm (2026-11-07, boards still rev A)
All boards are now **1.6 mm** FR-4 (were 1.0 mm). Footprints, outlines, holes and connector positions are unchanged.
| Item | 1.0 mm (before) | 1.6 mm (now) |
|---|---|---|
| ESC 1S top surface (from its bottom) | 1.0 | **1.6** |
| FC bottom / top (5 mm grommet gap) | 6.0 / 7.0 | **6.6 / 8.2** |
| GPS bottom / top (6 mm standoffs) | 13.0 / 14.0 | **14.2 / 15.8** |
| Stack top (SAM-M10Q, 6.3 mm) | 20.3 | **22.1** |
| Grommet column (ESC + gap + FC) | 7.0 | **8.2**: M2 grommets for 1.6 mm boards (the common FPV size) |
| M2 screw through ESC + FC + standoffs + GPS | — | **+1.8 mm** longer than before |
| Flow board screws to the tray | — | **+0.6 mm** longer |
| Board mass (bare FR-4) | FC 3.0, ESC 3.0, GPS 1.7, Flow 1.0 g | FC 4.8, ESC 4.8, GPS 2.7, Flow 1.6 g: **+4.2 g** indoor (ESC + FC + Flow), **+5.2 g** with the GPS |

Checks with the 1.6 mm boards (KiCad 10): DRC 0 / 0 on all boards; stack interference check (ESC + FC + GPS, all plugs
mated): no clash, closest part FC C2 0.28 mm from the +10, +10 grommet flange; the FC USB-C shell legs no longer stick
out under the FC; RF and USB impedance unchanged (same 0.21 mm 7628 prepreg under F.Cu). Render: `ACwing_stack_3D.png`,
interactive check: `ACwing_stack_check.html`.

## 1. Coordinate conventions

- **FC frame (u, v):** origin at the FC centre, u to the right, v up, **FC top view**. KiCad: X = 150 + u, Y = 100 − v.
  As in the preliminary draft frame, the FC is mounted rotated 45°: **flight direction = FC corner (+20, +20)** (top-right corner).
- **Flow-board frame (s, t):** origin at the flow-board centre, s to the right, t up, **viewed from the sensor side**
  (the side that faces the ground). Seen from above the drone, the board is mirrored (s → −s).
- Units: mm. Heights are above the PCB surface on the side named.

## 2. Flow board – ACwing Flow rev A

### 2.1 Board
| Item | Value |
|---|---|
| Outline | 21.0 (s) × 25.0 (t) mm, corner radius 1.5 mm |
| Thickness | 1.6 mm FR-4, 2 layers (1.0 mm until 2026-11-07) |
| Mass | ≈ 2.1 g (1.6 mm board + parts, no cable) |
| Holes | 2 × M2, Ø2.2 mm **plated**, at **(−8.0, +0.4)** and **(+8.0, +0.4)** → 16.0 mm apart along s (NPTH until 2026-11-03) |
| Hole keep-out | r 2.4 mm around each hole, both sides: no parts; a Ø3.6 mm GND copper ring on both sides (metal screws touch board GND, nylon is fine too). Room for M2 screw heads / standoffs Ø ≤ 4.5 mm |
| Sensor side | **all parts are on this side**; tallest: Qwiic connectors ≈ 3.0 mm, PMW3901 lens 2.28 mm, VL53L1X 1.56 mm, the rest ≤ 1.0 mm |
| Back side | **no parts** (flat; vias, copper, the GND rings of the holes and the five SWD test pads). Mount it against the tray with ≥ 1 mm nylon spacers, or an insulating layer (Kapton, 3D-printed plate) if the tray is carbon |

### 2.2 Sensors (sensor-side view)
| Sensor | Centre (s, t) | Body | Field of view | Range |
|---|---|---|---|---|
| **PMW3901MB** optical flow (U1) | (0.0, −6.2); the optical axis is within 0.5 mm of this point | lens assembly 6 × 6 × 2.28 mm | **42° full cone** (21° half-angle) | **80 mm to infinity** above the ground; needs ≥ 110 lux on the ground |
| **VL53L1X** ToF height (U3) | (0.0, +0.8) | 4.9 × 2.5 × 1.56 mm (emitter and receiver at the two ends of the long side, along s) | **27° full cone** (13.5° half-angle) | ≈ 40 mm to 4 m (indoor), 940 nm IR |

Both optical axes are **perpendicular to the board**. The board must be mounted **parallel to the propeller plane**
(±2°): the firmware corrects tilt with the gyro, but a fixed mounting tilt shows up as drift.

### 2.3 Connectors
| Ref | Type | Position | Mouth |
|---|---|---|---|
| J1 | Qwiic / STEMMA QT (JST SH 1.0 mm, 4-pin, side entry), IN | top edge, (−6.3, +8.95) (2026-11-02; was left edge, t = +7.0) | toward +t |
| J2 | same, OUT | top edge, (+6.3, +8.95) (2026-11-02; was right edge) | toward +t |

J1 and J2 are wired in parallel (pass-through). Only one is used in a simple FC → flow chain; both are used when the
flow board is in the middle of a chain. Leave **≈ 10 mm beyond the top edge** (above J1 / J2) for the plugs and the
cable bend (`QWIIC_PLUG_ZONE` in the DXF, updated 2026-11-02).

### 2.4 Mounting rules
1. **Location:** under the battery tray, sensor side down, as close as possible to the vertical axis through the
   vehicle's centre of gravity (target: lens ≤ 20 mm from that axis). Far from the CG, the ToF height reading changes
   with roll/pitch and the flow sees extra motion.
2. **Optical cones must stay clear** of landing gear, duct rings, battery strap, cables and the cable loop, all the way
   to the ground. Check them in the landed attitude and at 20° tilt.
3. **No window or cover in front of the sensors.** A transparent cover causes crosstalk on the ToF (it reads the cover
   instead of the floor) and blurs the flow. Use open apertures only.
4. If the board sits inside a shroud or bumper, an opening at depth *d* below the sensor-side surface must be at least:
   - PMW3901: **Ø (6 + 2·d·tan 21°) + 1 mm** = Ø (7 + 0.77·d) mm, centred on (0, −6.2);
   - VL53L1X: **(5.9 + 0.48·d) × (3.5 + 0.48·d) mm** (long side along s), centred on (0, +0.8).
5. Avoid **glossy or IR-reflective surfaces** inside the ToF cone (they bias the distance), and keep the PMW cone out
   of the propeller wash shadow if possible (the sensor needs the floor lit).
6. **Landed height:** the PMW3901 only works from 80 mm above the ground. Below that (landed, take-off, last
   centimetres of landing) the firmware uses the ToF only, so there is no need to raise the board. Please report back
   the lens height above the ground when landed; it sets the take-off logic.
7. **Stiffness:** hard-mount (no grommets needed). The tray must not flex or resonate with the board on it; a light
   board on a stiff tray is the goal.
8. **Protection:** the lens and the ToF stand proud of the board; a rim or bumper 1 mm lower than the lens (i.e. more
   than 2.3 mm from the PCB) protects them on hard landings without entering the cones.

### 2.5 Files
- `ACwing_Flow_A_mech_outline.dxf` – sensor-side view, layers: `OUTLINE`, `HOLES_M2`, `HOLE_KEEPOUT_R2.4`,
  `PMW3901_LENS_6x6`, `PMW3901_OPTICAL_AXIS`, `VL53L1X_PACKAGE`, `VL53L1X_AXIS`, `QWIIC_PLUG_ZONE`,
  `SENSOR_SIDE_PARTS_MAX_3.0MM`, `NOTES`.
- `ACwing_Flow_A.step` – full STEP of the assembled flow board, in the flow-board release package (same outline,
  holes and sensor positions as the DXF).

## 3. Expansion bus and cables (Qwiic)

The FC has **one** Qwiic port; the flow and GPS boards each have **two** (pass-through), so they daisy-chain.

| Port | Board | Position | Mouth |
|---|---|---|---|
| **J3** (Qwiic, JST SH 4-pin) | FC rev A | right edge, (u, v) = (+16.9, +3.6), top side | toward +u |
| **J4** (Qwiic, 2nd port) | FC rev A | right edge, (+16.9, −4.3), top side | toward +u |
| J1 IN / J2 OUT | GPS rev A | right edge, (+11.88, +3.85) / (+11.88, −4.05), top side | toward +u |
| J1 IN / J2 OUT | flow board | top edge, (∓6.3, +8.95) (§2.3) | toward +t |

Supported configurations (all on the same bus):
- **Indoor:** FC J4 (or J3) → flow J1.
- **Outdoor:** FC J3 → GPS J1.
- **Both:** FC J3 → GPS J1 (cable B), GPS J2 or FC J4 → flow J1 (cable C).

Cable rules:
- Standard Qwiic cables (JST SH 4-pin, 1:1): 50, 100, 150, 200 mm are off-the-shelf. **Total bus length ≤ 300 mm.**
- Cable B goes straight up the right edge (FC J3 → GPS J1). Cable C (to the flow board) goes **down behind the rear
  grommets**, not straight down the right edge (the ESC 1S M2 motor pads are at the right-edge centre), then along a
  frame member to the flow board (§0.14). Keep it ≥ 10 mm from the motor leads and the battery leads, and away from the
  GPS compass (top of the stack).
- Provide **strain relief** (clip or tie point) within 20 mm of each connector: the FC floats on grommets, so the
  cable must have a small slack loop at the FC connector and must not pull on the FC.
- The cable must stay **out of the propeller discs** and out of the flow-board optical cones.

## 4. ELRS receiver (long-range control)

- **Port:** FC **J5**, JST SH 1.0 mm 4-pin, on the **rear edge** at (u, v) = (+1.5, −16.9), mouth toward −v
  (rev A since 2026-11-02, §0.13; earlier drafts had it on the front edge).
  Pinout: 1 GND, 2 VSYS (battery, 3.3–4.2 V), 3 FC RX, 4 FC TX (CRSF).
- **Receiver envelope to plan for:** up to **12 × 10 × 4 mm** (common ELRS 2.4 GHz nano receivers are 10 × 10 mm or
  smaller), **≤ 1 g**, with either a ceramic chip antenna or a **T/dipole wire antenna of 30–80 mm**.
- **Placement:**
  - mount it on the frame, not on the FC (the FC floats on grommets); a cable of 30–60 mm to J5;
  - keep it **≥ 20 mm from the GPS module** and **outside the FC antenna keep-out** (left edge, BLE chip antenna,
    see the preliminary-draft keep-outs);
  - the antenna elements must stick out of any carbon part, **vertical** (or 45° V), away from the propeller discs;
  - the receiver bind button and LED should be reachable / visible, or leave a hole for them.
- Pilots choose BLE (built into the FC) or ELRS: the receiver is optional, so the frame must fly fine without it.

## 5. GPS board (optional) – ACwing GPS rev A

- 30 × 30 × 1.6 mm board **stacked on top of the FC** on the 20 × 20 mm pattern, with **6 mm M2 standoffs**
  (FC on its grommets → standoffs → GPS board). Plated holes with a GND ring, as on the other boards.
- The SAM-M10Q module (15.5 × 15.5 × 6.3 mm) is on top: the top of the stack is ≈ **13.9 mm above the FC top
  surface** (6 mm + 1.6 mm board + 6.3 mm module), 22.1 mm above the ESC 1S bottom (§0.15).
- Qwiic J1 IN / J2 OUT on the top side, right edge (§3).
- **Sky view:** nothing conductive above the module. Any canopy over it must be RF-transparent (no carbon, no metal
  paint, no metallised film). Keep the battery and carbon parts from shading its top.
- The stack moves with the FC on the grommets: leave ≥ 1.5 mm clearance around the GPS board edges.

## 6. Open item – larger 1S battery

We are going to evaluate a **larger 1S battery to at least double the flight time** without losing too much
performance. Until that study is done:
- size the battery bay with **margin** (please report the maximum battery envelope and mass the frame can take);
- attach the flow board to the **tray**, never to the battery, so a battery change does not move the sensors;
- the battery is still inserted from the rear (preliminary draft frame); the flow board and its cable must not block insertion.

## 7. Other draft E items visible on the FC (history; superseded by §0.6–§0.15)

- **RGB status LEDs** (WS2812B-2020, top side): D1 front at (u, v) ≈ (+14.0, +12.6), D2 rear at ≈ (−18.6, −12.6).
  Leave them visible from outside (open area or light pipe).
- The planned piezo buzzer was **dropped** (no free top-side spot, and its magnet would sit next to the compasses).
  Beeps are produced by the motors. No mechanical provision is needed.
- J3 (Qwiic) and J5 (ELRS) are new connectors on the right and top edges; both plugs enter from outside the board
  edge: keep **≈ 8 mm beyond the edge** free for each plug and cable bend, below the propeller-disc height.
- No other change to: outline, grommet holes and keep-outs, bottom-side 1.2 mm height limit, antenna keep-out, motor
  pads and lead entries, battery pads (J2) and lead exit, USB-C plug envelope.

## 8. What we need back

New with §0:
- 20 × 20 frame bosses, motor-board mounting, FC grommet/spacer stack height and the resulting FC height above the
  propeller plane.
- Stack cable routes and keep-outs (front edge for cables A / ESC B, right edge for cable B, cable C behind the rear
  grommets, ELRS at the rear edge: §0.14) and the visibility of the four RGB LEDs.
- Rev A stack heights with the 1.6 mm boards and the longer screws (§0.15).
- USB-C access at the new corner position and the 0.8 mm outline step (§0.7).
- The new weight budget (§0.3).

From the first issue:

1. Flow-board mounting drawing: position and orientation in the vehicle frame (which flow-board axis points
   forward), standoff/spacer type, distance from the CG axis.
2. Lens height above the ground when landed.
3. Cable routes and lengths (FC → GPS → flow), tie points.
4. ELRS receiver location and antenna routing.
5. Maximum battery envelope and mass for the larger-battery study.
