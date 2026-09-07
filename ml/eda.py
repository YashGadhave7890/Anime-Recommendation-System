"""
Exploratory Data Analysis (EDA) module for ANIMORA.
Generates comprehensive statistical summaries, metrics, and publication-ready
visualizations saved in docs/figures/.
"""

import ast
from collections import Counter
from pathlib import Path
from typing import Any, Dict
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless execution
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from ml.config import (
    DOCS_DIR,
    EDA_METRICS_PATH,
    FIGURES_DIR,
    PROCESSED_PARQUET_PATH,
    PROCESSED_CSV_PATH,
)
from ml.utils import save_json, setup_logger

logger = setup_logger("EDA")

# Styling configurations for portfolio-grade visuals
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
PALETTE = sns.color_palette("mako")
ACCENT_COLOR = "#6C5CE7"
SECONDARY_COLOR = "#00CEC9"
FONT_FAMILY = "sans-serif"
plt.rcParams.update({
    "font.sans-serif": "DejaVu Sans",
    "axes.edgecolor": "#CCCCCC",
    "axes.linewidth": 0.8,
    "grid.color": "#EAEAEA",
    "grid.linestyle": "--",
    "grid.alpha": 0.7,
})


def load_processed_data() -> pd.DataFrame:
    """Loads processed dataset from parquet (or CSV fallback)."""
    if PROCESSED_PARQUET_PATH.exists():
        logger.info(f"Loading processed dataset from parquet: {PROCESSED_PARQUET_PATH}")
        df = pd.read_parquet(PROCESSED_PARQUET_PATH)
    else:
        logger.info(f"Loading processed dataset from CSV: {PROCESSED_CSV_PATH}")
        df = pd.read_csv(PROCESSED_CSV_PATH)
    return df


def plot_missing_values(df: pd.DataFrame, output_path: Path) -> Dict[str, Any]:
    """Analyzes and plots missing value counts and percentages."""
    logger.info("Plotting missing values distribution...")
    missing = df.isna().sum()
    missing = missing[missing > 0].sort_values(ascending=False)

    if missing.empty:
        logger.info("No missing values found in processed dataset.")
        return {}

    pct = (missing / len(df)) * 100

    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    bars = ax.barh(missing.index, pct.values, color=PALETTE[2], edgecolor="#2D3436", alpha=0.85)
    
    # Add data labels
    for bar, count in zip(bars, missing.values):
        ax.text(
            bar.get_width() + 0.5,
            bar.get_y() + bar.get_height() / 2,
            f"{count:,} ({bar.get_width():.1f}%)",
            va="center",
            ha="left",
            fontsize=9,
            color="#2D3436",
            fontweight="bold",
        )

    ax.set_xlabel("Missing Percentage (%)", fontsize=11, fontweight="bold")
    ax.set_title("Missing Values by Feature in ANIMORA Dataset", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlim(0, max(pct.values) * 1.25)
    plt.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved: {output_path.name}")

    return {k: {"count": int(v), "pct": round(float(p), 2)} for k, v, p in zip(missing.index, missing.values, pct.values)}


def plot_rating_distributions(df: pd.DataFrame, output_path: Path) -> Dict[str, Any]:
    """Compares raw score vs Bayesian weighted score distributions."""
    logger.info("Plotting rating distributions...")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), dpi=300)

    # 1. Raw Score
    valid_scores = df["score"].dropna()
    mean_score = valid_scores.mean()
    median_score = valid_scores.median()

    sns.histplot(valid_scores, bins=35, kde=True, ax=axes[0], color=ACCENT_COLOR, edgecolor="#2D3436", alpha=0.6)
    axes[0].axvline(mean_score, color="#D63031", linestyle="--", linewidth=1.5, label=f"Mean: {mean_score:.2f}")
    axes[0].axvline(median_score, color="#00B894", linestyle=":", linewidth=1.8, label=f"Median: {median_score:.2f}")
    axes[0].set_title("Raw Score Distribution (Rated Anime)", fontsize=12, fontweight="bold")
    axes[0].set_xlabel("MAL Score (1 - 10)", fontsize=10)
    axes[0].set_ylabel("Anime Count", fontsize=10)
    axes[0].legend(frameon=True, facecolor="white")

    # 2. Bayesian Weighted Score
    valid_weighted = df["weighted_score"].dropna()
    mean_w = valid_weighted.mean()
    median_w = valid_weighted.median()

    sns.histplot(valid_weighted, bins=35, kde=True, ax=axes[1], color=SECONDARY_COLOR, edgecolor="#2D3436", alpha=0.6)
    axes[1].axvline(mean_w, color="#D63031", linestyle="--", linewidth=1.5, label=f"Mean: {mean_w:.2f}")
    axes[1].axvline(median_w, color="#00B894", linestyle=":", linewidth=1.8, label=f"Median: {median_w:.2f}")
    axes[1].set_title("Bayesian Weighted Score Distribution (All Anime)", fontsize=12, fontweight="bold")
    axes[1].set_xlabel("Weighted Score (Regularized)", fontsize=10)
    axes[1].set_ylabel("Anime Count", fontsize=10)
    axes[1].legend(frameon=True, facecolor="white")

    plt.suptitle("ANIMORA — Rating Distribution: Raw Score vs. Bayesian Weighted Score", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved: {output_path.name}")

    return {
        "raw_score_mean": round(float(mean_score), 2),
        "raw_score_median": round(float(median_score), 2),
        "raw_score_std": round(float(valid_scores.std()), 2),
        "weighted_score_mean": round(float(mean_w), 2),
        "weighted_score_median": round(float(median_w), 2),
        "weighted_score_std": round(float(valid_weighted.std()), 2),
    }


def plot_popularity_distribution(df: pd.DataFrame, output_path: Path) -> Dict[str, Any]:
    """Plots raw members vs log-transformed members distribution."""
    logger.info("Plotting popularity & member distributions...")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), dpi=300)

    # 1. Raw Members
    sns.histplot(df["members"], bins=40, ax=axes[0], color="#E17055", edgecolor="#2D3436", alpha=0.7)
    axes[0].set_title("Raw Member Distribution (Heavy Right Skew)", fontsize=12, fontweight="bold")
    axes[0].set_xlabel("Number of Members (Community Size)", fontsize=10)
    axes[0].set_ylabel("Anime Count", fontsize=10)

    # 2. Log-Transformed Members
    sns.histplot(df["log_members"], bins=40, kde=True, ax=axes[1], color="#0984E3", edgecolor="#2D3436", alpha=0.6)
    axes[1].set_title("Log-Transformed Members (Normalized Scale)", fontsize=12, fontweight="bold")
    axes[1].set_xlabel("log1p(Members)", fontsize=10)
    axes[1].set_ylabel("Anime Count", fontsize=10)

    plt.suptitle("ANIMORA — Community Popularity: Raw vs. Log-Transformed Members", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved: {output_path.name}")

    return {
        "members_max": int(df["members"].max()),
        "members_median": float(df["members"].median()),
        "members_mean": float(df["members"].mean()),
        "members_skewness": round(float(df["members"].skew()), 2),
        "log_members_skewness": round(float(df["log_members"].skew()), 2),
    }


def plot_genre_frequencies(df: pd.DataFrame, output_path: Path, top_n: int = 25) -> Dict[str, int]:
    """Extracts all genres, counts frequencies, and plots horizontal bar chart."""
    logger.info("Plotting genre frequencies...")
    all_genres = []
    for g_val in df["genres"]:
        if pd.notna(g_val) and str(g_val).strip():
            items = [item.strip() for item in str(g_val).split(",") if item.strip()]
            all_genres.extend(items)

    genre_counts = Counter(all_genres)
    top_genres = dict(genre_counts.most_common(top_n))

    fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
    colors = sns.color_palette("viridis", len(top_genres))[::-1]
    y_pos = np.arange(len(top_genres))
    bars = ax.barh(y_pos, list(top_genres.values())[::-1], color=colors, edgecolor="#2D3436", alpha=0.85)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(list(top_genres.keys())[::-1], fontsize=10)
    ax.set_xlabel("Number of Anime Titles", fontsize=11, fontweight="bold")
    ax.set_title(f"Top {top_n} Most Frequent Anime Genres in ANIMORA", fontsize=13, fontweight="bold", pad=12)

    # Value labels
    for bar in bars:
        ax.text(
            bar.get_width() + 50,
            bar.get_y() + bar.get_height() / 2,
            f"{int(bar.get_width()):,}",
            va="center",
            ha="left",
            fontsize=8.5,
            color="#2D3436",
        )

    ax.set_xlim(0, max(top_genres.values()) * 1.12)
    plt.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved: {output_path.name}")

    return top_genres


def plot_type_distribution(df: pd.DataFrame, output_path: Path) -> Dict[str, int]:
    """Plots anime format types (TV, Movie, OVA, Special, ONA, Music)."""
    logger.info("Plotting anime type distribution...")
    type_counts = df["type"].value_counts()

    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    colors = sns.color_palette("Set2", len(type_counts))
    bars = ax.bar(type_counts.index, type_counts.values, color=colors, edgecolor="#2D3436", alpha=0.85, width=0.55)

    for bar, count in zip(bars, type_counts.values):
        pct = (count / len(df)) * 100
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 80,
            f"{count:,}\n({pct:.1f}%)",
            va="bottom",
            ha="center",
            fontsize=9.5,
            fontweight="bold",
        )

    ax.set_ylabel("Anime Count", fontsize=11, fontweight="bold")
    ax.set_title("Distribution of Anime Production Formats", fontsize=13, fontweight="bold", pad=14)
    ax.set_ylim(0, max(type_counts.values) * 1.18)
    plt.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved: {output_path.name}")

    return type_counts.to_dict()


def plot_episode_distribution(df: pd.DataFrame, output_path: Path) -> Dict[str, Any]:
    """Analyzes episode count distribution, highlighting typical broadcast cour formats."""
    logger.info("Plotting episode count distribution...")
    valid_ep = df["episodes"].dropna()
    # Filter to television / series for clear display (<= 52 episodes)
    series_ep = valid_ep[(valid_ep >= 1) & (valid_ep <= 52)]

    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    sns.histplot(series_ep, bins=52, ax=ax, color="#6C5CE7", edgecolor="#2D3436", alpha=0.7)

    # Highlight common cour counts: 1 (movie/ova), 12 (1-cour), 24-26 (2-cour)
    ax.annotate(
        "1 Episode\n(Movies & Specials)",
        xy=(1, series_ep[series_ep == 1].count()),
        xytext=(4, series_ep[series_ep == 1].count() * 0.85),
        arrowprops=dict(facecolor="#D63031", shrink=0.05, width=1, headwidth=6),
        fontsize=9,
        fontweight="bold",
        color="#D63031",
    )
    ax.annotate(
        "12 Episodes\n(1-Cour Standard)",
        xy=(12, series_ep[series_ep == 12].count()),
        xytext=(15, series_ep[series_ep == 12].count() * 1.05),
        arrowprops=dict(facecolor="#0984E3", shrink=0.05, width=1, headwidth=6),
        fontsize=9,
        fontweight="bold",
        color="#0984E3",
    )
    ax.annotate(
        "24-26 Episodes\n(2-Cour Standard)",
        xy=(25, series_ep[(series_ep >= 24) & (series_ep <= 26)].count() / 3),
        xytext=(28, series_ep[(series_ep >= 24) & (series_ep <= 26)].count() / 3 + 300),
        arrowprops=dict(facecolor="#00B894", shrink=0.05, width=1, headwidth=6),
        fontsize=9,
        fontweight="bold",
        color="#00B894",
    )

    ax.set_xlabel("Episode Count (Zoomed 1 - 52)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Anime Count", fontsize=11, fontweight="bold")
    ax.set_title("Episode Count Distribution (Standard Broadcast Cours)", fontsize=13, fontweight="bold", pad=12)
    plt.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved: {output_path.name}")

    return {
        "episodes_median": float(valid_ep.median()),
        "episodes_mean": round(float(valid_ep.mean()), 2),
        "episodes_max": int(valid_ep.max()),
        "single_episode_count": int((valid_ep == 1).sum()),
        "twelve_episode_count": int((valid_ep == 12).sum()),
    }


def plot_release_year_trend(df: pd.DataFrame, output_path: Path) -> Dict[str, Any]:
    """Plots timeline of anime releases by year from 1970 to present."""
    logger.info("Plotting release year timeline...")
    years = df["release_year"].dropna()
    years = years[(years >= 1970) & (years <= 2022)]
    year_counts = years.value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(12, 5), dpi=300)
    ax.fill_between(year_counts.index, year_counts.values, color="#00CEC9", alpha=0.3)
    ax.plot(year_counts.index, year_counts.values, color="#0984E3", linewidth=2.5, marker="o", markersize=3)

    peak_year = year_counts.idxmax()
    peak_count = year_counts.max()
    ax.annotate(
        f"Peak Production: {peak_year}\n({peak_count:,} titles)",
        xy=(peak_year, peak_count),
        xytext=(peak_year - 10, peak_count - 100),
        arrowprops=dict(facecolor="#D63031", shrink=0.05, width=1.2, headwidth=6),
        fontsize=9.5,
        fontweight="bold",
        color="#D63031",
    )

    ax.set_xlabel("Release Year", fontsize=11, fontweight="bold")
    ax.set_ylabel("Number of Anime Released", fontsize=11, fontweight="bold")
    ax.set_title("Historical Growth of Anime Releases (1970 – 2022)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlim(1970, 2022)
    plt.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved: {output_path.name}")

    return {
        "peak_year": int(peak_year),
        "peak_count": int(peak_count),
        "year_min_analyzed": 1970,
        "year_max_analyzed": 2022,
    }


def plot_correlation_matrix(df: pd.DataFrame, output_path: Path) -> Dict[str, Any]:
    """Plots heatmap of correlations between key numerical features."""
    logger.info("Plotting numerical correlation matrix...")
    num_cols = [
        "score",
        "weighted_score",
        "members",
        "log_members",
        "favorites",
        "log_favorites",
        "episodes",
        "release_year",
    ]
    sub_df = df[num_cols].dropna().astype(float)
    corr = sub_df.corr().round(2)

    fig, ax = plt.subplots(figsize=(9, 7), dpi=300)
    cmap = sns.diverging_palette(220, 10, as_cmap=True)
    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap=cmap,
        vmin=-1,
        vmax=1,
        square=True,
        linewidths=0.5,
        cbar_kws={"shrink": 0.8},
        ax=ax,
    )

    ax.set_title("Correlation Matrix of Key Numerical Features", fontsize=13, fontweight="bold", pad=14)
    plt.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved: {output_path.name}")

    return corr.to_dict()


def plot_score_vs_popularity(df: pd.DataFrame, output_path: Path) -> None:
    """Plots scatter / 2D density of score vs log_members."""
    logger.info("Plotting score vs. popularity relationship...")
    sub_df = df[["score", "log_members", "type"]].dropna()

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    # Hexbin for density
    hb = ax.hexbin(
        sub_df["log_members"],
        sub_df["score"],
        gridsize=35,
        cmap="mako_r",
        mincnt=1,
        bins="log",
    )
    cb = fig.colorbar(hb, ax=ax)
    cb.set_label("log10(Anime Count in Bin)", fontsize=10)

    # Trendline
    z = np.polyfit(sub_df["log_members"], sub_df["score"], 1)
    p = np.poly1d(z)
    x_vals = np.linspace(sub_df["log_members"].min(), sub_df["log_members"].max(), 100)
    ax.plot(x_vals, p(x_vals), color="#FF7675", linewidth=2.5, linestyle="--", label=f"Trendline (Slope: +{z[0]:.2f})")

    ax.set_xlabel("log1p(Members) [Popularity Proxy]", fontsize=11, fontweight="bold")
    ax.set_ylabel("MAL Score (Rating)", fontsize=11, fontweight="bold")
    ax.set_title("Relationship Between Anime Popularity and User Rating", fontsize=13, fontweight="bold", pad=12)
    ax.legend(loc="upper left", frameon=True, facecolor="white")
    plt.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved: {output_path.name}")


def run_eda_pipeline() -> Dict[str, Any]:
    """Executes full EDA pipeline and saves all figures and metrics."""
    logger.info("Starting ANIMORA Exploratory Data Analysis (EDA)...")
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    df = load_processed_data()

    logger.info(f"Loaded dataset for EDA: {len(df):,} rows, {len(df.columns)} columns.")

    metrics = {
        "dataset_size": {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "memory_usage_mb": round(df.memory_usage(deep=True).sum() / 1024**2, 2),
        },
    }

    # Generate figures
    metrics["missing_values"] = plot_missing_values(df, FIGURES_DIR / "01_missing_values.png")
    metrics["ratings"] = plot_rating_distributions(df, FIGURES_DIR / "02_rating_distribution.png")
    metrics["popularity"] = plot_popularity_distribution(df, FIGURES_DIR / "03_popularity_distribution.png")
    metrics["genres"] = plot_genre_frequencies(df, FIGURES_DIR / "04_genre_frequency.png")
    metrics["types"] = plot_type_distribution(df, FIGURES_DIR / "05_type_distribution.png")
    metrics["episodes"] = plot_episode_distribution(df, FIGURES_DIR / "06_episode_distribution.png")
    metrics["release_years"] = plot_release_year_trend(df, FIGURES_DIR / "07_release_year_trend.png")
    metrics["correlations"] = plot_correlation_matrix(df, FIGURES_DIR / "08_correlation_matrix.png")
    plot_score_vs_popularity(df, FIGURES_DIR / "09_score_vs_popularity.png")

    # Save metrics JSON
    save_json(metrics, EDA_METRICS_PATH)
    logger.info(f"EDA metrics saved to {EDA_METRICS_PATH}")
    logger.info(f"All EDA visualizations successfully saved in {FIGURES_DIR}")
    return metrics


if __name__ == "__main__":
    metrics_summary = run_eda_pipeline()
    print("\n--- ANIMORA EDA Complete ---")
    print(f"Total Rows: {metrics_summary['dataset_size']['total_rows']:,}")
    print(f"Total Cols: {metrics_summary['dataset_size']['total_columns']}")
    print(f"Mean Score: {metrics_summary['ratings']['raw_score_mean']}")
    print(f"Top 5 Genres: {list(metrics_summary['genres'].keys())[:5]}")
