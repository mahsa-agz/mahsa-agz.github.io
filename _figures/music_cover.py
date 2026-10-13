# cover for the Music & Mental Health card: the study chart plus a few music elements
import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc, FancyBboxPatch
from PIL import Image

SRC, OUT, PREVIEW = sys.argv[1], sys.argv[2], sys.argv[3]

BG = "#f6f3fb"
BLUE = "#4c72b0"
ORANGE = "#dd8452"
GREEN = "#55a868"
INK = "#2d2a3e"

# chart without its paper caption
chart = Image.open(SRC).convert("RGB")
a = (np.asarray(chart).astype(int).sum(axis=2) < 720).sum(axis=1)
# the caption is the last block of text: cut at the blank gap just above it
ink = a > 0
last = max(y for y in range(chart.height) if ink[y])
y = last
while ink[y]:
    y -= 1
chart = chart.crop((0, 0, chart.width, y))

fig = plt.figure(figsize=(18, 10.5), dpi=100)
fig.patch.set_facecolor(BG)
bg = fig.add_axes([0, 0, 1, 1])
bg.set_xlim(0, 18)
bg.set_ylim(0, 10.5)
bg.axis("off")

# chart on a white card, right side
w = 11.6
h = w * chart.height / chart.width
bg.add_patch(FancyBboxPatch((5.55, 5.25 - h / 2 - 0.35), 12.0, h + 0.7, boxstyle="round,pad=0,rounding_size=0.25",
                            facecolor="white", edgecolor="#ddd6ea", lw=2))
ax = fig.add_axes([5.75 / 18, (5.25 - h / 2) / 10.5, w / 18, h / 10.5])
ax.imshow(chart)
ax.axis("off")

# headphones, left side
cx, cy = 2.75, 5.6
bg.add_patch(Arc((cx, cy), 3.2, 3.4, theta1=0, theta2=180, color=INK, lw=14))
for sx, c in [(-1, BLUE), (1, ORANGE)]:
    bg.add_patch(FancyBboxPatch((cx + sx * 1.6 - 0.42, cy - 1.45), 0.84, 1.55,
                                boxstyle="round,pad=0,rounding_size=0.3", facecolor=c, edgecolor=INK, lw=4))

# sound waves between the ear cups
t = np.linspace(-0.9, 0.9, 200)
for k, c in enumerate([BLUE, ORANGE, GREEN]):
    bg.plot(cx + t, cy - 0.7 + 0.28 * np.sin(t * (6 + 2 * k)) * np.cos(t * 1.6), color=c, lw=4)

# music notes, scattered
notes = [("♪", 1.1, 8.9, 54, ORANGE, -12), ("♫", 4.2, 9.0, 62, BLUE, 10),
         ("♪", 4.6, 2.3, 48, GREEN, 8), ("♫", 0.9, 2.0, 50, ORANGE, -6),
         ("♪", 2.8, 9.7, 36, GREEN, 0)]
for s, x, y, size, c, rot in notes:
    bg.text(x, y, s, fontsize=size, color=c, ha="center", va="center", rotation=rot, fontfamily="DejaVu Sans")

fig.savefig(OUT, dpi=100, facecolor=BG)
fig.savefig(PREVIEW, dpi=55, facecolor=BG)
print("saved")
