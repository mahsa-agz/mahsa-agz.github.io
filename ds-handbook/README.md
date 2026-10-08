# DS Handbook

A 30-day data science study plan: a handbook website plus daily practice notebooks for Google Colab.
This folder is part of the personal website and is served at https://mahsa-agz.github.io/ds-handbook/.

- **Handbook website:** https://mahsa-agz.github.io/ds-handbook/ (English, Persian, Korean)
- **Start here:** [exam_prep/00_start_here.ipynb](https://colab.research.google.com/github/mahsa-agz/mahsa-agz.github.io/blob/main/ds-handbook/exam_prep/00_start_here.ipynb) (opens in Colab)

## What is inside

| Path | Content |
|---|---|
| `index.html`, `app.js`, `plan.json`, `content/` | The handbook website: plan, algorithms, SQL, statistics, AI and ML, cheat sheets, daily theory flashcards, resources |
| `exam_prep/` | 30 days x 4 notebooks (algorithms, SQL, statistics, AI), easy to hard, with hints and full solutions; `data/` holds the real datasets they use |
| `_build/` | The scripts that generate everything above (Jekyll does not publish folders that start with `_`) |

## How to use
1. Open `exam_prep/00_start_here.ipynb` in Colab (link above). Every day has four links that open the notebooks in Colab.
2. Run the **Setup** cell first in every notebook: it downloads the data it needs from this repository.
3. To keep your answers, use **File > Save a copy in Drive** in Colab.

## Rebuilding (only needed after changing content)
Requires Python 3.11+ with numpy, pandas, scipy, statsmodels, scikit-learn, matplotlib, nbformat, nbclient.

```bash
cd ds-handbook/_build/exam30
python build_site.py                 # website files in ds-handbook/
python start_here.py                 # exam_prep/00_start_here.ipynb
python nb/algo_01.py                 # one notebook (pattern: nb/<area>_<DD>.py)
python verify_exam.py day_01         # run and check notebooks
```

## Data
The datasets in `exam_prep/data/` come from public sources (UCI, seaborn-data, MovieLens, Chinook, Northwind and
others). Sources and licenses are listed in `_build/exam30/DATASETS.md`. Some files have no clear license and are used
for study only.
