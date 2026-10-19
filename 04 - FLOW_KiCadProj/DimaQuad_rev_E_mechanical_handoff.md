# DimaQuad rev E – mechanical handoff (frame C)

**From:** electronics design (DimaQuadFC rev E, DimaQuadFlow rev A, DimaQuadGPS rev A/B)
**To:** mechanical / frame design agent
**Date:** 2026-10-17
**Status:** electronics placement frozen for the items below; PCB routing still in progress (does not change any
dimension given here).

Rev E is the first prototype of the new roadmap. Compared with rev C2/D, it adds a **flow + ToF board** for indoor
flight, an **ELRS receiver port**, a **shared expansion bus (Qwiic)** for the flow and GPS boards, and two
**addressable RGB LEDs**. The FC outline, holes, grommets, motor pads, battery pads and USB-C position are
**unchanged from frame C** (`DimaQuadFC_C_routing_brief.md`, `DimaQuadFC_C_Keepouts.dxf` are still valid).

What we need from the frame:
1. A mount for the **flow board under the battery tray**, sensors facing the ground, with clear optical cones.
2. A route for one or two **Qwiic cables** (FC → GPS → flow, or FC → flow).
3. A place for an **external ELRS receiver** and its antenna.
4. Room for the **optional GPS board** stacked on the FC (unchanged from GPS rev A).
5. A battery bay that can take a **larger 1S battery** later (open item, see §6).

---

## 1. Coordinate conventions

- **FC frame (u, v):** origin at the FC centre, u to the right, v up, **FC top view**. KiCad: X = 150 + u, Y = 100 − v.
  As in frame C, the FC is mounted rotated 45°: **flight direction = FC corner (+20, +20)** (top-right corner).
- **Flow-board frame (s, t):** origin at the flow-board centre, s to the right, t up, **viewed from the sensor side**
  (the side that faces the ground). Seen from above the drone, the board is mirrored (s → −s).
- Units: mm. Heights are above the PCB surface on the side named.

## 2. Flow board – DimaQuadFlow rev A

### 2.1 Board
| Item | Value |
|---|---|
| Outline | 21.0 (s) × 25.0 (t) mm, corner radius 1.5 mm |
| Thickness | 1.0 mm FR-4, 2 layers |
| Mass | ≈ 1.5 g (board + parts, no cable) |
| Holes | 2 × M2, Ø2.2 mm plain (NPTH), at **(−8.0, +0.4)** and **(+8.0, +0.4)** → 16.0 mm apart along s |
| Hole keep-out | r 2.4 mm around each hole, both sides: no copper, room for M2 nylon screw heads / standoffs (Ø ≤ 4.5 mm) |
| Sensor side | **all parts are on this side**; tallest: Qwiic connectors ≈ 3.0 mm, PMW3901 lens 2.28 mm, VL53L1X 1.56 mm, the rest ≤ 1.0 mm |
| Back side | **no parts** (flat; vias and copper only). Mount it against the tray with ≥ 1 mm nylon spacers, or an insulating layer (Kapton, 3D-printed plate) if the tray is carbon |

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
| J1 | Qwiic / STEMMA QT (JST SH 1.0 mm, 4-pin, side entry) | left edge, t = +7.0 | toward −s |
| J2 | same | right edge, t = +7.0 | toward +s |

J1 and J2 are wired in parallel (pass-through). Only one is used in a simple FC → flow chain; both are used when the
flow board is in the middle of a chain. Leave **≈ 10 mm beyond the used edge** (t +3.5 … +10.5) for the plug and the
cable bend (`QWIIC_PLUG_ZONE` in the DXF).

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
- `DimaQuadFlow_A_mech_outline.dxf` – sensor-side view, layers: `OUTLINE`, `HOLES_M2`, `HOLE_KEEPOUT_R2.4`,
  `PMW3901_LENS_6x6`, `PMW3901_OPTICAL_AXIS`, `VL53L1X_PACKAGE`, `VL53L1X_AXIS`, `QWIIC_PLUG_ZONE`,
  `SENSOR_SIDE_PARTS_MAX_3.0MM`, `NOTES`.
- A full STEP of the flow board will follow with the flow-board release package (same outline, holes and sensor
  positions as the DXF).

## 3. Expansion bus and cables (Qwiic)

The FC has **one** Qwiic port; the flow and GPS boards each have **two** (pass-through), so they daisy-chain.

| Port | Board | Position | Mouth |
|---|---|---|---|
| **J3** (Qwiic, JST SH 4-pin) | FC rev E | right edge, (u, v) = (+16.9, +7.8), top side | toward +u (right edge) |
| J1 / J2 | flow board | §2.3 | ±s |
| J1 / J2 | GPS board rev B | two Qwiic ports, positions in the GPS rev B release (rev A had one 6-pin JST SH at its right edge) | — |

Supported configurations (all on the same bus):
- **Indoor:** FC J3 → flow J1.
- **Outdoor:** FC J3 → GPS J1.
- **Both:** FC J3 → GPS J1, GPS J2 → flow J1.

Cable rules:
- Standard Qwiic cables (JST SH 4-pin, 1:1): 50, 100, 150, 200 mm are off-the-shelf. **Total bus length ≤ 300 mm.**
- Route the cable **down through the deck** close to J3 (right edge, front half) and along a frame member to the flow
  board. Keep it ≥ 10 mm from the motor leads and the battery leads, and away from the GPS compass (top of the stack).
- Provide **strain relief** (clip or tie point) within 20 mm of each connector: the FC floats on grommets, so the
  cable must have a small slack loop at J3 and must not pull on the FC.
- The cable must stay **out of the propeller discs** and out of the flow-board optical cones.

## 4. ELRS receiver (long-range control)

- **Port:** FC **J5**, JST SH 1.0 mm 4-pin, on the **top edge** at (u, v) = (+9.2, +16.85), mouth toward +v.
  Pinout: 1 GND, 2 VSYS (battery, 3.3–4.2 V), 3 FC RX, 4 FC TX (CRSF).
- **Receiver envelope to plan for:** up to **12 × 10 × 4 mm** (common ELRS 2.4 GHz nano receivers are 10 × 10 mm or
  smaller), **≤ 1 g**, with either a ceramic chip antenna or a **T/dipole wire antenna of 30–80 mm**.
- **Placement:**
  - mount it on the frame, not on the FC (the FC floats on grommets); a cable of 30–60 mm to J5;
  - keep it **≥ 20 mm from the GPS module** and **outside the FC antenna keep-out** (left edge, BLE chip antenna,
    see frame C keep-outs);
  - the antenna elements must stick out of any carbon part, **vertical** (or 45° V), away from the propeller discs;
  - the receiver bind button and LED should be reachable / visible, or leave a hole for them.
- Pilots choose BLE (built into the FC) or ELRS: the receiver is optional, so the frame must fly fine without it.

## 5. GPS board (optional, unchanged mechanics)

- 26 × 26 × 1.0 mm board **stacked on top of the FC** on the same 16 × 16 mm pattern, with **6 mm M2 nylon
  standoffs** (FC on its grommets → standoffs → GPS board), as in GPS rev A.
- The SAM-M10Q module (15.5 × 15.5 × 6.3 mm) is on top: the top of the stack is ≈ **13.5 mm above the FC top
  surface** (6 mm + 1.0 mm board + 6.3 mm module).
- **Sky view:** nothing conductive above the module. Any canopy over it must be RF-transparent (no carbon, no metal
  paint, no metallised film). Keep the battery and carbon parts from shading its top.
- The stack moves with the FC on the grommets: leave ≥ 1.5 mm clearance around the GPS board edges.

## 6. Open item – larger 1S battery

We are going to evaluate a **larger 1S battery to at least double the flight time** without losing too much
performance. Until that study is done:
- size the battery bay with **margin** (please report the maximum battery envelope and mass the frame can take);
- attach the flow board to the **tray**, never to the battery, so a battery change does not move the sensors;
- the battery is still inserted from the rear (frame C); the flow board and its cable must not block insertion.

## 7. Other rev E items visible on the FC (frame C still valid)

- **RGB status LEDs** (WS2812B-2020, top side): D1 front at (u, v) ≈ (+14.0, +12.6), D2 rear at ≈ (−18.6, −12.6).
  Leave them visible from outside (open area or light pipe).
- The planned piezo buzzer was **dropped** (no free top-side spot, and its magnet would sit next to the compasses).
  Beeps are produced by the motors. No mechanical provision is needed.
- J3 (Qwiic) and J5 (ELRS) are new connectors on the right and top edges; both plugs enter from outside the board
  edge: keep **≈ 8 mm beyond the edge** free for each plug and cable bend, below the propeller-disc height.
- No other change to: outline, grommet holes and keep-outs, bottom-side 1.2 mm height limit, antenna keep-out, motor
  pads and lead entries, battery pads (J2) and lead exit, USB-C plug envelope.

## 8. What we need back

1. Flow-board mounting drawing: position and orientation in the vehicle frame (which flow-board axis points
   forward), standoff/spacer type, distance from the CG axis.
2. Lens height above the ground when landed.
3. Cable routes and lengths (FC → GPS → flow), tie points.
4. ELRS receiver location and antenna routing.
5. Maximum battery envelope and mass for the larger-battery study.
