# ACwing preliminary draft frame – mechanical answer to the electronics handoff

> **Revisions.** This is a design log written before the first release. The boards it describes as current are now the rev A release (FC rev A, ESC 1S rev A, GPS rev A, Flow rev A); letters marked *draft* are earlier internal iterations that were never manufactured.

**Author:** Andrea Cirillo (ACwing). **From:** mechanical / frame design. **To:** electronics design (ACwing ESC 1S,
ACwing FC, ACwing GPS, ACwing Flow).
**Date:** 2026-10-19. **Answers:** `ACwing_mechanical_handoff.md` (§0.1–0.11, §2–§8) as of 2026-10-19.
**Inputs used:** the stack-check geometry of the GPS rev A package (`stack_data.js`, config D6 = ESC 1S A + FC A + GPS A,
6 mm standoffs), the FC A pin map, the ESC 1S A / Flow A hardware notes and the Flow A DXF.
**Electronics reply:** `ACwing_frame_preliminary_draft_electronics_reply.md`.

> The frame described here is a **preliminary draft**, superseded by **Mech A1** (frame A1 + battery trays) in
> [ACwing_Mechs](https://github.com/ACwing-UAV/ACwing_Mechs).

## 0. Decision 2026-10-19 – baseline configuration of the 1S mini drone: indoor, no GPS

The GPS board (ACwing GPS rev A) is an extension for a larger outdoor drone. The 1S mini drone flies **indoor only**:
ESC 1S A + FC A + Flow A, no GPS board and no cable B.
- Corner column without GPS: insert – ESC 1S A – S1 2.57 mm – grommet with FC A – **M2 washer (Ø5 × 0.3) + M2 × 12
  screw** on the upper ball (tip at −4.3 mm: 2.3 mm into the insert). No S2.
- FC A J3 stays free (no cable B); the frame keeps the 20 × 20 stack, so the GPS board can still be fitted for tests.
- Mass ≈ 66.5 g, **thrust-to-weight ≈ 2.1** (73.2 g / 1.91 with the GPS board).
- Sections 2, 4 and 7 below describe the full stack with GPS; they stay valid for the GPS option.

## 1. What changed in the frame (from the earlier preliminary draft)

| Item | Preliminary draft (stack version) | Handoff item |
|---|---|---|
| Stack bosses | 4 bosses on the **20 × 20** pattern (board (±10, ±10) = frame (0, ±14.14), (±14.14, 0)), Ø5.2 top (= ESC keep-out r 2.6), Ø6.6 at the deck, **3 mm** tall: the ESC sits directly on them, at the old FC height (bottom −2.0) | 0.1, 0.2 |
| Fastening | **Hangtife HLTI-M2-001** hot-melt insert (M2 × 3 × Ø3.0) in a Ø2.8 × 3.4 seat in each boss; Ø2.2 clearance below | 0.2 |
| Openings | top bridge removed on **both** ±X sides. The FC USB-C plug (+X) and the ESC 1S A charge-port plug (−X) pass between the two duct rings of that side: the gap between the rings is 13.2 mm, so a plug overmold up to **13.2 mm wide** fits (checked, 0 mm³). The rings are not cut (the 14 mm stack-check envelope with its +1.7 mm side margin would break them). Use slim USB-C cables. | 0.7, 0.10 |
| ESC cable | no frame part behind the rear edge between the board and the M1 duct ring; cable modelled and checked (§4) | 0.3, 0.7 |
| Qwiic slot | new deck slot for the flow cable, board (u 20.4…22.6, v −11.1…−6.9), behind FC J4 | 3 |
| Flow tray | 1.2 mm plate fused under the bay lips (front part of the bay, clear of the rear latch tongue), 2 downward bosses Ø4.8 × 2.4 with the same M2 inserts, lightening window | 2.4 |
| Mass | frame 15.6 g PETG (earlier preliminary draft 14.8 g): +0.8 g for the bosses and the flow plate | 0.3 |

All the earlier-draft items that do not depend on the stack (cage ducts, motor holders, TPU sleeves, legs, battery bay and
latch, motor-lead clips and deck slots, battery-lead notch) are unchanged. The motor leads still reach the ESC pads at
the edge midpoints exactly as they reached the FC pads of the earlier draft.

## 2. Stack and hardware (per corner, bottom to top)

| z (frame, mm) | Part |
|---|---|
| −5.0 … −2.0 | boss with the M2 insert (insert −5.0 … −2.0) |
| −2.0 … −1.0 | ACwing ESC 1S rev A, hard-mounted (clamped by the column) |
| −1.0 … 1.57 | spacer **S1** Ø4.5 / Ø2.3 × **2.57 mm** (PETG, printed; STL supplied) |
| 1.57 … 4.0 | lower ball of the M2 damping grommet (QUARKZMAN, 6 mm, slot Ø3.03 × 1.14) |
| 4.0 … 5.0 | ACwing FC rev A in the grommet slot (Ø3.2 holes) |
| 5.0 … 7.43 | upper ball |
| 7.43 … 11.0 | spacer **S2** Ø4.5 / Ø2.3 × **3.57 mm** |
| 11.0 … 12.0 | ACwing GPS rev A |
| 12.0 … 14.0 | **M2 × 16 socket-head screw** (tip at −4.0: 2 mm into the insert, 2.2 mm above the deck underside, 2.7 mm above the battery) |

- Gap ESC top → FC bottom = **5.0 mm** (§0.3), FC top → GPS bottom = **6.0 mm** (§0.11).
- FC height: bottom 4.0 / top 5.0 mm **above the propeller plane** (§8 new item 1). SAM-M10Q top at 18.3 mm.
- Without the GPS board: M2 × 12 with a washer on the upper ball, no S2.
- **Screws must be metal (stiff).** The GPS board rides on the four screws; with nylon screws its rocking mode on the
  12 mm columns would land near the 1× propeller band. Electronics reply: use **titanium** (or A4 / 316 stainless),
  not plain steel, because of the two compasses.
- Tighten until the head just seats: the balls must not be crushed (they set the FC isolation, §6).

## 3. USB-C access, outline steps, LEDs

- FC J1 (+X) and ESC J4 charge port (−X): the plugs pass between the duct rings; overmold width ≤ 13.2 mm (checked, 0 mm³).
  The 0.8 mm outline steps of FC A and ESC 1S A are inside the deck footprint; nothing to change in the frame.
- **RGB LEDs:** the FC top is 1.1 mm above the highest frame point, so nothing of the frame is above the LEDs. Ray test
  from each LED (36 azimuths × 4 elevations, frame + all stack parts): front pair visible in 74–76 % of the
  directions, rear pair in 52–60 % (the rear connectors and the ESC cable hide the low rear-inward directions). All four
  are visible from above and from the sides.

## 4. Cables (modelled wire by wire, pin 1 to pin 1)

Pin 1 of each JST SH footprint taken from the footprint orientation (unrotated: pin 1 at −X, mouth +Y), checked
against the FC A doc (J6 pin 1 at v = +0.1).

| Cable | From → to | Route | Wire length between plug housings | Off-the-shelf? |
|---|---|---|---|---|
| **A** ESC link, JST SH 8, 1:1 | ESC 1S A J1 (top, rear edge, pin 1 at u 6.1) → FC A J2 (top, rear edge, pin 1 at u −2.0) | out of J1, up through the corridor between the rear board edge and the M1 duct top ring (the ring passes 1.5–4.5 mm behind the edge at z 2.5–3.9), shifted to +u where the corridor is wider, then back to −u above the ring and into J2. Order is kept (no crossing). | ≈ 18 mm (≈ 26 mm plug to plug) | **custom**: a 50 mm cable leaves ≈ 25 mm of slack in the propeller area; use pre-crimped SH wires cut to 30 mm |
| **B** Qwiic | FC J3 → GPS J1 | loop outside the right edge, z 5.5–13.5, ≤ 3.6 mm beyond the edge | ≈ 14 mm | **custom** (≈ 20 mm); standard Qwiic cables start at 50 mm |
| **C** Qwiic | FC J4 → Flow J1 | out of J4, over the M2 duct ring (z > 4.3), back along the edge to v = −9, down beside the ESC edge, through the new deck slot, under the deck to Flow J1 (the ribbon twists half a turn under the deck: J4 pin 1 is at the rear, Flow J1 pin 1 is at the front) | ≈ 40 mm | standard **50 mm** Qwiic; the deck slot is the tie point (≈ 12 mm from J4) |
| **D** battery pigtail | ESC 1S A J2 pads → JST PH 2.0 | off the rear corner tip, down through the deck notch, PH pair behind the bay | 20 / 15 mm | PH 2.0 pigtail 30–40 mm, 24 AWG (BoM item) |

- Colours in the model: A = GND black, VBAT red, CUR yellow, TLM white, M1 blue, M2 green, M3 orange, M4 purple;
  Qwiic = GND black, 3V3 red, SDA blue, SCL yellow.
- **Battery pads polarity:** modelled with pad 1 (inboard) = VBAT+ and pad 2 (corner tip) = GND, as the earlier-draft
  BattPads footprint (confirmed by the electronics reply).
- Cable C stays ≥ 10 mm from the M2 motor leads (§3 rule), and out of the propeller discs and the optical cones.
- Checked: wires × frame, × propellers, × all stack parts, × hardware, × the other cables, × optical cones: **0 mm³**.

## 5. Flow board (§2, §8.1–8.2)

| Item | Value |
|---|---|
| Location | under the battery bay, sensor side down, on the frame plate (never on the battery) |
| Orientation | flow **t axis → forward (+Y)**; seen from above the board is mirrored, so frame x = −s, y = 6.2 + t |
| Position | PMW3901 optical axis on the frame centre (0, 0); VL53L1X at (0, +7.0); holes at frame (±8.0, 6.6) |
| Distance from the CG axis | CG at (0.07, 0.26, −6.4) (mass model below): **lens 0.3 mm** from the vertical CG axis |
| Mounting | 2 × M2 × 4 **nylon** screws from the sensor side into M2 inserts in the plate bosses; boss contact face r 2.4 (hole keep-out); 2.4 mm boss = spacer, back side 2.4 mm from the PETG plate (plate is insulating) |
| Parallelism | the plate is part of the printed frame, parallel to the propeller plane by construction |
| Heights | back −19.3, sensor face −20.3, lens tip −22.6, ground −33.9 |
| **Lens height landed** | **11.3 mm** (ToF window 12.1 mm): below the PMW3901 80 mm minimum, so take-off and landing run on the ToF only, as planned. The VL53L1X specifies ≈ 40 mm minimum too: below that it reads short or saturates, which the take-off logic should treat as "on the ground" |
| Optical cones | PMW 42°, ToF 27°, from the windows to the ground: free of frame, legs, cables, screws (0 mm³) |
| Cable | Flow **J1** (left edge in the sensor-side view = right side of the drone), mouth to +X |

## 6. Vibration (FC on the damping balls)

Same beam model as for the earlier preliminary draft (it reproduces the earlier-draft isolation band, 62–95 Hz):

| Grommet stiffness per corner (axial / radial, N/mm) | FC A isolation modes |
|---|---|
| 0.7 / 0.6 (earlier-draft assumption) | **92–120 Hz** |
| 1.4 / 1.2 (both balls clamped, realistic for this column) | 130–167 Hz |
| 0.45 / 0.4 | 75–96 Hz |

The FC is lighter (≈ 5.5 g against 7.9 g) and the holes are farther out (r 14.1 against 11.3), so the same grommet
gives higher modes than in the earlier preliminary draft. With both balls of each grommet working, the band is above the 60–100 Hz target.
**Action:** tap test on the first build (FC IMU at ≥ 1 kHz, FFT); if the peak is above ≈ 110 Hz, use softer (gel)
balls or a longer S1/S2 pair that preloads the balls less. The structural modes of the frame were not re-run with the
earlier-draft calibration; the structure is unchanged except for the bosses and the flow plate, but the central mass grew by
≈ 14 g, so re-check the frame modes on the bench with the same tap test.

## 7. Weight budget (§0.3)

| Item | g |
|---|---|
| Frame, preliminary draft (PETG, from the mesh) | 15.6 |
| TPU sleeves ×4 | 2.2 |
| Battery 1S 20 × 40 × 8 | 20.0 |
| Motors 8520 ×4 | 11.0 |
| Propellers + motor leads | 2.0 |
| ACwing ESC 1S A (doc) | 5.0 |
| ACwing FC A (estimate: 4.0 bare + parts) | 5.5 |
| ACwing GPS A (estimate, SAM-M10Q ≈ 4 g) | 6.0 |
| ACwing Flow A (doc) | 1.5 |
| Cables + PH pigtail | 1.2 |
| 4 × M2 × 16 steel, 6 inserts, 4 grommets, spacers | 3.4 |
| **Total** | **73.2** (earlier preliminary draft: 55.8) |

With ≈ 140 g of static thrust (4 × 8520, 55 mm props, 1S) the thrust-to-weight ratio is **1.91** with everything on
board, **2.12** without the GPS board, **2.17** without GPS and flow. Below 2 the drone hovers at more than half
throttle and has little margin for wind and control. Titanium screws save ≈ 1.1 g.

## 8. Larger battery (§6)

- Current bay: **20.6 × 40.5 × 8.5 mm** (rails, front stop and rear latch; deck to lips), 1S packs up to ≈ 20–21 g.
- With the flow plate under the lips, a thicker battery needs the lips and the plate lowered together (ground clearance
  under the flow lens is 11.3 mm, so ≈ 3 mm can be taken there).
- **A battery that doubles the capacity (≈ 35–40 g) brings the full configuration to ≈ 90 g and T/W ≈ 1.55 with the
  8520 motors: not flyable with margin.** The larger battery only makes sense with stronger motors (brushless frame
  variant, §0.2/0.8) or without GPS/flow.

## 9. ELRS receiver (§4) – proposal, not modelled yet

- Mount the receiver on the outer face of the **right** battery rail, under the deck (frame x ≈ +11.5…+15, y −6…+4,
  z −14…−7): ≥ 25 mm from the GPS module, away from the BLE antenna (FC left edge) and from the charge port, out of
  the propeller discs. Antenna: ceramic chip on the receiver, or a T antenna run down and out between the right arms.
- Cable from FC J5 (front-left edge) ≈ 60 mm, down through a second deck slot at the front.
- To confirm before modelling: receiver model and antenna type.

## 10. Files

The frame files of this preliminary draft (STL, GLB, renders, checks) were working files and are superseded by
the released mechanics, **Mech A1**, in [ACwing_Mechs](https://github.com/ACwing-UAV/ACwing_Mechs)
(`00 - Docs/00 - Mech_A1_Docs`).
