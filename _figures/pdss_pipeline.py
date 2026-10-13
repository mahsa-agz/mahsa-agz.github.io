# multimodal pipeline figure, same layout as the AML figure
import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc, Circle, Ellipse, FancyBboxPatch, Polygon, Rectangle

OUT = sys.argv[1]

INK = "#1f1f1f"
GREY = "#9e9e9e"
GREEN = "#3f8f5f"
ORANGE = "#d9822b"
RED = "#c94a4a"
ALERT = "#c62828"
PURPLE = "#a64bd6"
FONT = "Segoe UI"

fig, ax = plt.subplots(figsize=(20, 9), dpi=100)
ax.set_xlim(0, 20)
ax.set_ylim(0, 9)
ax.axis("off")


def box(x, y, w, h, face="white", edge=INK, lw=2, r=0.12, ls="-"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                facecolor=face, edgecolor=edge, lw=lw, ls=ls))


def arrow(x1, y1, x2, y2, color=INK, lw=1.2, head=10):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=head))


def label(x, y, text, size=15, color=INK, weight="normal"):
    ax.text(x, y, text, ha="center", va="center", fontsize=size, color=color,
            fontfamily=FONT, weight=weight)


def session(x, y, color):
    # one session tile: a short behaviour signal inside a rounded card
    box(x, y, 0.95, 0.55, face=color, edge="#333333", lw=1.6, r=0.08)
    t = np.linspace(0, 1, 60)
    ax.plot(x + 0.12 + 0.71 * t, y + 0.275 + 0.12 * np.sin(t * 4 * np.pi) * np.exp(-t),
            color="white", lw=2.2, solid_capstyle="round")


# ---------- icons ----------
def eye(cx, cy):
    ax.add_patch(Ellipse((cx, cy), 0.75, 0.42, facecolor="white", edgecolor=INK, lw=2))
    ax.add_patch(Circle((cx, cy), 0.13, facecolor=INK))
    ax.add_patch(Circle((cx + 0.04, cy + 0.04), 0.035, facecolor="white"))


def keyboard(cx, cy):
    box(cx - 0.4, cy - 0.22, 0.8, 0.44, lw=2, r=0.05)
    for row in range(2):
        for col in range(5):
            ax.add_patch(Rectangle((cx - 0.32 + col * 0.13, cy + 0.03 - row * 0.15), 0.09, 0.09,
                                   facecolor=INK, edgecolor="none"))
    ax.add_patch(Rectangle((cx - 0.2, cy - 0.17), 0.4, 0.06, facecolor=INK))


def stylus(cx, cy):
    body = np.array([[-0.32, 0.18], [0.22, -0.16], [0.28, -0.08], [-0.26, 0.26]])
    ax.add_patch(Polygon(body + [cx, cy], closed=True, facecolor="white", edgecolor=INK, lw=2))
    tip = np.array([[0.22, -0.16], [0.36, -0.24], [0.28, -0.08]])
    ax.add_patch(Polygon(tip + [cx, cy], closed=True, facecolor=INK, edgecolor=INK, lw=2))
    t = np.linspace(0, 1, 40)


def mic(cx, cy):
    box(cx - 0.11, cy - 0.05, 0.22, 0.36, lw=2, r=0.1)
    ax.add_patch(Arc((cx, cy + 0.05), 0.42, 0.42, theta1=200, theta2=340, color=INK, lw=2))
    ax.plot([cx, cx], [cy - 0.16, cy - 0.27], color=INK, lw=2)
    ax.plot([cx - 0.1, cx + 0.1], [cy - 0.27, cy - 0.27], color=INK, lw=2)


def baseline(cx, cy):
    # personal baseline: the usual range of a user's behaviour, one point outside it
    x = np.linspace(-0.6, 0.6, 100)
    y = 0.55 * np.exp(-(x / 0.22) ** 2)
    ax.fill_between(cx + x, cy - 0.3, cy - 0.3 + y, where=np.abs(x) < 0.3, color=PURPLE, alpha=0.25, lw=0)
    ax.plot(cx + x, cy - 0.3 + y, color=PURPLE, lw=2.5)
    ax.plot([cx - 0.65, cx + 0.65], [cy - 0.3, cy - 0.3], color=INK, lw=1.5)
    ax.add_patch(Circle((cx + 0.5, cy - 0.15), 0.07, facecolor=RED, edgecolor="none"))


def evidence(cx, cy):
    for i, c in enumerate(["#9cc9f0", "#f4b183", "#a9d8b8"]):
        ax.add_patch(Rectangle((cx - 0.32, cy + 0.12 - i * 0.16), 0.11, 0.11, facecolor=c))
        ax.plot([cx - 0.15, cx + 0.32], [cy + 0.175 - i * 0.16] * 2, color=INK, lw=1.8)


def events(cx, cy):
    xs = cx + np.array([-0.36, -0.12, 0.12, 0.36])
    ax.plot(xs, [cy] * 4, color=INK, lw=1.8)
    for x, c in zip(xs, [GREY, GREY, ORANGE, GREY]):
        ax.add_patch(Circle((x, cy), 0.08, facecolor=c, edgecolor=INK, lw=1.4))


def bubble(cx, cy):
    box(cx - 0.32, cy - 0.12, 0.64, 0.38, lw=2, r=0.08)
    ax.add_patch(Polygon([[cx - 0.18, cy - 0.12], [cx - 0.24, cy - 0.26], [cx - 0.05, cy - 0.12]],
                         closed=True, facecolor="white", edgecolor=INK, lw=2))
    for i in range(2):
        ax.plot([cx - 0.2, cx + 0.2 - i * 0.12], [cy + 0.14 - i * 0.12] * 2, color=INK, lw=1.8)


def person(cx, cy):
    ax.add_patch(Circle((cx, cy + 0.14), 0.12, facecolor="white", edgecolor=INK, lw=2))
    ax.add_patch(Arc((cx, cy - 0.22), 0.5, 0.48, theta1=0, theta2=180, color=INK, lw=2))


# ---------- top row: sessions in ----------
for i in range(5):
    session(0.35 + i * 1.03, 6.1, GREY)
label(2.85, 5.6, "sessions (sequences of events)", size=13, color="#555555")

# ---------- dashed box: modalities -> personal baseline ----------
box(5.65, 3.95, 5.7, 4.75, lw=2.2, r=0.02, ls=(0, (4, 3)))
mods = [("Eye tracking", eye), ("Keyboard", keyboard), ("Stylus", stylus), ("Voice", mic)]
for k, (name, icon) in enumerate(mods):
    y = 8.05 - k * 1.1
    icon(6.75, y + 0.12)
    label(6.75, y - 0.38, name, size=14)
    arrow(7.55, y, 8.95, 6.45 + (1.5 - k) * 0.3)
baseline(9.95, 6.55)
label(9.95, 5.75, "Personal baseline", size=15, color=PURPLE)
label(9.95, 5.4, "per-user model", size=12, color=PURPLE)

# ---------- top row: sessions out ----------
for i, c in enumerate([RED, GREEN, GREEN, ORANGE, GREEN]):
    session(11.55 + i * 1.03, 6.1, c)
ax.text(12.35, 5.6, "usual (green) or departing from the baseline", ha="left", va="center", fontsize=13, color="#555555", fontfamily=FONT)

# ---------- flag path ----------
ax.plot([12.02, 12.02], [6.05, 3.15], color=ALERT, lw=3.5)
ax.plot([12.02, 7.1], [3.15, 3.15], color=ALERT, lw=3.5)
arrow(7.1, 3.17, 7.1, 2.05, color=ALERT, lw=3.5, head=28)
label(13.25, 4.55, "Unusual session", size=17, color=ALERT)
ax.add_patch(Rectangle((14.75, 4.2), 0.05, 0.85, facecolor="#2b2b5a"))
ax.add_patch(Polygon([[14.8, 5.05], [15.45, 4.85], [14.8, 4.6]], closed=True, facecolor="#f05a5a"))

# ---------- bottom row ----------
steps = [
    ("Multimodal\nFeatures", evidence),
    ("Event\nSequence", events),
    ("Compare to\nBaseline", baseline),
    ("Describe the\nChange", bubble),
    ("Report to\nClinician", person),
]
w, h, gap, x0 = 2.3, 1.55, 0.42, 5.95
for k, (name, icon) in enumerate(steps):
    x = x0 + k * (w + gap)
    box(x, 0.45, w, h, lw=2.2, r=0.1)
    icon(x + w / 2, 1.62)
    label(x + w / 2, 0.88, name, size=14)
    if k < len(steps) - 1:
        arrow(x + w + 0.02, 1.22, x + w + gap - 0.02, 1.22, lw=1.8, head=16)

fig.savefig(OUT, dpi=100, bbox_inches="tight", facecolor="white")
print("saved", OUT)
