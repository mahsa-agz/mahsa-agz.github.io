# mahsa-agz.github.io

Personal site, served at <https://mahsa-agz.github.io>.

## Structure

```
.
├── index.html              # Home — short hero, currently strip, featured + contact
├── about/index.html        # Long-form bio + education + beyond work + recognition
├── work/index.html         # Research + experience + selected projects + toolkit
├── blog/
│   ├── index.html          # Blog index — lists all posts
│   └── _template.html      # Copy this to start a new post
├── 404.html                # Custom not-found page
├── styles/
│   ├── main.css            # Site-wide design tokens + layout
│   └── post.css            # Long-form article styles
├── scripts/main.js         # Theme toggle, tabs, scroll progress, image protect
├── assets/
│   ├── images/about/       # Profile + about photos
│   ├── images/taekwondo/
│   ├── images/drawings/
│   ├── images/photography/
│   └── favicon.svg
├── sitemap.xml             # Add new post URLs here
├── robots.txt
└── mahsa_resume.tex        # CV source (compile to mahsa_resume.pdf)
```

## Page architecture

- `/` — landing: hero, currently, featured work, blog teaser, contact.
- `/about/` — bio, education, beyond work (taekwondo / photography / drawing), recognition.
- `/work/` — research, experience, selected projects, toolkit.
- `/blog/` — single unified feed of writing. New posts land here.
- `/blog/<slug>.html` — individual posts, each with comments placeholder.

## Local preview

```bash
python -m http.server 8000
# then visit http://localhost:8000
```

## Adding a new post

1. Copy `blog/_template.html` to `blog/<slug>.html` (e.g. `blog/pca.html`).
2. Fill in: `<title>`, description, Open Graph tags, JSON-LD dates, visible header, body.
3. Add a `<li class="note">` entry to the Notes section in `index.html`
   (under `notes-panel-all` and `notes-panel-site`). For LinkedIn-only
   posts, add the entry under `notes-panel-all` and `notes-panel-linkedin`
   with an `https://linkedin.com/...` URL.
4. Add a `<li class="post-list__item">` entry to `blog/index.html`.
5. Add a `<url>` block to `sitemap.xml`.
6. Commit & push — GitHub Pages publishes automatically.

## Comments (giscus)

The post template includes a comments placeholder. To enable real comments
(stored in this repo's GitHub Discussions, free, no ads):

1. Repo → Settings → General → Features → enable **Discussions**.
2. Go to <https://giscus.app> and configure with this repo:
   - **Mapping:** pathname (each post URL becomes its own thread)
   - **Category:** Announcements (or another read-only-by-default category)
   - **Theme:** `preferred_color_scheme` (auto-matches light/dark mode)
3. Copy the generated `<script>` snippet.
4. In `blog/_template.html`, replace the placeholder inside
   `<section class="post__comments">` with that snippet.
5. From now on, every new post copied from the template gets comments.

## Sharing a post on LinkedIn

LinkedIn reads the Open Graph tags in the post `<head>`. Once a post is live,
paste its full URL into a LinkedIn post and the preview card renders
automatically. If the preview looks stale, refresh with the
[LinkedIn Post Inspector](https://www.linkedin.com/post-inspector/).

**Don't iframe LinkedIn embeds** — they're heavy and break when LinkedIn
changes their embed code. The Notes section's "LinkedIn" tab is meant to
hold link cards back to the LinkedIn post, not embedded iframes.

## Image protection — what it does and doesn't do

Photos in the hero portrait and the Beyond-work galleries carry
`data-protect`. The CSS + JS deterrents do:

- Disable the right-click "Save image as…" menu on those images.
- Disable drag-to-save (dragging an image out of the page).
- Disable text selection / long-press image actions on mobile.

The deterrents do **NOT**:

- Prevent screenshots (no website on Earth can — it's an OS-level action).
- Prevent DevTools / "View source" extraction (anyone with a browser can).
- Prevent download via the browser's network inspector.

If you have photos you genuinely don't want anyone to save, the only
reliable options are: (a) don't put them on a public site, (b) watermark
them before uploading, or (c) upload only low-resolution versions so any
saved copy is too small to use.

## Notes

- One CV PDF lives at `mahsa_resume.pdf` (linked from the hero "Download CV"
  button — generate it from `mahsa_resume.tex`).
- Default social preview image is `assets/og-default.png` (1200×630).
