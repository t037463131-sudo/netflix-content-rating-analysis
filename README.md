# Netflix Content & Rating Analysis

A Python course project analyzing 5,850 Netflix movie and TV show records using data cleaning, descriptive statistics, and grouped comparisons.

## Research questions
- How do movies and TV shows differ in title counts and average IMDb ratings?
- Which genres are most common, and which have the highest average IMDb ratings?

## Tools and methods
Python standard library (`csv`, `ast`, `math`, `collections`, `pathlib`) and Matplotlib for optional charts. Custom functions calculate mean, median, and population standard deviation. Records are checked for missing or duplicate IDs and invalid content types. Missing numeric values are excluded from the relevant calculation. Genre rating comparisons require at least 30 rated titles.

## Verified results
| Metric | Result |
| --- | --- |
| Unique titles analyzed | 5,850 |
| Movies / TV shows | 3,744 / 2,106 |
| Average IMDb rating: movies / TV shows | 6.25 / 6.98 |
| Overall average IMDb rating | 6.51 |
| Titles missing a valid IMDb rating | 482 |

Drama (2,968 titles) and Comedy (2,325) are the most common genre labels. History (7.13), War (7.07), and Documentation (7.01; the dataset's label for documentaries) have the highest average IMDb ratings among eligible genres.

## Files
- `netflix_analysis.py`: analysis and chart-generation code
- `analysis_summary.txt`: verified text output
- `Netflix_Dataset_Analysis.pptx`: project presentation
- `requirements.txt`: chart dependency

## Reproduce the analysis
1. Download `titles.csv` from the [Kaggle dataset](https://www.kaggle.com/datasets/victorsoeiro/netflix-tv-shows-and-movies). Use the 5,850-row snapshot for the results above; other versions may differ.
2. Put `titles.csv` in the same directory as `netflix_analysis.py`. If your downloaded file has another name, rename it to `titles.csv`.
3. Install the plotting dependency and run:

```bash
python3 -m pip install -r requirements.txt
python3 netflix_analysis.py
```

The script writes `analysis_summary.txt` and three PNG charts in `charts/`. Without Matplotlib, it still produces the text summary.

## Interpretation and limitations
This dataset is a historical snapshot, not a current inventory of Netflix titles. IMDb ratings do not measure Netflix viewership, revenue, or the preferences of all subscribers. Comparisons are descriptive and do not establish causality. Average ratings are calculated per title, without weighting by vote counts. Titles may have multiple genres, so genre counts overlap. Movie runtime and TV show runtime are not directly comparable as total viewing duration; show runtime can represent an episode rather than an entire series. The combined runtime average should therefore be interpreted cautiously.

## Project context
Prepared as a Python course final project for UC Berkeley Extension. This is an independent academic analysis and is not affiliated with Netflix.
