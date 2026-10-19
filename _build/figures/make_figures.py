#!/usr/bin/env python3
"""Draws the three overview figures shown on the home page (assets/figures/overview-*.svg).

They illustrate each research direction; they are not results. To redraw after an edit:
    pip install matplotlib numpy
    python3 _build/figures/make_figures.py
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle, FancyArrowPatch
from matplotlib.colors import LinearSegmentedColormap

OUT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'figures'))
# Figures use the same typeface as the website (EB Garamond, bundled in ./fonts, SIL Open Font License).
FONT_DIR = os.path.join(os.path.dirname(__file__), 'fonts')
for f in sorted(os.listdir(FONT_DIR)):
    if f.endswith('.ttf'):
        font_manager.fontManager.addfont(os.path.join(FONT_DIR, f))
plt.rcParams.update({
    'font.family': ['EB Garamond', 'Garamond', 'Times New Roman', 'serif'],
    'font.weight': 500, 'font.size': 16, 'svg.fonttype': 'path', 'axes.linewidth': 1.0,
    'image.interpolation': 'antialiased',
})

# palette: warm ink and greys from the website, one deep accent (the site's oxblood) and a muted bronze.
# Names are kept from the earlier palette so the drawing code reads the same.
INK, GREY, MID, LIGHT, RULE = '#1b1a17', '#6a665e', '#a39e94', '#f4f2ee', '#e2ded6'
BLUE, BLUE_L = '#6b1f2a', '#f1e9e7'          # oxblood accent
AMBER, AMBER_L, AMBER_D = '#8c6d46', '#f2ede4', '#6e5434'   # bronze
TEAL, RED = '#4f5b55', '#6b1f2a'
T_LABEL, T_SMALL, T_TITLE = 17.5, 16, 18.5

W, H = 8.0, 7.0          # inches; drawing units are 160 x 140


def mute(img, keep=0.35):
    """Pulls a photo toward a warm monochrome so it sits with the restrained palette."""
    rgb = img[..., :3].astype(float)
    if rgb.max() > 1.5:
        rgb = rgb / 255
    g = rgb @ np.array([0.299, 0.587, 0.114])
    warm = np.dstack([g * 1.02, g * 0.99, g * 0.94])
    out = np.clip(keep * rgb + (1 - keep) * warm, 0, 1)
    return np.dstack([out, img[..., 3]]) if img.shape[-1] == 4 else out


def canvas(lift=10):
    """Returns (fig, bottom_axes, top_axes). Both span the figure in 160 x 140 units; the top-row axes are
    shifted up by `lift`, which sets the gap between the two rows without touching either row's layout."""
    fig = plt.figure(figsize=(W, H))
    axb = fig.add_axes([0, 0, 1, 1])
    axb.set_xlim(0, 160); axb.set_ylim(0, 140); axb.axis('off')
    axt = fig.add_axes([0, 0, 1, 1])
    axt.set_xlim(0, 160); axt.set_ylim(-lift, 140 - lift); axt.axis('off'); axt.patch.set_alpha(0)
    return fig, axb, axt


def panel(ax, x, y, title, size=12.0, track=0.42):
    """Panel title in uppercase with even letterspacing (track, in drawing units), like the site's minor headings."""
    r = ax.figure.canvas.get_renderer()
    inv = ax.transData.inverted()
    cx = x
    for ch in title.upper():
        if ch == ' ':
            cx += size * 0.16
            continue
        t = ax.text(cx, y, ch, fontsize=size, fontweight=500, color=INK, va='baseline')
        bb = t.get_window_extent(renderer=r)
        (x0, _), (x1, _) = inv.transform([[bb.x0, 0], [bb.x1, 0]])
        cx += (x1 - x0) + track


def arrow(ax, p, q, color=MID, lw=1.3, ls='-', rad=0.0, head=11, z=1):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle='-|>', mutation_scale=head, lw=lw, color=color,
                                 linestyle=ls, connectionstyle=f'arc3,rad={rad}', shrinkA=0, shrinkB=0, zorder=z))


def save(fig, name):
    path = os.path.join(OUT, name)
    if os.environ.get('FIG_PNG'):                               # optional PNG preview for checking
        fig.savefig(os.path.join(os.environ['FIG_PNG'], name.replace('.svg', '.png')), dpi=110, facecolor='white')
    fig.savefig(path, format='svg', dpi=220, facecolor='white')
    plt.close(fig)
    import re
    with open(path, encoding='utf-8') as f:
        svg = f.read()
    svg = re.sub(r'<!DOCTYPE[^>]*>\s*', '', svg)          # plain SVG, no DTD
    with open(path, 'w', encoding='utf-8') as f:
        f.write(svg)


# ───────────────────────── synthetic image content ─────────────────────────
def fundus(n=600, seed=3, overlay=False):
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[-1:1:n * 1j, -1:1:n * 1j]
    r = np.hypot(xx, yy)
    disc = np.exp(-(((xx + 0.42) ** 2 + (yy + 0.02) ** 2) / 0.010))
    mac = np.exp(-(((xx - 0.16) ** 2 + yy ** 2) / 0.04))
    base = np.clip(1 - 0.6 * r ** 2.2, 0, 1)
    img = np.zeros((n, n, 3))
    img[..., 0] = 0.80 * base + 0.18 * disc - 0.12 * mac
    img[..., 1] = 0.38 * base + 0.48 * disc - 0.10 * mac
    img[..., 2] = 0.17 * base + 0.32 * disc - 0.04 * mac
    img += rng.normal(0, 0.010, img.shape)
    mask = np.zeros((n, n), bool)

    def branch(x, y, ang, length, width, depth):
        if depth == 0:
            return
        for _ in range(int(length * n / 2)):
            ang += rng.normal(0, 0.05)
            x += np.cos(ang) * 2 / n; y += np.sin(ang) * 2 / n
            i, j = int((y + 1) / 2 * n), int((x + 1) / 2 * n)
            if not (0 <= i < n and 0 <= j < n) or np.hypot(x, y) > 0.96:
                return
            w = max(1, int(round(width)))
            mask[max(0, i - w):i + w, max(0, j - w):j + w] = True
        for s in (-1, 1):
            branch(x, y, ang + s * rng.uniform(0.35, 0.65), length * 0.72, width * 0.7, depth - 1)

    for a in (-1.2, -0.6, 0.6, 1.2):
        branch(-0.42, -0.02, a, 0.72, 3.4 * n / 520, 5)
    img[mask] = img[mask] * 0.6 + np.array([0.32, 0.05, 0.04]) * 0.4
    if overlay:
        right = xx > 0.0
        img[right & ~mask] *= 0.5
        img[right & mask] = np.array([0.36, 0.80, 0.76])
    alpha = np.clip((0.975 - r) * 120, 0, 1)
    return np.dstack([np.clip(img, 0, 1), alpha])


def real_fundus(n=600, vessel_half=False):
    """CC0 fundus photograph (Wikimedia, Mikael Haggstrom) shipped with scikit-image.
    With vessel_half=True the right half shows a Frangi vesselness map computed from the photo."""
    from skimage import data, transform, filters, exposure
    img = transform.resize(data.retina(), (n, n), anti_aliasing=True)
    yy, xx = np.mgrid[-1:1:n * 1j, -1:1:n * 1j]
    r = np.hypot(xx, yy)
    fov = r < 0.93
    if vessel_half:
        g = exposure.equalize_adapthist(img[..., 1])
        v = filters.frangi(1 - g, sigmas=np.linspace(1, 4, 6) * n / 600, black_ridges=False)
        v = v * fov
        v = np.clip(v / np.percentile(v[fov], 99.2), 0, 1) ** 0.7
        right = xx > 0
        img[right] = np.dstack([v, v, v])[right]
    alpha = np.clip((0.985 - r) * 80, 0, 1)
    return np.dstack([np.clip(img, 0, 1), alpha])


def oct_scan(n_w=700, n_h=280, seed=5):  # noqa
    rng = np.random.default_rng(seed)
    x = np.linspace(-1, 1, n_w)
    pit = 30 * np.exp(-(x / 0.2) ** 2)
    tops = [70, 92, 104, 130, 152, 164, 178]
    vals = [0.95, 0.32, 0.72, 0.22, 0.55, 1.0, 0.42]
    img = np.full((n_h, n_w), 0.05)
    lines = []
    for k, (t, v) in enumerate(zip(tops, vals)):
        depth = pit * (1.0 if k < 4 else 0.22)
        top = t + depth + 3 * np.sin(2 * np.pi * (x * 0.55 + k * 0.15))
        lines.append(top)
        for c in range(n_w):
            img[int(top[c]):, c] = v * (1 - 0.12 * k / 7)
    img[205:, :] *= np.linspace(1, 0.2, n_h - 205)[:, None]
    img = img * rng.gamma(5.0, 0.2, img.shape)
    return np.clip(img, 0, 1), lines


def surgical_frame(seed, n=200):
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:1:int(n * 0.77) * 1j, 0:1:n * 1j]
    tissue = 0.5 + 0.5 * np.sin(6 * xx + 3 * yy + seed) * np.cos(5 * yy - 2 * xx)
    tissue = tissue + rng.normal(0, 0.05, tissue.shape)
    img = np.zeros(tissue.shape + (3,))
    img[..., 0] = 0.74 + 0.16 * tissue
    img[..., 1] = 0.38 + 0.13 * tissue
    img[..., 2] = 0.37 + 0.10 * tissue
    img *= (1 - 0.5 * ((xx - 0.5) ** 2 + (yy - 0.5) ** 2) * 2.2)[..., None]
    tool = np.abs((0.9 - yy) - 0.8 * (xx - 0.45 - 0.07 * seed)) < 0.06
    img[tool & (xx > 0.38)] = [0.72, 0.74, 0.77]
    return np.clip(img, 0, 1)


# ───────────────────────── figure 1: multimodal perception and decision ─────────────────────────
def fig_multimodal():
    from skimage import data, transform
    fig, ax, _ = canvas(lift=0)
    panel(ax, 4, 132, 'Multimodal inputs and attention')
    panel(ax, 104, 132, 'Decision with deferral')
    panel(ax, 4, 61.5, 'Language-guided object retrieval')

    tw, th = 40.0, 17.5
    cells = [(6, 104), (50, 104), (6, 78.5), (50, 78.5)]

    def frame(x_, y_, label):
        ax.add_patch(Rectangle((x_, y_), tw, th, fc='none', ec=RULE, lw=0.7, zorder=6))
        ax.text(x_, y_ - 1.2, label, fontsize=T_SMALL, color=INK, va='top')

    # image: CC0 photograph; attention shown as a spotlight on the cup
    cof = mute(data.coffee().astype(float) / 255)
    h_ = int(cof.shape[1] * th / tw)
    crop = cof[40:40 + h_]
    yy_, xx_ = np.mgrid[0:crop.shape[0], 0:crop.shape[1]]
    heat = np.exp(-(((xx_ - 0.40 * crop.shape[1]) / (0.16 * crop.shape[1])) ** 2 + ((yy_ - 0.38 * crop.shape[0]) / (0.36 * crop.shape[0])) ** 2))
    lit = crop * (0.32 + 0.68 * heat[..., None])
    ax.imshow(np.clip(lit, 0, 1), extent=(cells[0][0], cells[0][0] + tw, cells[0][1], cells[0][1] + th), zorder=2)
    ax.contour(np.linspace(cells[0][0], cells[0][0] + tw, crop.shape[1]), np.linspace(cells[0][1] + th, cells[0][1], crop.shape[0]),
               heat, levels=[0.5], colors=['white'], linewidths=1.0, zorder=3)
    frame(*cells[0], 'Image')
    # video: four consecutive frames of one scene (a slow pan); bars show per-frame attention
    rk = mute(data.rocket())
    fw = (tw - 3 * 0.8) / 4
    wts = [0.25, 0.45, 1.0, 0.6]
    bar = 1.2
    ch = 400; cw = int(round(ch * fw / (th - bar)))
    for k in range(4):
        fx = cells[1][0] + k * (fw + 0.8)
        x0_ = 150 + 40 * k
        crop_v = rk[10:10 + ch, x0_:x0_ + cw]
        ax.imshow(crop_v, extent=(fx, fx + fw, cells[1][1] + bar, cells[1][1] + th), aspect='auto', zorder=2)
        ax.add_patch(Rectangle((fx, cells[1][1]), fw, bar, fc=LIGHT, ec='none', zorder=2))
        ax.add_patch(Rectangle((fx, cells[1][1]), fw * wts[k], bar, fc=BLUE, ec='none', zorder=3))
        if wts[k] == max(wts):
            ax.add_patch(Rectangle((fx, cells[1][1]), fw, th, fc='none', ec=BLUE, lw=0.9, zorder=7))
    ax.add_patch(Rectangle((cells[1][0], cells[1][1]), tw, th, fc='none', ec=RULE, lw=0.7, zorder=6))
    ax.text(cells[1][0], cells[1][1] - 1.2, 'Video', fontsize=T_SMALL, color=INK, va='top')
    # audio: spectrogram; the attended segment stays bright
    sr = 8000; t = np.arange(0, 1.6, 1 / sr)
    f0 = 140 + 40 * np.sin(2 * np.pi * 1.1 * t)
    phase = 2 * np.pi * np.cumsum(f0) / sr
    sig = sum(np.sin(h * phase) / h for h in range(1, 14)) * (0.55 + 0.45 * np.sin(2 * np.pi * 2.2 * t) ** 2)
    sig = sig * (0.25 + 0.75 * (np.sin(2 * np.pi * 0.8 * t + 0.6) > -0.8))
    win, hop = 256, 40
    frames_ = np.stack([sig[i_:i_ + win] * np.hanning(win) for i_ in range(0, len(sig) - win, hop)], 1)
    spec = 20 * np.log10(np.abs(np.fft.rfft(frames_, axis=0))[:90] + 1e-3)
    spec = np.clip((spec - spec.max() + 60) / 60, 0, 1)
    rgb = LinearSegmentedColormap.from_list('m', ['#f4f2ee', '#a39e94', '#3a3631', '#1b1a17'])(spec)[..., :3]
    tt = np.linspace(0, 1, spec.shape[1])
    on = (tt > 0.55) & (tt < 0.8)
    rgb[:, ~on] = rgb[:, ~on] * 0.35 + 0.65 * np.array([0.955, 0.95, 0.93])
    ax.imshow(rgb, origin='lower', aspect='auto', extent=(cells[2][0], cells[2][0] + tw, cells[2][1], cells[2][1] + th), zorder=2)
    ax.add_patch(Rectangle((cells[2][0] + 0.55 * tw, cells[2][1]), 0.25 * tw, th, fc='none', ec='white', lw=1.0, zorder=4))
    frame(*cells[2], 'Audio')
    # text: the query, with attended words highlighted
    x_, y_ = cells[3]
    ax.add_patch(Rectangle((x_, y_), tw, th, fc='white', ec='none', zorder=1))
    r_ = fig.canvas.get_renderer()
    inv = ax.transData.inverted()

    def words(line, y_line, hi):
        cx = x_ + 2.4
        for w_ in line.split(' '):
            tx = ax.text(cx, y_line, w_, fontsize=T_LABEL, color=INK, va='baseline', style='italic', zorder=4)
            bb = tx.get_window_extent(renderer=r_)
            (bx0, by0), (bx1, by1) = inv.transform([[bb.x0, bb.y0], [bb.x1, bb.y1]])
            if w_.strip('?') in hi:
                ax.add_patch(FancyBboxPatch((bx0 - 0.4, by0 - 0.4), bx1 - bx0 + 0.8, by1 - by0 + 0.6,
                                            boxstyle='round,pad=0,rounding_size=0.8', fc=BLUE_L, ec='none', zorder=3))
            sp = ax.text(0, 0, 'a a', fontsize=T_LABEL, style='italic'); sb = sp.get_window_extent(renderer=r_)
            sa = ax.text(0, 0, 'aa', fontsize=T_LABEL, style='italic'); sab = sa.get_window_extent(renderer=r_)
            space = inv.transform([[sb.x1 - sab.x1 + sab.x0, 0]])[0][0] - inv.transform([[sb.x0, 0]])[0][0]
            sp.remove(); sa.remove()
            cx = bx1 + space
    words('Is the cup inside', y_ + th - 6.4, {'cup'})
    words('the blue bowl?', y_ + th - 12.6, {'blue', 'bowl'})
    frame(x_, y_, 'Text')

    # ── decision map: refer, routine, or defer by predicted risk and uncertainty (clinical example)
    x0, x1, y0, y1 = 112, 155, 80, 122
    thr_r, thr_u = 0.5, 0.55
    Xr = lambda v: x0 + (x1 - x0) * v
    Yu = lambda v: y0 + (y1 - y0) * v
    ax.add_patch(Rectangle((x0, y0), Xr(thr_r) - x0, Yu(thr_u) - y0, fc=LIGHT, ec='none'))
    ax.add_patch(Rectangle((Xr(thr_r), y0), x1 - Xr(thr_r), Yu(thr_u) - y0, fc=BLUE_L, ec='none'))
    ax.add_patch(Rectangle((x0, Yu(thr_u)), x1 - x0, y1 - Yu(thr_u), fc=AMBER_L, ec='none'))
    ax.plot([x0, x0, x1], [y1, y0, y0], color=INK, lw=1.0)
    ax.text((x0 + x1) / 2, Yu(0.87), 'Defer to clinician', fontsize=T_SMALL, color=AMBER_D, ha='center', va='center')
    ax.text(Xr(0.25), Yu(0.11), 'Routine', fontsize=T_SMALL, color=GREY, ha='center', va='center')
    ax.text(Xr(0.75), Yu(0.11), 'Refer', fontsize=T_SMALL, color=BLUE, ha='center', va='center')
    pts = np.array([[0.12, 0.30], [0.22, 0.42], [0.30, 0.25], [0.38, 0.47], [0.68, 0.36], [0.78, 0.24], [0.86, 0.42],
                    [0.93, 0.30], [0.44, 0.64], [0.57, 0.70], [0.32, 0.69], [0.68, 0.63]])
    for (r_, u_) in pts:
        col = AMBER if u_ >= thr_u else (BLUE if r_ >= thr_r else MID)
        ax.plot([Xr(r_)], [Yu(u_)], 'o', ms=4.6, mfc=col, mec='white', mew=0.8, zorder=4)
    ax.text((x0 + x1) / 2, y0 - 2.0, 'Predicted risk', fontsize=T_SMALL, color=GREY, ha='center', va='top')
    ax.text(x0 - 2.0, (y0 + y1) / 2, 'Uncertainty', fontsize=T_SMALL, color=GREY, ha='right', va='center', rotation=90)
    ax.text((x0 + x1) / 2, y0 - 7.4, 'clinical example', fontsize=T_SMALL - 2.5, color=GREY, ha='center', va='top', style='italic')

    # ── language-guided object retrieval: real-robot sequence (Koh et al., ICRA submission, Fig. 1)
    ax.text(4, 54.5, '“Pick up the target inside the covered container.”', fontsize=T_SMALL, color=INK,
            style='italic', va='center')
    steps = (('Observe', 'target occluded'), ('Remove cover', 'container exposed'),
             ('Re-observe', 'new visual evidence'), ('Grasp target', 'target lifted'))
    gap = 2.4
    pw = (156 - 4 - 3 * gap) / 4
    ph = pw * 178 / 243
    py0 = 22.0
    for k, (lab_, sub_) in enumerate(steps):
        x_ = 4 + k * (pw + gap)
        photo = mute(plt.imread(os.path.join(os.path.dirname(__file__), 'sources', f'retrieval-{k + 1}.png')), keep=0.55)
        ax.imshow(photo, extent=(x_, x_ + pw, py0, py0 + ph), zorder=2, interpolation='antialiased')
        ax.add_patch(Rectangle((x_, py0), pw, ph, fc='none', ec=RULE, lw=0.6, zorder=3))
        ax.text(x_ + pw / 2, py0 - 1.4, f"{('I', 'II', 'III', 'IV')[k]}. {lab_}", fontsize=T_SMALL, color=INK, ha='center', va='top', fontweight=600)
        ax.text(x_ + pw / 2, py0 - 7.0, sub_, fontsize=T_SMALL - 1.5, color=GREY, ha='center', va='top')
        if k < 3:
            arrow(ax, (x_ + pw + 0.25, py0 + ph / 2), (x_ + pw + gap - 0.25, py0 + ph / 2), color=MID, head=8, lw=1.0, z=5)
    save(fig, 'overview-multimodal.svg')


# ───────────────────────── figure 2: medical image and video ─────────────────────────
def fig_medical():
    fig, axb, ax = canvas()
    panel(ax, 4, 123, 'Retinal grading')
    panel(ax, 58, 123, 'Retinal layers')
    panel(ax, 110, 123, 'Brain connectivity')
    panel(axb, 4, 57, 'Human pose from video')
    panel(axb, 86, 57, 'Endoscope motion')
    # fundus photograph and the five-level diabetic retinopathy severity scale it is graded on (no grade is claimed)
    ax.imshow(real_fundus(600), extent=(10.5, 44.5, 79, 113), zorder=2)
    arrow(ax, (27.5, 78.0), (27.5, 74.6), head=8, lw=1.0)
    sx0, sx1, sy = 3.5, 51.5, 70.4
    shades = ['#efebe6', '#dcd0c9', '#b89a94', '#8d4d55', BLUE]
    names = ['None', 'Mild', 'Mod.', 'Severe', 'PDR']
    sw_ = (sx1 - sx0) / 5
    for k, (c, nm) in enumerate(zip(shades, names)):
        ax.add_patch(Rectangle((sx0 + k * sw_ + 0.2, sy), sw_ - 0.4, 3.0, fc=c, ec='none', zorder=2))
        ax.text(sx0 + (k + 0.5) * sw_, sy - 1.0, nm, fontsize=T_SMALL - 3.5, color=GREY, ha='center', va='top')
    # retinal layers in OCT: right half shows the predicted layers as colored bands
    img, lines = oct_scan()
    img = img[::2, ::2]; lines = [l[::2] / 2 for l in lines]
    ox0, ox1, oy0, oy1 = 58, 100, 76, 108
    ax.imshow(img, cmap='gray', extent=(ox0, ox1, oy0, oy1), aspect='auto', zorder=2, vmin=0, vmax=1)
    xs = np.linspace(ox0, ox1, img.shape[1])
    Yo = lambda ln: oy1 - ln / img.shape[0] * (oy1 - oy0)
    half = xs >= 79
    band_cols = ['#3a3631', '#8c6d46', '#a39e94', '#6b1f2a', '#5b5750']
    for k in range(5):
        top, bot = Yo(lines[k]), Yo(lines[k + 1])
        ax.fill_between(xs[half], bot[half], top[half], color=band_cols[k], alpha=0.55, lw=0, zorder=3)
    for k in range(6):
        ax.plot(xs[half], Yo(lines[k])[half], color='white', lw=0.7, zorder=4)
    ax.plot([79, 79], [oy0 + 0.5, oy1 - 0.5], color='white', lw=1.0, ls=(0, (2.5, 2)), zorder=5)
    ax.text(68.5, 68.5, 'OCT', fontsize=T_SMALL, color=GREY, ha='center', va='top')
    ax.text(89.5, 68.5, 'Layers', fontsize=T_SMALL, color=GREY, ha='center', va='top')
    # brain connectivity: MNI152 template slice with network regions, and the region-by-region matrix
    import json
    src = os.path.join(os.path.dirname(__file__), 'sources')
    mni = plt.imread(os.path.join(src, 'mni152-axial.png'))
    info = json.load(open(os.path.join(src, 'mni152-rois.json')))
    H_, W_ = info['shape']
    bh = 37.0; bw_ = bh * W_ / H_
    bx0, by0 = 106.0, 73.5
    g_ = mni if mni.ndim == 2 else mni[..., 0]
    rgba = np.dstack([g_, g_, g_, np.clip((g_ - 0.04) * 12, 0, 1) * 0.55])   # template drawn faintly under the graph
    ax.imshow(rgba, extent=(bx0, bx0 + bw_, by0, by0 + bh), zorder=1)
    net_col = {'DefaultMode': BLUE, 'Visual': AMBER, 'Auditory': TEAL, 'FrontoParietal': INK}
    order = ['DefaultMode', 'FrontoParietal', 'Auditory', 'Visual', 'Other']
    rois = info['rois']
    P_ = np.array([(bx0 + (r['i'] + 0.5) / W_ * bw_, by0 + (r['j'] + 0.5) / H_ * bh) for r in rois])
    nets = [r['net'] if r['net'] in net_col else 'Other' for r in rois]
    rng = np.random.default_rng(11)
    n = len(rois)
    # edges (illustrative): each region links to its nearest regions in the same network, plus a few links across networks
    edges = set()
    for a_ in range(n):
        same = [b_ for b_ in range(n) if b_ != a_ and nets[b_] == nets[a_]]
        same.sort(key=lambda b_: np.hypot(*(P_[a_] - P_[b_])))
        for b_ in same[:2]:
            edges.add((min(a_, b_), max(a_, b_)))
    for a_, b_ in edges:
        ax.plot(*zip(P_[a_], P_[b_]), color=net_col.get(nets[a_], MID), lw=1.0, alpha=0.8, zorder=2)
    cross = [(a_, b_) for a_ in range(n) for b_ in range(a_ + 1, n) if nets[a_] != nets[b_] and np.hypot(*(P_[a_] - P_[b_])) < 9]
    for k_ in rng.choice(len(cross), size=min(5, len(cross)), replace=False):
        a_, b_ = cross[k_]
        ax.plot(*zip(P_[a_], P_[b_]), color=MID, lw=0.7, ls=(0, (2, 1.5)), zorder=2)
    for (px_, py_), nt in zip(P_, nets):
        ax.plot([px_], [py_], 'o', ms=3.8, mfc=net_col.get(nt, MID), mec='white', mew=0.6, zorder=4)
    # the same graph as a region-by-region matrix, drawn small
    lab = np.array(sorted(range(n), key=lambda q: order.index(nets[q])))
    g = np.array([order.index(nets[q]) for q in lab])
    C = np.where(g[:, None] == g[None, :], 0.6, 0.05) + rng.normal(0, 0.14, (n, n))
    C = (C + C.T) / 2; np.fill_diagonal(C, 1)
    div = LinearSegmentedColormap.from_list('d', [AMBER, '#ece3d6', '#ffffff', '#e2cfcc', BLUE])
    # place the matrix level with the centre of the visible brain and start the arrow at the brain's right edge
    vis = np.where((g_ > 0.06).any(axis=0))[0]
    rows_ = np.where((g_ > 0.06).any(axis=1))[0]
    brain_r = bx0 + (vis.max() + 1) / g_.shape[1] * bw_
    brain_cy = by0 + bh - (rows_.min() + rows_.max() + 1) / 2 / g_.shape[0] * bh
    ms_ = 12.5
    mx0, my0 = brain_r + 7.0, brain_cy - ms_ / 2
    ax.imshow(np.clip(C, -1, 1), cmap=div, vmin=-1, vmax=1, extent=(mx0, mx0 + ms_, my0, my0 + ms_), interpolation='nearest', zorder=2)
    ax.add_patch(Rectangle((mx0, my0), ms_, ms_, fc='none', ec=INK, lw=0.6, zorder=3))
    arrow(ax, (brain_r + 1.2, brain_cy), (mx0 - 1.0, brain_cy), head=8, lw=1.0)
    ax.text(bx0 + bw_ / 2, 68.5, 'Region graph', fontsize=T_SMALL - 1.5, color=GREY, ha='center', va='top')
    ax.text(mx0 + ms_ / 2, 68.5, 'Matrix', fontsize=T_SMALL - 1.5, color=GREY, ha='center', va='top')

    ax = axb
    # human pose: keypoint skeletons across video frames (left)
    def skeleton(phase):
        sw = np.sin(phase)
        hip = np.array([0.0, 0.0]); neck = np.array([0.4, 6.2]); head = neck + [0.5, 2.0]
        sh_l, sh_r = neck + [-1.0, -0.3], neck + [1.0, -0.3]
        hp_l, hp_r = hip + [-0.8, 0], hip + [0.8, 0]
        el_l, el_r = sh_l + [-1.2 * sw, -2.6], sh_r + [1.2 * sw, -2.6]
        wr_l, wr_r = el_l + [-0.6 * sw + 0.6, -2.2], el_r + [0.6 * sw + 0.6, -2.2]
        kn_l, kn_r = hp_l + [1.6 * sw, -3.4], hp_r + [-1.6 * sw, -3.4]
        an_l, an_r = kn_l + [0.6 * sw - 0.3, -3.6], kn_r + [-0.6 * sw - 0.3, -3.6]
        return dict(head=head, neck=neck, sh_l=sh_l, sh_r=sh_r, el_l=el_l, el_r=el_r, wr_l=wr_l, wr_r=wr_r,
                    hip=hip, hp_l=hp_l, hp_r=hp_r, kn_l=kn_l, kn_r=kn_r, an_l=an_l, an_r=an_r)
    bones = [('head', 'neck', INK), ('neck', 'hip', INK), ('neck', 'sh_l', AMBER), ('sh_l', 'el_l', AMBER), ('el_l', 'wr_l', AMBER),
             ('neck', 'sh_r', BLUE), ('sh_r', 'el_r', BLUE), ('el_r', 'wr_r', BLUE), ('hip', 'hp_l', AMBER), ('hp_l', 'kn_l', AMBER),
             ('kn_l', 'an_l', AMBER), ('hip', 'hp_r', BLUE), ('hp_r', 'kn_r', BLUE), ('kn_r', 'an_r', BLUE)]
    for k, ph in enumerate(np.linspace(-1.0, 1.0, 4)):
        fx = 8 + k * 17.5
        ax.add_patch(Rectangle((fx, 14), 15, 31, fc=LIGHT, ec=RULE, lw=0.8, zorder=1))
        P = {kk: vv * 1.35 for kk, vv in skeleton(ph).items()}
        off = np.array([fx + 7.0, 28.0])
        for a_, b_, c_ in bones:
            p1, p2 = P[a_] + off, P[b_] + off
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=c_, lw=1.6, solid_capstyle='round', zorder=3)
        for v in P.values():
            ax.plot(*(v + off), 'o', ms=3.2, mfc='white', mec=INK, mew=0.9, zorder=4)
        ax.text(fx + 7.5, 11, f't{k + 1}', fontsize=T_SMALL - 1, color=GREY, ha='center', va='top')

    # endoscope trajectory (right)
    t = np.linspace(0, 1, 300)
    px = 90 + 62 * t
    py = 30 + 8 * np.sin(2 * np.pi * t * 1.1) + 3 * t
    ax.plot(px, py - 1.4 + 1.6 * np.sin(8 * t + 0.4), color=MID, lw=1.3, ls=(0, (3.5, 2.5)))
    ax.plot(px, py, color=BLUE, lw=2.0)
    for k in np.linspace(12, 288, 5).astype(int):
        cx, cy = px[k], py[k]
        a = np.arctan2(py[min(k + 4, 299)] - py[k - 4], px[min(k + 4, 299)] - px[k - 4])
        R = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
        tri = np.array([[0, 0], [5, 2.6], [5, -2.6]]) @ R.T + [cx, cy]
        ax.add_patch(Polygon(tri, closed=True, fc='white', ec=BLUE, lw=1.2, zorder=4))
    ax.plot([90, 97], [11, 11], color=BLUE, lw=2.0); ax.text(98.5, 11, 'Estimated', fontsize=T_SMALL, color=INK, va='center')
    ax.plot([122, 129], [11, 11], color=MID, lw=1.3, ls=(0, (3.5, 2.5))); ax.text(130.5, 11, 'Reference', fontsize=T_SMALL, color=INK, va='center')
    save(fig, 'overview-medical.svg')


# ───────────────────────── figure 3: reliable and efficient AI ─────────────────────────
def fig_reliable():
    fig, axb, ax = canvas()
    panel(ax, 4, 123, 'Distribution shift')
    panel(axb, 4, 59, 'Test-time adaptation')
    panel(axb, 86, 59, 'Compact models for real time')
    x = np.linspace(-4, 7, 400)
    X = lambda v: 14 + (v + 4) / 11 * 138
    Y = lambda v: 76 + v * 30
    s_ = np.exp(-(x / 1.0) ** 2 / 2); tg = 0.82 * np.exp(-((x - 2.7) / 1.35) ** 2 / 2)
    ax.fill_between(X(x), Y(0), Y(s_), color=BLUE_L, lw=0); ax.plot(X(x), Y(s_), color=BLUE, lw=1.8)
    ax.fill_between(X(x), Y(0), Y(tg), color=AMBER_L, lw=0, alpha=0.85); ax.plot(X(x), Y(tg), color=AMBER, lw=1.8)
    ax.plot([X(-4), X(7)], [76, 76], color=INK, lw=1.0)
    arrow(ax, (X(-0.1), Y(1.17)), (X(2.7), Y(1.17)), color=GREY, head=10)
    ax.text(X(1.3), Y(1.21), 'shift', fontsize=T_SMALL, color=GREY, ha='center', va='bottom')
    ax.text(X(-1.85), Y(0.6), 'Training\ndata', fontsize=T_SMALL, color=BLUE, ha='center', linespacing=1.15)
    ax.text(X(5.25), Y(0.55), 'Deployment\ndata', fontsize=T_SMALL, color=AMBER_D, ha='center', linespacing=1.15)
    ax.text(X(1.5), 73, 'Pixel intensity', fontsize=T_SMALL, color=GREY, ha='center', va='top')

    ax = axb
    # test-time adaptation (conceptual): unlabeled deployment frames update the model before it predicts
    # one outdoor scene (public-domain photo shipped with scikit-image) under three weather conditions
    from skimage import data as skdata, transform as sktf
    scene = mute(sktf.resize(skdata.rocket().astype(float)[40:427, 0:640] / 255, (156, 204), anti_aliasing=True))
    rng_w = np.random.default_rng(3)
    def fog(im):
        return im * 0.45 + 0.55 * np.array([0.84, 0.85, 0.87])
    def rain(im):
        im = im * 0.62 + 0.38 * np.array([0.55, 0.58, 0.62])
        out = im.copy(); h, w = im.shape[:2]
        for _ in range(170):
            y, x = rng_w.integers(0, h - 9), rng_w.integers(0, w - 4)
            for t_ in range(8):
                out[y + t_, min(w - 1, x + t_ // 3)] = out[y + t_, min(w - 1, x + t_ // 3)] * 0.4 + 0.6
        return out
    looks = [('Clear', scene), ('Fog', fog(scene)), ('Rain', rain(scene))]
    fw_, fh_, gap_ = 10.4, 8.0, 0.9
    for k, (nm, img) in enumerate(looks):
        fx = 4.5 + k * (fw_ + gap_)
        ax.imshow(np.clip(img, 0, 1), extent=(fx, fx + fw_, 28.0, 28.0 + fh_), zorder=2, aspect='auto')
        ax.add_patch(Rectangle((fx, 28.0), fw_, fh_, fc='none', ec=RULE, lw=0.6, zorder=3))
        ax.text(fx + fw_ / 2, 26.8, nm, fontsize=T_SMALL - 2.5, color=GREY, ha='center', va='top')
    ax.text(4.5 + 1.5 * fw_ + gap_, 19.6, 'Unlabeled test data', fontsize=T_SMALL - 1, color=GREY, ha='center', va='top')
    arrow(ax, (37.6, 32.0), (40.6, 32.0), head=8, lw=1.1)
    ax.add_patch(FancyBboxPatch((41, 26), 17, 12, boxstyle='round,pad=0,rounding_size=1.4', fc=BLUE_L, ec=BLUE, lw=1.1))
    ax.text(49.5, 32, 'Model', fontsize=T_SMALL, color=BLUE, ha='center', va='center')
    ax.add_patch(FancyArrowPatch((54.5, 38.6), (44.5, 38.6), connectionstyle='arc3,rad=1.25', arrowstyle='-|>',
                                 mutation_scale=9, lw=1.1, color=BLUE))
    ax.text(49.5, 47.2, 'adapt', fontsize=T_SMALL, color=BLUE, ha='center', va='bottom')
    arrow(ax, (58.6, 32.0), (66.0, 32.0), head=9, lw=1.1)
    ax.text(67.0, 32.0, 'Predict', fontsize=T_SMALL, color=INK, ha='left', va='center')
    ax.text(49.5, 22.6, 'no labels', fontsize=T_SMALL - 1, color=GREY, ha='center', va='top', style='italic')

    # compact models under a real-time budget (conceptual; no measured values). The student replaces the
    # teacher's multi-head self-attention with a single head and learns from the teacher (Lightweight TransUNet).
    ay, ax0, ax1 = 21.5, 90.0, 154.0
    arrow(ax, (ax0, ay), (ax1, ay), color=INK, lw=1.0, head=9)
    ax.text((ax0 + ax1) / 2, ay - 2.2, 'Inference cost per frame', fontsize=T_SMALL - 1, color=GREY, ha='center', va='top')
    bxl = 121.0
    ax.plot([bxl, bxl], [ay - 1.2, 49.0], color=TEAL, lw=1.2, ls=(0, (3, 2)))
    ax.text(bxl, 50.0, 'real-time budget', fontsize=T_SMALL - 1.5, color=TEAL, ha='center', va='bottom')
    amap = LinearSegmentedColormap.from_list('a', ['#ffffff', BLUE_L, BLUE])
    rng_a = np.random.default_rng(7)
    def attn(cx, cy, size, seed):
        r = np.random.default_rng(seed)
        q = np.linspace(0, 1, 8)
        A = np.exp(-((q[:, None] - q[None, :] - r.uniform(-0.3, 0.3)) / r.uniform(0.12, 0.3)) ** 2) + 0.15 * r.random((8, 8))
        ax.imshow(A / A.max(), cmap=amap, vmin=0, vmax=1, extent=(cx - size / 2, cx + size / 2, cy - size / 2, cy + size / 2),
                  interpolation='nearest', zorder=3)
        ax.add_patch(Rectangle((cx - size / 2, cy - size / 2), size, size, fc='none', ec=INK, lw=0.6, zorder=4))
    tcx, tcy, sz = 140.0, 36.5, 6.2
    for k, (dx, dy) in enumerate(((-1, 1), (1, 1), (-1, -1), (1, -1))):
        attn(tcx + dx * (sz / 2 + 0.5), tcy + dy * (sz / 2 + 0.5), sz, k + 1)
    scx = 103.0
    attn(scx, tcy, 8.0, 9)
    ax.text(tcx, 44.6, 'Teacher', fontsize=T_SMALL, color=INK, ha='center', va='bottom')
    ax.text(scx, 44.6, 'Student', fontsize=T_SMALL, color=BLUE, ha='center', va='bottom')
    ax.text(tcx, 28.9, 'multi-head attention', fontsize=T_SMALL - 2.5, color=GREY, ha='center', va='top')
    ax.text(scx, 28.9, 'single-head attention', fontsize=T_SMALL - 2.5, color=GREY, ha='center', va='top')
    arrow(ax, (tcx - 8.2, tcy), (scx + 5.0, tcy), color=GREY, ls=(0, (3, 2)), head=9)
    ax.text(113.0, tcy + 1.2, 'distill', fontsize=T_SMALL - 1, color=GREY, ha='center', va='bottom')
    save(fig, 'overview-reliable.svg')


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    fig_multimodal(); fig_medical(); fig_reliable()
    print('saved to', OUT)
