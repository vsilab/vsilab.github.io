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

# palette: neutral greys plus two restrained hues
INK, GREY, MID, LIGHT, RULE = '#1f2328', '#6b7280', '#9aa1ab', '#f1f2f4', '#d5d9de'
BLUE, BLUE_L = '#2b5c8a', '#dce7f1'
AMBER, AMBER_L, AMBER_D = '#c97c2b', '#f6e7d4', '#9a5a16'
TEAL, RED = '#3f8a83', '#a8423a'
T_LABEL, T_SMALL, T_TITLE = 17.5, 16, 18.5

W, H = 8.0, 7.0          # inches; drawing units are 160 x 140


def canvas(lift=10):
    """Returns (fig, bottom_axes, top_axes). Both span the figure in 160 x 140 units; the top-row axes are
    shifted up by `lift`, which sets the gap between the two rows without touching either row's layout."""
    fig = plt.figure(figsize=(W, H))
    axb = fig.add_axes([0, 0, 1, 1])
    axb.set_xlim(0, 160); axb.set_ylim(0, 140); axb.axis('off')
    axt = fig.add_axes([0, 0, 1, 1])
    axt.set_xlim(0, 160); axt.set_ylim(-lift, 140 - lift); axt.axis('off'); axt.patch.set_alpha(0)
    return fig, axb, axt


def panel(ax, x, y, title):
    ax.text(x, y, title, fontsize=T_TITLE, fontweight=600, color=INK, va='baseline')


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
    panel(ax, 4, 132, 'Multimodal inputs')
    panel(ax, 104, 132, 'Imaging with patient data')
    panel(ax, 4, 61.5, 'Robot retrieval under occlusion')

    tw, th = 40.0, 17.5
    cells = [(6, 104), (50, 104), (6, 78.5), (50, 78.5)]

    def frame(x_, y_, label):
        ax.add_patch(Rectangle((x_, y_), tw, th, fc='none', ec=RULE, lw=0.7, zorder=6))
        ax.text(x_, y_ - 1.2, label, fontsize=T_SMALL, color=INK, va='top')

    # image: CC0 photograph
    cof = data.coffee().astype(float) / 255
    h_ = int(cof.shape[1] * th / tw)
    ax.imshow(cof[40:40 + h_], extent=(cells[0][0], cells[0][0] + tw, cells[0][1], cells[0][1] + th), zorder=2)
    frame(*cells[0], 'Image')
    # video: four consecutive frames of one scene (a slow pan)
    rk = data.rocket()
    fw = (tw - 3 * 0.8) / 4
    ch = 400; cw = int(round(ch * fw / th))
    for k in range(4):
        fx = cells[1][0] + k * (fw + 0.8)
        x0_ = 150 + 40 * k
        ax.imshow(rk[10:10 + ch, x0_:x0_ + cw], extent=(fx, fx + fw, cells[1][1], cells[1][1] + th), aspect='auto', zorder=2)
    ax.add_patch(Rectangle((cells[1][0], cells[1][1]), tw, th, fc='none', ec=RULE, lw=0.7, zorder=6))
    ax.text(cells[1][0], cells[1][1] - 1.2, 'Video', fontsize=T_SMALL, color=INK, va='top')
    # text: a language query
    x_, y_ = cells[2]
    ax.add_patch(Rectangle((x_, y_), tw, th, fc='white', ec='none', zorder=1))
    ax.text(x_ + 2.4, y_ + th - 6.4, 'Which container', fontsize=T_LABEL, color=INK, va='baseline', style='italic', zorder=4)
    ax.text(x_ + 2.4, y_ + th - 12.6, 'holds the target?', fontsize=T_LABEL, color=INK, va='baseline', style='italic', zorder=4)
    frame(x_, y_, 'Text')
    # patient data: a small table of clinical variables
    x_, y_ = cells[3]
    ax.add_patch(Rectangle((x_, y_), tw, th, fc='white', ec='none', zorder=1))
    rows = 4
    for r_ in range(rows + 1):
        yy = y_ + th - 1.6 - r_ * (th - 3.2) / rows
        ax.plot([x_ + 2, x_ + tw - 2], [yy, yy], color=RULE if r_ else MID, lw=0.7, zorder=3)
    for c_ in (0.36, 0.68):
        ax.plot([x_ + tw * c_] * 2, [y_ + 1.6, y_ + th - 1.6], color=RULE, lw=0.7, zorder=3)
    rng_ = np.random.default_rng(4)
    for r_ in range(rows):
        yy = y_ + th - 1.6 - (r_ + 0.5) * (th - 3.2) / rows
        for c0, c1 in ((0.07, 0.30), (0.42, 0.62), (0.74, 0.93)):
            L = rng_.uniform(0.5, 1.0) * (c1 - c0) * tw
            ax.plot([x_ + c0 * tw, x_ + c0 * tw + L], [yy, yy], color=MID, lw=2.2, solid_capstyle='round', zorder=4)
    frame(x_, y_, 'Patient data')

    # ── imaging with patient data: two sources combined into one prediction (conceptual)
    bx, bw = 108.0, 17.0
    ax.add_patch(Rectangle((bx, 104), bw, 17.5, fc=LIGHT, ec=RULE, lw=0.7))
    mni_ = plt.imread(os.path.join(os.path.dirname(__file__), 'sources', 'mni152-axial.png'))
    mni_ = mni_ if mni_.ndim == 2 else mni_[..., 0]
    ax.imshow(mni_, cmap='gray', extent=(bx + 1.5, bx + bw - 1.5, 105.5, 119.5), zorder=2, aspect='auto')
    ax.text(bx + bw / 2, 102.8, 'Images', fontsize=T_SMALL, color=INK, ha='center', va='top')
    ax.add_patch(Rectangle((bx, 78.5), bw, 17.5, fc='white', ec=RULE, lw=0.7))
    for r_ in range(4):
        yy = 92.6 - r_ * 3.6
        ax.plot([bx + 2, bx + 2 + rng_.uniform(6, 12)], [yy, yy], color=MID, lw=2.2, solid_capstyle='round')
    ax.text(bx + bw / 2, 77.3, 'Clinical data', fontsize=T_SMALL, color=INK, ha='center', va='top')
    fx_, fy_ = 136.0, 100.0
    arrow(ax, (bx + bw + 0.6, 112.75), (fx_ - 2.6, fy_ + 1.6), head=8, lw=1.0)
    arrow(ax, (bx + bw + 0.6, 87.25), (fx_ - 2.6, fy_ - 1.6), head=8, lw=1.0)
    ax.add_patch(FancyBboxPatch((fx_ - 2.2, fy_ - 4), 18.4, 8, boxstyle='round,pad=0,rounding_size=1.2', fc=BLUE_L, ec=BLUE, lw=1.0))
    ax.text(fx_ + 7, fy_, 'Model', fontsize=T_SMALL, color=BLUE, ha='center', va='center')
    arrow(ax, (fx_ + 7, fy_ - 4.4), (fx_ + 7, 87.0), head=8, lw=1.0)
    ax.text(fx_ + 7, 85.6, 'Detection or', fontsize=T_SMALL, color=INK, ha='center', va='top')
    ax.text(fx_ + 7, 80.2, 'outcome', fontsize=T_SMALL, color=INK, ha='center', va='top')

    # ── robot retrieval under occlusion: real-robot sequence (Koh et al., under review, Fig. 1)
    ax.text(4, 54.5, '“Pick up the target inside the covered container.”', fontsize=T_SMALL, color=INK,
            style='italic', va='center')
    steps = (('Observe', 'target not visible'), ('Remove cover', 'act to gain a view'),
             ('Re-observe', 'view into container'), ('Grasp', 'evidence suffices'))
    gap = 2.4
    pw = (156 - 4 - 3 * gap) / 4
    ph = pw * 178 / 243
    py0 = 22.0
    for k, (lab_, sub_) in enumerate(steps):
        x_ = 4 + k * (pw + gap)
        photo = plt.imread(os.path.join(os.path.dirname(__file__), 'sources', f'retrieval-{k + 1}.png'))
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
    # fundus photograph and the five-level diabetic retinopathy scale it is graded on (no grade is claimed)
    ax.imshow(real_fundus(600), extent=(10, 45, 76, 111), zorder=2)
    sx0, sx1, sy = 6.0, 49.0, 70.5
    steps_ = ['#eef1f4', '#d6e1ec', '#aec4da', '#6f93b8', BLUE]
    sw_ = (sx1 - sx0) / 5
    for k, c in enumerate(steps_):
        ax.add_patch(Rectangle((sx0 + k * sw_ + 0.2, sy), sw_ - 0.4, 2.2, fc=c, ec='none', zorder=2))
    ax.text(sx0, sy - 1.2, 'None', fontsize=T_SMALL - 1.5, color=GREY, ha='left', va='top')
    ax.text(sx1, sy - 1.2, 'Proliferative', fontsize=T_SMALL - 1.5, color=GREY, ha='right', va='top')
    # retinal layers in OCT: right half shows the predicted layers as colored bands
    img, lines = oct_scan()
    img = img[::2, ::2]; lines = [l[::2] / 2 for l in lines]
    ox0, ox1, oy0, oy1 = 58, 100, 76, 108
    ax.imshow(img, cmap='gray', extent=(ox0, ox1, oy0, oy1), aspect='auto', zorder=2, vmin=0, vmax=1)
    xs = np.linspace(ox0, ox1, img.shape[1])
    Yo = lambda ln: oy1 - ln / img.shape[0] * (oy1 - oy0)
    half = xs >= 79
    band_cols = ['#4aa39b', '#3b6fa0', '#d9a25a', '#8f6bb0', '#c4574d']
    for k in range(5):
        top, bot = Yo(lines[k]), Yo(lines[k + 1])
        ax.fill_between(xs[half], bot[half], top[half], color=band_cols[k], alpha=0.62, lw=0, zorder=3)
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
    bh = 34.0; bw_ = bh * W_ / H_
    bx0, by0 = 107.0, 75.5
    g_ = mni if mni.ndim == 2 else mni[..., 0]
    rgba = np.dstack([g_, g_, g_, np.clip((g_ - 0.04) * 12, 0, 1)])     # transparent outside the head
    ax.imshow(rgba, extent=(bx0, bx0 + bw_, by0, by0 + bh), zorder=2)
    net_col = {'DefaultMode': BLUE, 'Visual': AMBER, 'Auditory': TEAL, 'FrontoParietal': '#7a5c99'}
    order = ['DefaultMode', 'FrontoParietal', 'Auditory', 'Visual', 'Other']
    rois = info['rois']
    for r in rois:
        c = net_col.get(r['net'], '#c4574d')
        px_ = bx0 + (r['i'] + 0.5) / W_ * bw_; py_ = by0 + (r['j'] + 0.5) / H_ * bh
        ax.plot([px_], [py_], 'o', ms=3.4, mfc=c, mec='white', mew=0.6, zorder=4)
    groups = [r['net'] if r['net'] in net_col else 'Other' for r in rois]
    lab = np.array(sorted(range(len(groups)), key=lambda q: order.index(groups[q])))
    g = np.array([order.index(groups[q]) for q in lab])
    rng = np.random.default_rng(11)
    n = len(g)
    C = np.where(g[:, None] == g[None, :], 0.6, 0.05) + rng.normal(0, 0.14, (n, n))
    C[np.ix_(g == 0, g == 1)] -= 0.3; C[np.ix_(g == 1, g == 0)] -= 0.3
    C = (C + C.T) / 2; np.fill_diagonal(C, 1)
    div = LinearSegmentedColormap.from_list('d', [AMBER, '#f3d9b8', '#ffffff', '#b9cfe3', BLUE])
    mx0, my0, ms_ = 139.5, 83.0, 17.0
    ax.imshow(np.clip(C, -1, 1), cmap=div, vmin=-1, vmax=1, extent=(mx0, mx0 + ms_, my0, my0 + ms_), interpolation='nearest', zorder=2)
    ax.add_patch(Rectangle((mx0, my0), ms_, ms_, fc='none', ec=INK, lw=0.7, zorder=3))
    cols_all = [net_col.get(order[q], '#c4574d') for q in g]
    for q, c in enumerate(cols_all):                       # network strip along the matrix
        ax.add_patch(Rectangle((mx0 + q * ms_ / n, my0 + ms_ + 0.4), ms_ / n, 1.0, fc=c, ec='none', zorder=3))
    arrow(ax, (bx0 + bw_ + 0.4, by0 + bh / 2), (mx0 - 0.6, by0 + bh / 2), head=8, lw=1.0)
    ax.text(bx0 + bw_ / 2, 68.5, 'fMRI regions', fontsize=T_SMALL - 1.5, color=GREY, ha='center', va='top')
    ax.text(mx0 + ms_ / 2 - 0.5, 68.5, 'Connectivity', fontsize=T_SMALL - 1.5, color=GREY, ha='center', va='top')

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
    panel(axb, 4, 57, 'Test-time adaptation')
    panel(axb, 86, 57, 'Compact models by distillation')
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
    ax.text(X(1.5), 73, 'Imaging device, weather, developmental stage', fontsize=T_SMALL, color=GREY, ha='center', va='top')

    ax = axb
    # test-time adaptation (conceptual): unlabeled deployment frames update the model before it predicts
    from skimage import data as skdata
    scene = skdata.rocket().astype(float)[60:360, 120:510] / 255        # stand-in outdoor frame (public domain)
    for k, fog in enumerate((0.0, 0.35, 0.65)):
        fx, fy = 6 + k * 3.2, 22 + k * 4.2
        img = scene * (1 - fog) + fog * np.array([0.86, 0.87, 0.89])
        ax.imshow(img, extent=(fx, fx + 17, fy, fy + 13), zorder=2 + k, aspect='auto')
        ax.add_patch(Rectangle((fx, fy), 17, 13, fc='none', ec='white', lw=0.8, zorder=2 + k))
    ax.text(16.5, 18.6, 'Unlabeled', fontsize=T_SMALL, color=GREY, ha='center', va='top')
    ax.text(16.5, 13.6, 'test data', fontsize=T_SMALL, color=GREY, ha='center', va='top')
    arrow(ax, (31.0, 32.0), (40.0, 32.0), head=9, lw=1.1)
    ax.add_patch(FancyBboxPatch((41, 26), 17, 12, boxstyle='round,pad=0,rounding_size=1.4', fc=BLUE_L, ec=BLUE, lw=1.1))
    ax.text(49.5, 32, 'Model', fontsize=T_SMALL, color=BLUE, ha='center', va='center')
    ax.add_patch(FancyArrowPatch((54.5, 38.6), (44.5, 38.6), connectionstyle='arc3,rad=1.25', arrowstyle='-|>',
                                 mutation_scale=9, lw=1.1, color=BLUE))
    ax.text(49.5, 47.2, 'adapt', fontsize=T_SMALL, color=BLUE, ha='center', va='bottom')
    arrow(ax, (58.6, 32.0), (66.0, 32.0), head=9, lw=1.1)
    ax.text(67.0, 32.0, 'Predict', fontsize=T_SMALL, color=INK, ha='left', va='center')
    ax.text(49.5, 22.6, 'no labels', fontsize=T_SMALL - 1, color=GREY, ha='center', va='top', style='italic')

    # distillation (conceptual): a large teacher trains a smaller student
    def net(cx, cy, layers, sp_x, sp_y, col, ms):
        pts = []
        for li, n_ in enumerate(layers):
            xs_ = cx + (li - (len(layers) - 1) / 2) * sp_x
            ys_ = [cy + (q - (n_ - 1) / 2) * sp_y for q in range(n_)]
            pts.append([(xs_, y) for y in ys_])
        for a_, b_ in zip(pts[:-1], pts[1:]):
            for p1 in a_:
                for p2 in b_:
                    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=RULE, lw=0.5, zorder=1)
        for layer in pts:
            for (xx, yy) in layer:
                ax.plot([xx], [yy], 'o', ms=ms, mfc=col, mec='white', mew=0.6, zorder=2)
    net(104, 32, [5, 7, 7, 5], 5.4, 3.6, MID, 4.6)
    net(140, 32, [3, 4, 3], 5.0, 4.0, BLUE, 4.6)
    ax.text(104, 17.5, 'Teacher', fontsize=T_SMALL, color=INK, ha='center', va='top')
    ax.text(140, 17.5, 'Student', fontsize=T_SMALL, color=BLUE, ha='center', va='top')
    arrow(ax, (117.5, 32), (128.5, 32), color=GREY, ls=(0, (3, 2)), head=10)
    ax.text(123, 34.2, 'distill', fontsize=T_SMALL, color=GREY, ha='center', va='bottom')
    ax.text(140, 12.4, 'fewer parameters', fontsize=T_SMALL - 1, color=TEAL, ha='center', va='top')
    save(fig, 'overview-reliable.svg')


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    fig_multimodal(); fig_medical(); fig_reliable()
    print('saved to', OUT)
