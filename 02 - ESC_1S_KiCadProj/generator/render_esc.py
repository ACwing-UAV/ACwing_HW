# DimaQuadESC rev B renders (top / isometric / bottom) from the STEP mesh made by genD/step_mesh.py.
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

G = np.load('/tmp/claude-0/meshESCB.npz')

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

# --- GPS board alone
Tg, Cg = centred(G)
fig, axs = plt.subplots(1, 3, figsize=(21, 7.5))
view(axs[0], Tg, Cg, 0, 0, 'Top: motor stages, battery pads, charge port (front-left), charger, Q5, ESC link J1')
view(axs[1], Tg, Cg, -35, -60, 'Isometric')
view(axs[2], Tg, Cg, 0, 180, 'Bottom: shunt R9 + TSC213, charger passives')
plt.tight_layout(); plt.savefig('/home/claude/outESCB/DimaQuadESC_B_3D.png', dpi=80); plt.close()

print('render written')
