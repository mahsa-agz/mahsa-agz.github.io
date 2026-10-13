# cover for the cold-start music recommender, drawn from the README's description of the method
# (content tower for every song, co-occurrence tower only in training, contrastive loss between them)
import sys

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Polygon

OUT, PREVIEW = sys.argv[1], sys.argv[2]

INK = "#1f1f1f"
MUTED = "#555555"
GREY = "#a6a6a6"
PURPLE = "#8e5bd6"
TEAL = "#2a9d8f"
BLUE = "#3a7bd5"
ORANGE = "#e07a2f"
FONT = "Segoe UI"

fig, ax = plt.subplots(figsize=(18, 9.6), dpi=100)
fig.patch.set_facecolor("white")
fig.subplots_adjust(0, 0, 1, 1)
ax.set_xlim(0, 18)
ax.set_ylim(0, 9.6)
ax.axis("off")


def box(x, y, w, h, edge=INK, face="white", lw=2.4, ls="-"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.15",
                                facecolor=face, edgecolor=edge, lw=lw, ls=ls))


def text(x, y, s, size=16, color=INK, weight="normal", ha="center"):
    ax.text(x, y, s, ha=ha, va="center", fontsize=size, color=color, fontfamily=FONT, weight=weight)


def arrow(x1, y1, x2, y2, color=INK, lw=2.4, head=20, ls="-"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=head, linestyle=ls,
                                shrinkA=0, shrinkB=0))


def tower(cx, cy, color, label, ls="-"):
    ax.add_patch(Polygon([[cx - 0.95, cy + 0.75], [cx + 0.95, cy + 0.42], [cx + 0.95, cy - 0.42], [cx - 0.95, cy - 0.75]],
                         closed=True, facecolor=color, alpha=0.15, edgecolor=color, lw=2.4, ls=ls))
    ax.add_patch(Polygon([[cx - 0.95, cy + 0.75], [cx + 0.95, cy + 0.42], [cx + 0.95, cy - 0.42], [cx - 0.95, cy - 0.75]],
                         closed=True, fill=False, edgecolor=color, lw=2.4, ls=ls))
    text(cx, cy, label, 14, color, "bold")


def vector(cx, cy, color):
    for i in range(5):
        ax.add_patch(FancyBboxPatch((cx - 0.15, cy - 0.68 + i * 0.28), 0.3, 0.22,
                                    boxstyle="round,pad=0,rounding_size=0.04", facecolor=color, edgecolor="none",
                                    alpha=0.4 + 0.12 * i))


def note(x, y, size, color, glyph="♪"):
    ax.text(x, y, glyph, fontsize=size, color=color, ha="center", va="center", fontfamily="DejaVu Sans")


def person(cx, cy):
    ax.add_patch(Circle((cx, cy + 0.28), 0.22, facecolor="white", edgecolor=INK, lw=2.2))
    ax.add_patch(FancyBboxPatch((cx - 0.34, cy - 0.42), 0.68, 0.42, boxstyle="round,pad=0,rounding_size=0.18",
                                facecolor="white", edgecolor=INK, lw=2.2))


# ---------- legend ----------
text(0.5, 9.0, "Cold-start music recommendation", 23, INK, "bold", ha="left")
ax.plot([9.3, 10.1], [9.0, 9.0], color=INK, lw=2.4)
text(10.25, 9.0, "every song", 13, MUTED, ha="left")
ax.plot([11.9, 12.7], [9.0, 9.0], color=INK, lw=2.4, ls=(0, (3, 2)))
text(12.85, 9.0, "training only", 13, MUTED, ha="left")

# ---------- row 1: user ----------
YU, YC, YZ = 7.3, 5.0, 2.2
person(1.05, YU)
text(1.05, YU - 0.8, "user", 13, MUTED)
arrow(1.6, YU, 2.15, YU, BLUE)
tower(3.1, YU, BLUE, "user")
arrow(4.05, YU, 4.7, YU, BLUE)
vector(5.0, YU, BLUE)

# ---------- row 2: song content (every song, also new ones) ----------
note(1.05, YC + 0.2, 40, PURPLE, "♫")
text(1.05, YC - 0.75, "genre, artist, album", 12, MUTED)
arrow(1.6, YC, 2.15, YC, PURPLE)
tower(3.1, YC, PURPLE, "content")
arrow(4.05, YC, 4.7, YC, PURPLE)
vector(5.0, YC, PURPLE)

# ---------- row 3: who listened (warm songs, training only) ----------
for i, c in enumerate([TEAL, TEAL, GREY, TEAL]):
    ax.add_patch(Circle((0.8 + (i % 2) * 0.5, YZ + 0.25 - (i // 2) * 0.5), 0.18, facecolor=c, edgecolor="none"))
text(1.05, YZ - 0.8, "listeners", 12, MUTED)
arrow(1.6, YZ, 2.15, YZ, TEAL, ls="--")
tower(3.1, YZ, TEAL, "co-occurrence", ls="--")
arrow(4.05, YZ, 4.7, YZ, TEAL, ls="--")
vector(5.0, YZ, TEAL)

# ---------- contrastive loss between the two song embeddings ----------
ax.annotate("", xy=(5.75, YC - 0.55), xytext=(5.75, YZ + 0.55),
            arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=2.2, mutation_scale=18, linestyle="--"))
box(6.05, 3.15, 2.25, 0.9, edge=INK, ls=(0, (4, 3)))
text(7.18, 3.6, "contrastive loss", 14, INK, "bold")

# ---------- score -> top-5 users ----------
box(8.0, 5.6, 2.1, 1.3, edge=ORANGE)
text(9.05, 6.45, "score", 16, ORANGE, "bold")
text(9.05, 6.0, "user × song", 12, MUTED)
arrow(5.35, YU, 8.0, 6.55, BLUE)
arrow(5.35, YC, 8.0, 5.95, PURPLE)
arrow(10.1, 6.25, 10.85, 6.25, ORANGE)
box(10.85, 5.3, 2.0, 1.9, edge=ORANGE, face="#fff4ec")
note(11.35, 6.65, 26, ORANGE)
text(12.0, 6.65, "new", 13, ORANGE, "bold")
text(11.85, 6.05, "top-5 users", 14, INK, "bold")
text(11.85, 5.65, "per new song", 12, MUTED)

# ---------- result ----------
names = ["Content-KNN", "CCFCRec"]
vals = [0.525, 0.768]
colors = [GREY, ORANGE]
x0, base, scale, bw = 14.0, 1.25, 7.0, 1.3
ax.add_patch(FancyBboxPatch((13.5, 0.45), 4.15, 8.0, boxstyle="round,pad=0,rounding_size=0.2",
                            facecolor="#fafafa", edgecolor="#e3e3e3", lw=1.5))
for k, (n, v, c) in enumerate(zip(names, vals, colors)):
    x = x0 + k * 1.8
    ax.add_patch(FancyBboxPatch((x, base), bw, v * scale, boxstyle="round,pad=0,rounding_size=0.06",
                                facecolor=c, edgecolor="none"))
    text(x + bw / 2, base - 0.38, n, 13, INK)
    text(x + bw / 2, base + v * scale + 0.35, f"{v:.2f}", 16, MUTED if c == GREY else c, "bold")
text(x0 + 1.8 + bw / 2, base + vals[1] * scale + 0.85, "+46%", 15, ORANGE, "bold")
ax.plot([x0 - 0.2, x0 + 3.3], [base, base], color=INK, lw=1.5)
text(15.57, 8.0, "HR@5, 25K unseen songs", 13, MUTED)

fig.savefig(OUT, dpi=100, facecolor="white")
fig.savefig(PREVIEW, dpi=55, facecolor="white")
print("saved")
