# ACwing preliminary draft frame – electronics reply to the mechanical answer

> **Revisions.** This is a design log written before the first release. The boards it describes as current are now the rev A release (FC rev A, ESC 1S rev A, GPS rev A, Flow rev A); letters marked *draft* are earlier internal iterations that were never manufactured.

**Author:** Andrea Cirillo (ACwing). **From:** electronics design. **To:** mechanical / frame design. **Date:** 2026-10-19.
**Answers:** `ACwing_frame_preliminary_draft_mechanical_answer.md` (2026-10-19). Boards checked: ACwing ESC 1S rev A, ACwing FC rev A,
ACwing GPS rev A, ACwing Flow rev A (as packaged).

## 1. Checked and confirmed (no board change)
| Item in the answer | Electronics data | Result |
|---|---|---|
| Baseline 1S indoor: ESC 1S A + FC A + Flow A, no GPS | FC A runs without the GPS board; J3 left free | OK |
| ESC 1S A hard mount on the bosses, M2 inserts | ESC 1S A holes Ø2.2 NPTH at (±10, ±10), keep-out r 2.6 | OK |
| S1 / S2 spacers Ø4.5 | ESC keep-out r 2.6, FC keep-out r 3.0 top / 3.6 bottom, GPS keep-out r 2.6 | OK (r 2.25) |
| Grommet slot Ø3.03 × 1.14, balls Ø6 | FC A holes Ø3.2 plated, 1.0 mm board, 5.0 mm GND ring | OK; ball r 3.0 = FC top keep-out, no part inside |
| Gaps 5.0 mm (ESC → FC) and 6.0 mm (FC → GPS) | stack check D6 with all plugs mated: 0 clashes | OK |
| **Battery pad polarity** | ESC 1S A J2 pad 1 (inboard, (−13.47, −13.47)) = VBAT, pad 2 (corner tip) = GND; "+" printed next to pad 1 | **Confirmed** as modelled |
| Cable A (ESC link) ≈ 26 mm plug to plug, custom | JST SH 8, 1:1, pin 1 ESC J1 u = +6.1 → FC J2 u = −2.0 | OK; BoM note: pre-crimped SH wires cut to 30 mm |
| Cable C (Qwiic FC J4 → Flow J1), standard 50 mm, half twist | FC J4 pin 1 = GND at the rear end (v −5.8); Flow J1 pin 1 at the front | OK: a 1:1 Qwiic cable with the twist keeps pin 1 → pin 1 |
| Flow board position, lens on the CG axis, nylon screws | Flow A holes Ø2.2 NPTH at (±8.0, +0.4), keep-out r 2.4 | OK |
| ToF minimum range ≈ 40 mm against 12.1 mm landed | — | firmware: ToF below ≈ 40 mm (or saturated) = "on the ground"; take-off/landing on ToF only |
| USB plugs between the duct rings, overmold ≤ 13.2 mm | FC J1 and ESC J4 are standard USB-C receptacles | OK; user note: slim USB-C cables |
| LEDs visibility | 4 × WS2812B on the FC top | OK |

## 2. Change requested: non-magnetic stack screws
The answer specifies **steel** M2 screws (M2 × 16 with the GPS board, M2 × 12 without). Steel is ferromagnetic:
- the FC compass (IIS2MDC, front corner (+17.4, +17.4)) is 10.5 mm from the (+10, +10) screw, the GPS compass sits at
  the centre of the GPS board, 14 mm from all four screws;
- a steel screw adds hard-iron and soft-iron distortion; the soft-iron part changes with heading and is only partly
  removed by a calibration.

**Request:** titanium M2 screws (stiff enough for the GPS rocking mode, and 1.1 g lighter, which helps the thrust-to-
weight ratio of 1.91–2.12), or A4 / 316 stainless as the low-cost option (weakly magnetic only). No plain steel or
A2 / 304 (magnetic after cold heading). Nylon stays excluded, as the answer explains.

## 3. Notes for the next steps
- **Vibration:** the predicted isolation band 92–167 Hz is above the 60–100 Hz target. Agreed with the tap test on the
  first build (FC IMU at ≥ 1 kHz, FFT). The firmware can log raw IMU data to the 16 MB flash for this.
- **ELRS receiver on the right battery rail, cable ≈ 60 mm from FC J5:** fine electrically (CRSF at 420 kbaud on a
  60 mm 4-wire cable). FC J5 is on the front edge at u = +2.0, mouth +v; J5 supplies 4.1 V (VSYS), so any 5 V ELRS
  receiver with an on-board 3.3 V LDO works. Receiver model to be chosen; a ceramic-antenna receiver keeps the build
  simple.
- **Thrust-to-weight:** noted (2.12 without GPS). Board masses to update after the first build (FC A estimate 5.5 g).
