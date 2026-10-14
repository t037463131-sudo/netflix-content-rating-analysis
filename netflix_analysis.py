"""Analyze Netflix TV shows and movies using Python's standard library and Matplotlib.

Dataset source: https://www.kaggle.com/datasets/victorsoeiro/netflix-tv-shows-and-movies
Place titles.csv in the same folder as this script, then run:
    python3 netflix_analysis.py
"""

import ast
import csv
import math
from collections import defaultdict
from pathlib import Path

try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    plt = None


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "titles.csv"
CHART_DIR = BASE_DIR / "charts"
SUMMARY_FILE = BASE_DIR / "analysis_summary.txt"


def mean(numbers):
    """Return the arithmetic mean of a non-empty list."""
    return sum(numbers) / len(numbers)


def median(numbers):
    """Return the middle value of a list, or the mean of two middle values."""
    numbers = sorted(numbers)
    middle = len(numbers) // 2
    if len(numbers) % 2 == 1:
        return numbers[middle]
    return (numbers[middle - 1] + numbers[middle]) / 2


def standard_deviation(numbers):
    """Return the population standard deviation of a non-empty list."""
    average = mean(numbers)
    variance = sum((number - average) ** 2 for number in numbers) / len(numbers)
    return math.sqrt(variance)


def parse_number(value):
    """Convert a numeric CSV value to float, returning None for blanks or invalid values."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_genres(value):
    """Convert a CSV string such as "['drama', 'comedy']" into a list of genres."""
    try:
        genres = ast.literal_eval(value)
        return genres if isinstance(genres, list) else []
    except (ValueError, SyntaxError):
        return []


def load_titles(filename):
    """Read, clean, and return valid Netflix title dictionaries plus cleaning counts."""
    titles = []
    seen_ids = set()
    cleaning = defaultdict(int)

    with filename.open(encoding="utf-8") as csv_file:
        for row in csv.DictReader(csv_file):
            cleaning["rows_read"] += 1
            title_id = row["id"].strip()
            if not title_id or title_id in seen_ids:
                cleaning["duplicate_or_missing_id"] += 1
                continue
            seen_ids.add(title_id)

            content_type = row["type"].strip()
            if content_type not in {"MOVIE", "SHOW"}:
                cleaning["invalid_type"] += 1
                continue

            release_year = parse_number(row["release_year"])
            runtime = parse_number(row["runtime"])
            imdb_score = parse_number(row["imdb_score"])
            genres = parse_genres(row["genres"])

            if release_year is None:
                cleaning["missing_release_year"] += 1
            if runtime is None or runtime <= 0:
                cleaning["missing_or_invalid_runtime"] += 1
                runtime = None
            if imdb_score is None or not 0 <= imdb_score <= 10:
                cleaning["missing_or_invalid_imdb_score"] += 1
                imdb_score = None
            if not genres:
                cleaning["missing_genres"] += 1
                genres = ["unknown"]

            titles.append(
                {
                    "id": title_id,
                    "title": row["title"].strip(),
                    "type": content_type,
                    "release_year": int(release_year) if release_year is not None else None,
                    "runtime": runtime,
                    "genres": genres,
                    "imdb_score": imdb_score,
                    "imdb_votes": parse_number(row["imdb_votes"]),
                }
            )

    cleaning["usable_title_rows"] = len(titles)
    return titles, cleaning


def group_titles(titles, key):
    grouped = defaultdict(list)
    for title in titles:
        grouped[title[key]].append(title)
    return grouped


def numeric_values(titles, column):
    return [title[column] for title in titles if title[column] is not None]


def make_genre_groups(titles):
    genre_groups = defaultdict(list)
    for title in titles:
        for genre in title["genres"]:
            if genre != "unknown":
                genre_groups[genre].append(title)
    return genre_groups


def write_chart_type_counts(type_groups):
    if plt is None:
        return
    labels = ["Movie", "TV Show"]
    counts = [len(type_groups["MOVIE"]), len(type_groups["SHOW"])]
    plt.figure(figsize=(8, 5))
    bars = plt.bar(labels, counts, color=["#E50914", "#221F1F"])
    plt.title("Netflix Titles by Content Type")
    plt.ylabel("Number of titles")
    plt.bar_label(bars, padding=3)
    plt.tight_layout()
    plt.savefig(CHART_DIR / "titles_by_type.png", dpi=200)
    plt.close()


def write_chart_genre_counts(genre_groups):
    if plt is None:
        return
    top_genres = sorted(genre_groups, key=lambda genre: len(genre_groups[genre]), reverse=True)[:10]
    labels = [genre.title() for genre in reversed(top_genres)]
    counts = [len(genre_groups[genre]) for genre in reversed(top_genres)]
    plt.figure(figsize=(10, 6))
    bars = plt.barh(labels, counts, color="#B20710")
    plt.title("Top 10 Genres by Number of Netflix Titles")
    plt.xlabel("Number of titles")
    plt.bar_label(bars, padding=3)
    plt.tight_layout()
    plt.savefig(CHART_DIR / "top_genres_by_count.png", dpi=200)
    plt.close()


def write_chart_genre_scores(genre_groups):
    # Requiring 30 rated titles makes the comparison less affected by small groups.
    scored_genres = []
    for genre, titles in genre_groups.items():
        scores = numeric_values(titles, "imdb_score")
        if len(scores) >= 30:
            scored_genres.append((genre, mean(scores), len(scores)))
    top_genres = sorted(scored_genres, key=lambda item: item[1], reverse=True)[:10]
    if plt is not None:
        labels = [genre.title() for genre, score, count in reversed(top_genres)]
        scores = [score for genre, score, count in reversed(top_genres)]
        plt.figure(figsize=(10, 6))
        bars = plt.barh(labels, scores, color="#564D4D")
        plt.title("Top 10 Genres by Average IMDb Score (at least 30 rated titles)")
        plt.xlabel("Average IMDb score")
        plt.xlim(0, 10)
        plt.bar_label(bars, labels=[f"{score:.2f}" for score in scores], padding=3)
        plt.tight_layout()
        plt.savefig(CHART_DIR / "top_genres_by_imdb_score.png", dpi=200)
        plt.close()
    return top_genres


def format_summary(titles, cleaning, type_groups, genre_groups, top_scored_genres):
    runtimes = numeric_values(titles, "runtime")
    scores = numeric_values(titles, "imdb_score")
    top_titles = sorted(
        (title for title in titles if title["imdb_score"] is not None),
        key=lambda title: (title["imdb_score"], title["imdb_votes"] or 0),
        reverse=True,
    )[:10]

    lines = [
        "NETFLIX TV SHOWS AND MOVIES DATASET ANALYSIS",
        "=" * 46,
        "",
        "DATASET AND CLEANING",
        f"Rows read: {cleaning['rows_read']:,}",
        f"Usable unique title rows: {cleaning['usable_title_rows']:,}",
        f"Rows with missing or invalid runtime: {cleaning['missing_or_invalid_runtime']:,}",
        f"Rows with missing or invalid IMDb score: {cleaning['missing_or_invalid_imdb_score']:,}",
        f"Rows with missing genres: {cleaning['missing_genres']:,}",
        "",
        "DESCRIPTIVE STATISTICS",
        f"Runtime (minutes): min {min(runtimes):.0f}, max {max(runtimes):.0f}, mean {mean(runtimes):.2f}, median {median(runtimes):.0f}",
        f"IMDb score: min {min(scores):.1f}, max {max(scores):.1f}, mean {mean(scores):.2f}, median {median(scores):.1f}, standard deviation {standard_deviation(scores):.2f}",
        "",
        "GROUP STATISTICS BY CONTENT TYPE",
    ]
    for content_type in ["MOVIE", "SHOW"]:
        group = type_groups[content_type]
        group_scores = numeric_values(group, "imdb_score")
        group_runtimes = numeric_values(group, "runtime")
        lines.append(
            f"{content_type.title()}: {len(group):,} titles, "
            f"average IMDb {mean(group_scores):.2f} ({len(group_scores):,} rated), "
            f"average runtime {mean(group_runtimes):.2f} minutes"
        )
    lines.extend(["", "TOP 10 GENRES BY TITLE COUNT"])
    for genre in sorted(genre_groups, key=lambda name: len(genre_groups[name]), reverse=True)[:10]:
        scores_in_genre = numeric_values(genre_groups[genre], "imdb_score")
        score_text = f", average IMDb {mean(scores_in_genre):.2f}" if scores_in_genre else ""
        lines.append(f"{genre.title()}: {len(genre_groups[genre]):,} titles{score_text}")
    lines.extend(["", "TOP 10 GENRES BY AVERAGE IMDb SCORE (at least 30 rated titles)"])
    for genre, score, count in top_scored_genres:
        lines.append(f"{genre.title()}: {score:.2f} average IMDb score ({count:,} rated titles)")
    lines.extend(["", "TOP 10 TITLES BY IMDb SCORE"])
    for rank, title in enumerate(top_titles, start=1):
        lines.append(f"{rank}. {title['title']} ({title['release_year']}): {title['imdb_score']:.1f}")
    return "\n".join(lines)


def main():
    CHART_DIR.mkdir(exist_ok=True)
    titles, cleaning = load_titles(DATA_FILE)
    type_groups = group_titles(titles, "type")
    genre_groups = make_genre_groups(titles)

    write_chart_type_counts(type_groups)
    write_chart_genre_counts(genre_groups)
    top_scored_genres = write_chart_genre_scores(genre_groups)

    summary = format_summary(titles, cleaning, type_groups, genre_groups, top_scored_genres)
    SUMMARY_FILE.write_text(summary, encoding="utf-8")
    print(summary)
    if plt is None:
        print("\nMatplotlib is not installed, so the text analysis was saved without PNG charts.")
        print("Install it with: python3 -m pip install matplotlib")
    else:
        print(f"\nSaved charts to: {CHART_DIR}")


if __name__ == "__main__":
    main()
