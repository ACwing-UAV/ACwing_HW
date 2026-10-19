# Rev E / flow / GPS rev B: STEP models missing from the KiCad 7 library.
# Same frame convention as make_3d.py (origin = footprint origin on the board top, Y = -Y(footprint), Z up, mm).
import sys
sys.argv = sys.argv[:2]
exec(open('/home/claude/genD/make_3d.py').read().split('# ---- PowerPAK')[0])

# ---- JST SH SM04B-SRSS-TB side entry: body 6.0 x 4.25 x 2.9, mouth at footprint +Y (model -Y),
#      signal pins at footprint Y -2.0 (x -1.5..1.5), fixing tabs at (+-2.8, 1.875)
body = box(6.0, 4.25, 2.9, 0, -0.4, 0).cut(box(4.6, 3.2, 1.6, 0, -1.1, 0.6))
parts = [(body, C(.95, .95, .92), 'body')]
for k in range(4):
    parts.append((box(0.3, 1.3, 0.12, -1.5 + k, 2.0, 0), TINW, 'pin%d' % k))
for x in (-2.8, 2.8):
    parts.append((box(1.0, 1.6, 0.15, x, -1.875, 0), TINW, 'tab%g' % x))
save('JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal', parts)

# ---- WS2812B-2020: 2.0 x 2.0 x 0.84, white body, clear window with the LED die
body = box(2.0, 2.0, 0.7, 0, 0, 0.0)
win = box(1.6, 1.6, 0.14, 0, 0, 0.7)
parts = [(body, WHITE, 'body'), (win, C(.85, .9, .95), 'window'),
         (box(0.5, 0.5, 0.02, 0.0, 0.0, 0.84), C(.3, .3, .3), 'die')]
for x in (-0.92, 0.92):
    for y in (-0.55, 0.55):
        parts.append((box(0.4, 0.4, 0.02, x, -y, -0.01), GOLD, 'p%g%g' % (x, y)))
save('LED_WS2812B-2020_PLCC4_2.0x2.0mm', parts)

# ---- WSON-8 6 x 5 x 0.75 (W25Q128JVPIQ), pin 1 dot at footprint (-2.66, -1.91)
body = box(5.0, 6.0, 0.75, 0, 0, 0.0)
parts = [(body, BLACK, 'body'), (box(3.4, 4.0, 0.02, 0, 0, -0.01), TINW, 'ep'),
         (cq.Workplane('XY').circle(0.25).extrude(0.01).translate((-1.8, 2.2, 0.75)), WHITE, 'dot')]
for x in (-2.66, 2.66):
    for y in (-1.905, -0.635, 0.635, 1.905):
        parts.append((box(0.6, 0.4, 0.2, x * 0.95, -y, 0.0), TINW, 'l%g%g' % (x, y)))
save('WSON-8-1EP_6x5mm_P1.27mm_EP3.4x4mm', parts)

# ---- ST UFQFPN-20 3 x 3 x 0.55 (STM32C011F4U6), pin 1 at footprint (-1.48, -1.0)
body = box(3.0, 3.0, 0.55, 0, 0, 0.0)
parts = [(body, BLACK, 'body'),
         (cq.Workplane('XY').circle(0.15).extrude(0.01).translate((-1.0, 1.0, 0.55)), WHITE, 'dot')]
save('ST_UFQFPN-20_3x3mm_P0.5mm', parts)

# ---- PixArt PMW3901MB-TXQT COB 6 x 6 with the LN03-ZSZ lens assembly: total height 2.28 mm
base = box(6.0, 6.0, 0.6, 0, 0, 0.0)
holder = box(5.4, 5.4, 1.2, 0, 0, 0.6).edges('|Z').fillet(0.4)
lens = cq.Workplane('XY').circle(1.3).extrude(0.48).translate((-0.25, 0.382, 1.8))
parts = [(base, C(.15, .3, .15), 'cob'), (holder, BLACK, 'holder'), (lens, C(.55, .65, .75), 'lens')]
save('PixArt_PMW3901MB_COB-28_6x6mm', parts)
