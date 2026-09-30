# Secure AI Hackathon Day 2 & 3 — local workspace

Competition: https://www.kaggle.com/competitions/secure-ai-hackathon
Deadline: 2026-09-30 23:59 UTC

| Path | What |
|---|---|
| `docs/OVERVIEW.md` | All Kaggle pages: description, tracks, evaluation rubric, submission requirements, rules, data description |
| `docs/pages.json`, `docs/competition.json`, `docs/tracks.json` | Raw API responses the overview was built from |
| `docs/DAY1_README.md`, `docs/DAY1_DATASET.md`, `docs/01_Beginner_Track_Day1.ipynb` | Day 1 material for reference |
| `kaggle/02_Intermediate_Advanced_Day2.ipynb` | Day 2 starter notebook (the harness: data, partitions, WeakMLP, run_fl, hooks, export cell) |
| `kaggle/test_public.csv`, `kaggle/sample_submission.csv` | Day 1 leftovers on the competition data tab; not used for Day 2 scoring |
| `data/KDDTrain+.txt`, `data/KDDTest+.txt` | Raw NSL-KDD, same files the notebook downloads |
| `repos/NSL-KDD-Dataset/` | Clone of github.com/jmnwong/NSL-KDD-Dataset (the notebook's data source) |
| `day1_code/` | Our Day 1 scripts (train.py, tune.py, trees*.py) for the reusable pipeline |

## Deliverables (from Submission Requirements)
1. Kaggle Writeup, max 1500 words, with before/after F1 clearly stated.
2. Cover image in Media Gallery.
3. Public notebook, fully run top to bottom.
4. Video, 3 minutes or less, on YouTube.
5. Public GitHub repo with `model_scripted.pt`, `submission.json`, README with reproduction steps.

## Reproduce our results
```
python3 -m venv .venv && .venv/bin/pip install torch scikit-learn pandas numpy
.venv/bin/python solution.py
```
Prints all before/after F1 numbers and writes `model_scripted.pt`, `submission.json`, `results.json`. See `WRITEUP.md`.

Notebook route (what the judges re-run): `pip install matplotlib nbconvert ipykernel`, then
`python build_notebook.py && python -m nbconvert --to notebook --execute --inplace 02_Intermediate_Advanced_Day2.ipynb`.
The executed notebook, `cover.png`, `model_scripted.pt` and `submission.json` are committed.
