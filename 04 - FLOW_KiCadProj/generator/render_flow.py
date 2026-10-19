# DimaQuadFlow rev A renders: sensor side, isometric, back side
# (M2 standoffs 6 mm, JST SH cable sketched), from the STEP meshes made by genD/step_mesh.py.
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

G = np.load('/tmp/claude-0/meshFlow.npz')
T_FC, STANDOFF = 1.6, 6.0

def view(ax, T, C, az, el, title, lim=None):
    a, e = np.radians(az), np.radians(el)
    R1 = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
    R2 = np.array([[1, 0, 0], [0, np.cos(e), -np.sin(e)], [0, np.sin(e), np.cos(e)]])
    R = R2 @ R1
    V = T @ R.T
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); n /= (np.linalg.norm(n, axis=1)[:, None] + 1e-12)
    light = np.array([0.3, 0.4, 0.85]); light /= np.linalg.norm(light)
    sh = 0.35 + 0.65 * np.abs((n @ R.T) @ light)
    o = np.argsort(V[:, :, 2].mean(1))
    cols = np.clip(C[o] * sh[o][:, None], 0, 1)
    ax.add_collection(PolyCollection(V[o][:, :, :2], facecolors=cols, edgecolors=cols, linewidths=0.2))
    ax.set_aspect('equal'); ax.axis('off'); ax.set_title(title, fontsize=13)
    if lim:
        ax.set_xlim(*lim[0]); ax.set_ylim(*lim[1])
    else:
        ax.autoscale_view()

def centred(d, dz=0.0):
    return d['T'] - np.array([150, -100, -dz]), d['C']

Tg, Cg = centred(G)
fig, axs = plt.subplots(1, 3, figsize=(21, 8))
view(axs[0], Tg, Cg, 0, 0, 'Sensor side (faces the ground): PMW3901 (bottom), VL53L1X, MCU, Qwiic J1/J2')
view(axs[1], Tg, Cg, -35, -60, 'Isometric')
view(axs[2], Tg, Cg, 0, 180, 'Back side (against the tray): no parts')
plt.tight_layout(); plt.savefig('/home/claude/outFlow/DimaQuadFlow_A_3D.png', dpi=80); plt.close()
print('render written')
