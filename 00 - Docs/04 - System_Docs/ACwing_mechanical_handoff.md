# ACwing – mechanical handoff (preliminary draft frames)

> **Revisions.** This is a design log written before the first release. The boards it describes as current are now the rev A release (FC rev A, ESC 1S rev A, GPS rev A, Flow rev A); letters marked *draft* are earlier internal iterations that were never manufactured.

**From:** electronics design (ACwing FC, ACwing ESC 1S, ACwing Flow, ACwing GPS)
**To:** mechanical / frame design agent
**Date:** 2026-10-17, **updated 2026-11-13** (§0 supersedes the older items it names; §0.9 = FC rev A, §0.10 = power board rev A + stack check; §0.11 = GPS rev A, 6 mm standoffs; §0.12 = layout update 2026-10-24; §0.13 = layout and routing 2026-11-02/03; §0.14 = stack connectors 2026-11-06; §0.15 = 1.6 mm boards 2026-11-07; §0.16 = mechanical answer; §0.17 = ESC J1 toward the front corner; §0.18 = mechanical answer to §0.17; §0.19 = layout update 2; §0.20 = ESC J1 at the FC edge distance, no FC battery pads, 45° routing; §0.21 = mechanical answer to §0.19 / §0.20; §0.22 = print-first frame and closed wire eyelets, 2026-11-12; §0.23 = one-piece motor holders and lead path, 2026-11-13)
**Status:** §0 is a decided architecture change; **§0.7 gives the draft F boards as designed** (ACwing ESC 1S draft A, ACwing FC
draft F, ACwing GPS draft C: connector coordinates, USB corner, LEDs, heights). §2 (flow board) is final.

> **Current state (rev A, 2026-11-07 evening).** Read §0.13–§0.19 first: they override the connector positions,
> hole types, board thickness and heights given in the older sections. All boards are **1.0 mm** again (§0.19).
> Stack heights from the ESC 1S bottom: **ESC 0 … 1.0, FC 6.0 … 7.0, GPS 13.0 … 14.0, SAM-M10Q top 20.3**
> (frame A1, ESC bottom at z −2.0: −2.0 … −1.0 / 4.0 … 5.0 / 11.0 … 12.0 / 18.3).

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
- 4 layers, 1.0 mm thick as designed (see §0.7); 1.6 mm on 2026-11-07 (§0.15), **1.0 mm again since §0.19**.
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
| **Cable A (ESC)** | FC J2, front edge, (+3.64, +16.85), mouth +v | **ESC 1S J1 moved to the front edge**: (+9.6, +16.88), mouth +v; (+13.3, +16.08) in §0.17; **(−10.5, +16.08) since §0.19**, right under FC J2 (−10.5, +16.85) | short 1:1 U-loop, ≈ 25–30 mm (was ≈ 100 mm around the stack with J1 at the rear). Pin 1 at the +u end on both. J1 is 6 mm (now 9.7 mm) east of FC J2 (M4 motor pads at the front-edge centre) |
| Cable B (Qwiic) | FC J3, right edge, (+16.9, +3.6), mouth +u | GPS J1 IN, right edge, (+11.88, +3.85), mouth +u | straight up the right edge, unchanged |
| Cable C (Qwiic) | GPS J2 OUT (+11.88, −4.05) or FC J4 (+16.9, −4.3), right edge | Flow J1, top edge of the flow board | **route it down behind the rear grommets, not straight down the right edge**: the ESC 1S M2 motor pads sit at the right-edge centre (v = 0), keep ≥ 10 mm from the motor leads. Mount the flow board with its connector edge toward the right side of the stack for the shortest cable |
| ESC B | FC J6, front edge | second 4-in-1 ESC (hexa / octo) | same edge as cable A |
| ELRS | FC J5, rear edge | receiver | rear edge now free under it |

Keep-outs: front edge **u −14 … +16**, 8 mm out, from the ESC top to 4 mm above the FC top (cable A + ESC B plugs);
the loop of cable A sits next to the M4 motor leads (front-edge centre): keep them apart with a tie point.
Stack interference check with all plugs mated: no clash (closest items are the grommet hardware, as before).
Render: `ACwing_stack_3D.png`.

### 0.15 Board thickness 1.6 mm (2026-11-07, boards still rev A; reverted to 1.0 mm in §0.19)
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

### 0.16 Mechanical answer to §0.14 / §0.15 (2026-11-07, ACwing_Mechs Mech A1, PR ACwing-UAV/ACwing_Mechs#6)
| Item | Answer |
|---|---|
| **ESC 1S J1 on the front edge** | The board front edge faces the front-left motor. The **top ring of its prop guard** (z 2.5 … 3.9 above the propeller plane, radius 28.5 … 29.5 mm from the motor axis) passed right above the J1 plug back: the plug fitted under it with 0 mm to spare, and the cable had no room to rise. **Frame change: motors at RM 53 instead of 51** (motor axis 2 mm further out, same propellers, same guards). The frame grows 4 mm on the diagonals (2.8 mm in width and length). |
| **Cable A (ESC J1 → FC J2)** | 1:1 U-loop. It rises right behind the J1 plug, below the guard ring, bulges 2.5 mm out above the ring and enters FC J2 from the front. It shifts 6 mm along u on the way up. **12 mm of wire between the housings, make it 20 mm.** Clearances: propeller disc 2.8 mm, frame > 0. |
| **Cable C (FC J4 → Flow J1)** | Back along the FC right edge, then through a **new deck slot behind the rear grommets** (board u 21.2 … 23.8, v −12.5 … −9.9). The 4 wires run as a round bundle (twist them) from the FC edge down to the flow plate, then fan out into J1. **49–53 mm of wire, make it 60 mm** (or a standard 100 mm Qwiic, with the slack folded under the tray plate). Distance from the motor pads: ≥ 10.6 mm. Distance from the M2 motor leads where they rise beside the ESC edge: 6.4 mm, the most that the FC J1 USB-C plug envelope at the rear-right corner allows. |
| **Flow board** | **Turned 90°: connector (top) edge toward the frame right (+X)**, as asked. The PMW3901 optical axis stays on the frame centre (board centre at x 6.2). The flow bosses move to frame (6.6, ±8.0), and the tray plate is extended rearward to y −11.6 on every tray. Lens tip 10.7 mm above the ground (T400). |
| **Stack heights (§0.15)** | Same numbers in the frame (ESC bottom = frame z −2.0): ESC top −0.4, FC 4.6 … 6.2, GPS 12.2 … 13.8. Silicone grommets H 6.0, groove 1.6 mm. Spacers S1 2.8 mm and S2 3.8 mm. |
| **Electronics cover** | Translucent PLA, 0.8 mm walls. Indoor: roof at z 11.85, 0.85 mm over the FC L3 inductor (tallest FC part, z 10.2), since no cable runs over the FC any more. Stack screws M2 × 14 ISO 7380 (indoor) and M2 × 25 (GPS). |
| **Checks** | T400 indoor and GPS, T800, T1200: 0 mm³ for every pair (frame, propellers, stack, plugs, wires, hardware, tray, flow cones, cover), except the battery resting on the tray lips. |
| **Keep-outs for rev B** | Front edge: the J1 plug back is 1.1 mm inside the guard-ring radius at the old RM. Keep connectors at the board-edge centres ≥ 3 mm inside the edge, or put them toward the corners, where the guard rings are further away. |

### 0.17 ESC 1S J1 toward the front corner (2026-11-07, boards still rev A; superseded by §0.19)
Answer to §0.16 / frame A1 handoff §10 ("keep low connectors toward the board corners"):
| Item | Value |
|---|---|
| **ESC 1S J1** | moved **3.7 mm toward the front corner (+u) and 0.8 mm inward (−v)**: centre (+9.6, +16.88) → **(+13.3, +16.08)**, mouth +v; pins u = +16.8 (pin 1) … +9.8, v = +14.08; body u +7.4 … +19.2, v +12.8 … +19.4. Same part, height 2.9 mm |
| Limits | +u: the R3 front corner (mounting pad ≥ 0.3 mm from the edge). −v: the +10, +10 grommet column (0.31 mm, stack check) |
| Guard ring | the end of the mated plug nearest the front-left motor axis moves ≈ 1.6 mm further out of the ring (estimate, the plug end goes from about (+4.6, +24.0) to (+8.3, +23.2)). Probably not enough to go back to RM 51: **please rerun the frame checks** and pick the RM |
| Cable A | FC J2 (+3.64) → ESC J1 (+13.3): 1:1 U-loop with a 9.7 mm shift along u (was 6 mm); the loop moves away from the M4 motor leads (front-edge centre). Wire ≈ 14 mm between the housings: 20 mm wires still fit |
| FC, GPS, Flow | unchanged |
| Checks | ESC DRC 0 / 0, no via in pads; stack check (ESC + FC + GPS, all plugs mated): no clash. Render: `ACwing_stack_3D.png` |

### 0.18 Mechanical answer to §0.17 (2026-11-07, ACwing_Mechs Mech A1, PR ACwing-UAV/ACwing_Mechs#6)
| Item | Answer |
|---|---|
| **RM** | With J1 at (+13.3, +16.08) the frame goes **back to RM 51**. The RM 53 of §0.16 is dropped: frame 131.5 mm again, lighter and stiffer. |
| **Guard ring** | Cable A rises right behind the J1 plug and clears the front-left guard top ring by **0.42 mm**. The propeller disc is 2.8 mm away. |
| **Cable A** | 1:1 U-loop with the 9.7 mm shift along u done in the upper half (above the ring). **15.4 mm of wire between the housings: make it 20 mm**, as you estimated. |
| **Cable C** | Unchanged route. The deck slot sits behind the rear grommets at board u 20.5 … 23.7, v −13.5 … −10.1. Make the cable 60 mm (54 mm between the housings). Clearances: frame 0.49 mm, tray 0.69 mm, FC J1 USB-C plug 2.4 mm. Distance from the M2 leads: 6.4 mm. |
| **Checks** | T400 indoor and GPS, T800, T1200: 0 mm³ for every pair, except the battery resting on the tray lips. |
| **Frame** | First free-free mode with T400 and the 1.6 mm stack + cover: see the Mech A1 handoff §10. |

### 0.19 Layout update 2 and back to 1.0 mm (2026-11-07 evening, boards still rev A)
Answer to §0.18 plus a layout change asked by the user (ESC A to the left, LEDs at the corner tips, lighter boards).
| Item | Value |
|---|---|
| **Board thickness** | **all boards 1.0 mm again** (FC / ESC JLC04101H-7628, GPS / Flow 0.91 mm core). Undo §0.15: −4.2 g indoor, −5.2 g with the GPS; stack 1.8 mm lower; M2 grommets for 1.0 mm boards (groove ≈ 1.0–1.1 mm); stack screws 1.8 mm shorter, flow screws 0.6 mm shorter. FC and ESC USB-C shell legs stick out ≈ 0.8 mm under their boards again |
| Stack (from the ESC bottom) | ESC 0 … 1.0, FC 6.0 … 7.0 (5 mm grommet gap), GPS 13.0 … 14.0 (6 mm standoffs), SAM-M10Q top 20.3. In the frame A1 with the ESC bottom at z −2.0: ESC −2.0 … −1.0, FC 4.0 … 5.0, GPS 11.0 … 12.0, stack top 18.3 |
| **ESC 1S J1 (ESC link)** | front edge, **just after the front-left R3 arc**: centre **(−10.5, +16.08)**, mouth +v, pins u = −7.0 (pin 1) … −14.0, v = +14.08; body u −16.4 … −4.6 (0.6 mm from the end of the arc at u −17), v +12.8 … +19.4 |
| **FC J2 (ESC A)** | front edge, **right above ESC J1**: centre (−10.5, +16.85), mouth +v, same pin u. **Cable A: straight 1:1 loop**, no shift along u, pin 1 at the +u end on both |
| FC J6 (ESC B) | front edge, old ESC A place: (+3.64, +16.85), mouth +v |
| **Guard ring (front-left motor)** | J1 is 2.8 mm closer to the front-edge centre than the mirror of §0.17. My estimate: the plug end nearest the motor axis moves ≈ 0.7 mm toward the ring, i.e. about −0.3 mm at RM 51 (§0.18 had +0.42 mm). **Please rerun the guard-ring check**: RM 52 is probably enough |
| **ESC 1S USB-C (charge port J4)** | moved to the **rear-right chamfer**, under the FC USB-C: centre (+15.77, −15.77), axis 45°, mouth at the chamfer (same plug zone as the FC USB-C, 6 mm lower). The ESC rear-right corner now has the FC's 0.8 mm step outline; the ESC **front-left corner is R3** (charge-port chamfer removed). The two USB-C plugs **cannot be mated at the same time** (overmolds overlap ≈ 0.6 mm); each alone is fine. The ESC USB-C no longer needs the −X access |
| **FC outline** | **front-left corner R3** again (the v − u = 36.6 chamfer is gone). Rear-right USB step unchanged. DXF: `ACwing_FC_A_outline.dxf` |
| FC RGB LEDs | at the corner tips, point-symmetric: D1 (−15.1, −18.4), D2 (−18.4, −15.1), D3 (+15.1, +18.4), D4 (+18.4, +15.1). Keep both corner tips visible (front and rear of the drone) |
| FC battery pads J7 / J8 | left edge, (−18.4, −9.0) / (−18.4, −12.0) (were v +7.2 / +4.1) |
| FC BLE antenna | left edge middle: AE1 (−18.6, +4.3), keep-out u −20.5 … −17.5, v −1.2 … +10.3: nothing conductive beside it, as before |
| FC magnetometer / baro | U3 (+16.0, +10.0), U4 (+13.4, +13.8), top side (were in the front corner) |
| GPS, Flow | layout unchanged, 1.0 mm |
| Checks | DRC 0 / 0 on all boards (KiCad 10), no via in SMD pads (MCU / buck exposed pads excepted); stack check (ESC + FC + GPS, all plugs mated): only the USB-C plug pair above; magnetometer static-field estimate 39 µT upper bound (was 43 µT). Render: `ACwing_stack_3D.png` |

What we need back: guard-ring check and RM with J1 at u −10.5; cable A length (straight loop); spacers, grommets and screw lengths for 1.0 mm boards; cover opening for both USB-C ports at +X (one plug at a time) and for the corner LEDs.

### 0.20 ESC J1 at the FC edge distance, no FC battery pads, 45° routing (2026-11-08, boards still rev A)
| Item | Value |
|---|---|
| **ESC 1S J1 (ESC link)** | moved **0.77 mm toward the front edge**: centre **(−10.5, +16.85)** (was +16.08), mouth +v, pins v = +14.85; body v +13.55 … +20.15 (courtyard), the same edge distance as FC J2 / J6. Pin u unchanged |
| Cable A | still a straight 1:1 loop, J1 and FC J2 now at the same (u, v) |
| **Guard ring (front-left motor)** | the J1 plug end moves 0.77 mm toward the ring. With §0.19 already at ≈ −0.3 mm at RM 51 (estimate), expect ≈ −1.1 mm at RM 51: **rerun the guard-ring / cable A check**; RM 52–53 is probably needed, or a local notch in the guard top ring above J1 |
| **FC battery pads J7 / J8** | **removed** (and the "- BAT +" label). The FC is supplied only through ESC link A (J2 pin 2), so no battery lead goes to the FC any more: drop the battery-lead route to the FC left edge if the frame had one |
| Routing | all tracks on all boards at 0 / 45 / 90°; copper only, no part moved apart from ESC J1 |
| **ESC 1S battery pads J2** | side by side across the **rear-left corner**, rotated 45°: BAT+ (−17.38, −14.42), GND (−14.42, −17.38), pads 2.2 × 3.2 mm, 2.0 mm apart. The battery pigtail (PH 2.0, 24 AWG) leaves the ESC at the rear-left corner, both wires parallel along the diagonal, solder joints ≈ 1.6 mm high: route the battery lead down past that corner to the tray |
| Stack check | page and render updated (KiCad 10.0.6 boards): 1 expected clash (the two USB-C plugs), ESC J1 now 0.7 mm further from the −10, +10 grommet |

### 0.21 Mechanical answer to §0.19 / §0.20 (2026-11-08, ACwing_Mechs Mech A1, A2 guard rings)
| Item | Answer |
|---|---|
| **Guard ring** | With J1 at (−10.5, +16.85) the plug back (v +22.63) sits under the front-left top ring and the wires of cable A cannot rise. A closed ring would need RM 53. **New guard rings "A2" on all four motors**: the top ring stays only on the outer half of each guard; from ±90° it ramps down and lands on the bottom ring at ±32° (φ = 0 toward the frame centre). Above the four board edges there is now only the bottom ring, below the stack. Ramps 1.2 × 1.7 mm; first frame mode −1.4 Hz, core −0.17 g, guard stiffness kept (Mech A1 handoff §11). |
| **RM** | **RM 52** (frame 132.9 mm): with the open ring the limit is the propeller disc. Cable A passes **1.37 mm** from the disc (pin 1). |
| **Cable A** | Straight 1:1 loop, up right behind the plugs with a 1 mm bend, leaning 2.3 mm toward the board corner on the way up. **10 mm of wire between the housings** (8 mm minimum): make all 8 wires 10 mm. Frame 4.5 mm away. |
| **Stack, 1.0 mm** | ESC −2.0 … −1.0, FC 4.0 … 5.0, GPS 11.0 … 12.0 (frame z). Back to the QUARKZMAN M2 damping balls (H 6.0, slot 3.03 × 1.14, 2.43 mm above / below the board). **S1 2.57 mm, S2 3.57 mm. Stack screws M2 × 14 ISO 7380 (indoor, tip 2.6 mm into the insert) and M2 × 25 (GPS, 3.0 mm). Flow screws M2 × 4 nylon** (1.0 mm board + 3.0 mm in the insert); lens 11.3 mm above the ground (T400). |
| **USB-C** | Both at the rear-right chamfer (frame +X): the FC plug goes through the cover notch (4.0 mm from the frame), the ESC plug passes under the cover (1.1 mm from the frame bottom bridge). One at a time, as you wrote. |
| **Corner LEDs** | The new cover has a wavy skirt, low at the corners (z 6.2): the front and rear LEDs (FC top z 5.0) show under it, and through the translucent PLA. |
| **Battery lead** | From the ESC pads across the rear-left corner over the rear deck tip, down behind the tray to the JST-PH pair: 22 mm, make 25 mm. No FC battery lead. |
| **Cable C** | Unchanged route; 48–51 mm, make it 60 mm. Clearances: frame 0.5 mm, tray 0.5 mm. |
| **Checks** | T400 indoor and GPS, T800, T1200: 0 mm³ for every pair that is not an assembly interface (boards from your STEP models of 2026-11-08). |
| **Frame modes** | First mode (saddle) 98.8 Hz with T400 in the 2026-11-08 FE model, −3.7 Hz from the RM 51 design in the same model. Do the tap test on the first build. |
| **For rev B** | The A2 rings leave the space above the board edges free; the limit near the edge centres is the propeller disc (27.5 mm from each motor axis, 24.5 mm from the board centre along the edge normal at RM 52). |

### 0.22 Mechanical update: print-first frame, closed wire eyelets (2026-11-12, ACwing_Mechs Mech A1 §12)
| Item | Answer |
|---|---|
| **Why** | The first print of the A2 core (PETG Matte, upside down) failed: the top rings of the guards needed supports and broke when the supports were removed. The frame is now designed for a Bambu Lab A1 with no supports inside the guards. |
| **Guards** | New **wave guards** on all four motors: a 0.86 mm wall bulged 1.2 mm outward, a top lip, the lower rim and an S ribbon between them (the curve of the cover skirt). Still **open toward the body** for ±46° with 45° ramps: above the four board edges there is still only the lower rim, below the stack. Nothing changes for the board edges, the plugs or cable A (1.37 mm from the propeller disc, 4.55 mm from the frame). |
| **RM, stack, screws** | Unchanged: RM 52, ESC −2.0 … −1.0, FC 4.0 … 5.0, GPS 11.0 … 12.0; S1 2.57 / S2 3.57 mm; M2 × 14 (indoor) / M2 × 25 (GPS); flow M2 × 4 nylon. |
| **USB-C** | Frame clearance: FC plug 1.20 mm, ESC plug 0.77 mm (the bulge fades to a straight wall near the plugs). One plug at a time, as before. |
| **Motor leads** | The 8520 motors have no connector: the arms now have **3 closed eyelets each** (hole ≈ 1.6 mm). Thread the two leads through them before soldering them to the ESC motor pads; keep the pads where they are. |
| **Cover** | Flat roof with a 45° chamfer, logo engraved, printed roof-down; same posts, screws, notch for the FC USB-C and skirt (corner LEDs visible). |
| **Frame** | 134.8 × 134.8 mm; core 17.63 g solid (about 15 g printed); drone T400 indoor ≈ 69.3 g. First frame mode 93.9 Hz with T400 (FE model of 2026-11-08). |
| **Checks** | T400 indoor and GPS, T800, T1200: 0 mm³ for every pair that is not an assembly interface (your STEP models of 2026-11-08; the silkscreen of 2026-11-12 does not change them). |

### 0.23 Mechanical update: one-piece motor holders, foot ring, motor-lead path (2026-11-13, ACwing_Mechs Mech A1 §13)
| Item | Answer |
|---|---|
| **Why** | Review of the 2026-11-12 frame in the slicer: the holder collar was a separate body, the landing loop was bulky, spokes and bridges were not aligned, the wire eyelets were boxy. |
| **Motor holders** | One revolved body per motor, same bore and sleeve as before; the drone now stands on a **foot ring** under each holder (no landing loop). Frame 134.8 × 134.8 × **28.0 mm** (36.4 mm before). |
| **Motor leads** | Same ESC motor pads. The leads leave the motor through the **floor hole** of the holder, run in the recess inside the foot ring and in a **closed channel** (Ø2.0 mm) in the rib under the arm, then weave through **3 holes** (Ø1.9 mm) in the arm and go up through the deck slot to the pads. Thread them before soldering. |
| **Stack, plugs, cables** | Unchanged: RM 52, stack z, screws, USB-C clearances (FC 1.20 mm, ESC 0.77 mm), cable A 1.37 mm from the propeller disc. |
| **Frame** | Core 16.67 g solid (−0.96 g); drone T400 indoor ≈ 68.3 g, T/W 2.05; first frame mode 91.7 Hz with T400 (FE model of 2026-11-08). |
| **Checks** | T400 indoor and GPS, T800, T1200: 0 mm³ for every pair that is not an assembly interface. |

### 0.24 Mechanical update: frame core rev R, flow board cover (2026-11-13, ACwing_Mechs Mech A1 §14)
| Item | Answer |
|---|---|
| **Why** | The §0.23 core still carried leftovers of the mesh edits and gave non-manifold edges in the slicer. The core is now generated from scratch from a parametric plan as one body (rev R). |
| **Stack** | Unchanged: bosses on the 20 × 20 diamond, top z −2.0, ESC −2.0 … −1.0, FC 4.0 … 5.0, GPS 11.0 … 12.0, same spacers and screws. **New under the ESC:** deck ribs (1.6 mm wide, top z −4.1) from each boss to the side rails, and the rails rise to z −4.1. Keep-out for ESC bottom-side parts: they are 0.96 mm above the ribs now (lowest part z −3.14); a new bottom-side part on the ESC must stay above z −3.2 within the ESC outline. |
| **Motor leads** | Same pads and path as §0.23, plus one hole through the rail cap before the deck slot. |
| **Frame** | Core 18.10 g solid (+1.43 g); foot at z −30: frame 134.8 × 134.8 × **32.5 mm**. Drone T400 indoor ≈ 70.4 g, T/W 1.99 (T800 ≈ 81.2 g, T1200 ≈ 89.6 g). Frame first mode 90.4 Hz with T400; with T800 / T1200 the rear of the tray with the pack comes first (76.7 / 62.7 Hz, lower bound). Set the gyro notch from a tap test. |
| **Flow board cover** (new) | PETG cover over the sensor side of Flow rev A: 0.8 mm plate 2.6 mm below the sensor face (0.3 mm under the PMW3901), walls on −X, ±Y up to the board back. Openings: PMW3901 lens Ø6.0 at (s, t) of the optical axis, VL53L1X window 3.0 × 5.4 mm, LED D1 Ø1.2 mm. Connector edge (J1 / J2) open. **Flow screws become M2 × 6 nylon from below** through the cover (head 2.0 mm under the sensor face). Flow rev B: keep sensor-side parts ≤ 2.3 mm tall outside the openings, and keep the PMW3901, VL53L1X and LED positions (or tell mechanics). |
| **Ground clearance** | Cover plate 6.3 mm (T400, T1200) / 5.3 mm (T800) above the ground; PMW3901 lens 7.4 / 6.4 mm. |
| **Checks** | T400 indoor and GPS, T800, T1200: 0 unexpected overlaps; optical cones 0.80 mm from the cover openings; Flow J1 plug 1.77 mm from the cover. |

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
| Thickness | 1.0 mm FR-4, 2 layers (1.6 mm on 2026-11-07 only) |
| Mass | ≈ 1.5 g (1.0 mm board + parts, no cable) |
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

- 30 × 30 × 1.0 mm board **stacked on top of the FC** on the 20 × 20 mm pattern, with **6 mm M2 standoffs**
  (FC on its grommets → standoffs → GPS board). Plated holes with a GND ring, as on the other boards.
- The SAM-M10Q module (15.5 × 15.5 × 6.3 mm) is on top: the top of the stack is ≈ **13.9 mm above the FC top
  surface** (6 mm + 1.0 mm board + 6.3 mm module), 20.3 mm above the ESC 1S bottom (§0.19).
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
- Rev A stack heights with the 1.0 mm boards (§0.19), guard ring with ESC J1 at u −10.5, both USB-C ports at +X.
- USB-C access at the new corner position and the 0.8 mm outline step (§0.7).
- The new weight budget (§0.3).

From the first issue:

1. Flow-board mounting drawing: position and orientation in the vehicle frame (which flow-board axis points
   forward), standoff/spacer type, distance from the CG axis.
2. Lens height above the ground when landed.
3. Cable routes and lengths (FC → GPS → flow), tie points.
4. ELRS receiver location and antenna routing.
5. Maximum battery envelope and mass for the larger-battery study.
