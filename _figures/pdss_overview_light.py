# turn the dark 3R overview figure into a white-background version
import sys

import numpy as np
from PIL import Image

src, out, preview = sys.argv[1], sys.argv[2], sys.argv[3]

im = Image.open(src).convert("RGB")
im = im.resize((2000, round(2000 * im.height / im.width)), Image.LANCZOS)
a = np.asarray(im).astype(float)

r, g, b = a[..., 0], a[..., 1], a[..., 2]
light = a.max(axis=2)
chroma = light - a.min(axis=2)

# neutral pixels (black background, dark navy panels, white text) get their brightness flipped;
# coloured pixels (orange, cyan) stay as they are
neutral = chroma < 60
flip = 255 - a
res = np.where(neutral[..., None], flip, a)

# dark navy panels become a soft blue-grey instead of near-white
navy = (b > r + 8) & (light < 70) & (light > 20)
res[navy] = [236, 241, 248]

# white headings ("Modeling", "Explain") become dark ink, not pure black
ink = neutral & (light > 180)
res[ink] = [34, 40, 49]

# orange reads pale on white: darken it a little
orange = (~neutral) & (r > g) & (g > b)
res[orange] = res[orange] * 0.86

Image.fromarray(res.clip(0, 255).astype(np.uint8)).save(out, quality=90)
Image.fromarray(res.clip(0, 255).astype(np.uint8)).resize((1000, round(1000 * im.height / im.width))).save(preview)
print("saved")
