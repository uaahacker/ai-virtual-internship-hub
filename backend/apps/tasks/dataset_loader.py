"""
Dataset loader for VIHub AI modules.

Loads three curated CSV datasets from backend/datasets/ and transforms them
into the numpy arrays expected by the ML training pipeline.

Datasets
--------
student_performance.csv
    500 student skill profiles modelled on Upwork/Freelancer.com market
    statistics (2024).  Used to supplement synthetic seed data when training
    the RandomForest domain predictor.

freelancer_skills.csv
    74 freelancer job-skill mappings curated from Kaggle "Freelancer Job
    Postings 2024" and Upwork Skills Index 2024.  Used by the content-based
    recommendation engine to enrich task-skill similarity scoring.

text_quality_samples.csv
    50 annotated writing samples with ground-truth Flesch Reading-Ease scores
    and quality labels (based on Grammarly Blog benchmarks).  Used to
    validate/calibrate the NLP evaluation thresholds in evaluation_service.py.
"""

import csv
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# backend/datasets/
DATASETS_DIR = Path(__file__).resolve().parent.parent.parent / "datasets"

DOMAINS = [
    "Graphic Design", "Content Writing", "Programming", "Freelancing",
    "E-Commerce", "QuickBooks", "AutoCAD", "Data Analytics",
    "Digital Marketing", "WordPress",
]
N_DOMAINS = len(DOMAINS)
N_FEATURES = N_DOMAINS + 3  # matches domain_predictor.py


# ─────────────────────────────────────────────────────────────────────────────
# student_performance.csv → RandomForest training vectors
# ─────────────────────────────────────────────────────────────────────────────

def load_student_performance() -> Tuple[List[np.ndarray], List[str]]:
    """
    Load student_performance.csv and return (X, y) in the same format
    as domain_predictor.generate_seed_data().

    Returns
    -------
    X : list of np.ndarray, shape (N_FEATURES,)
    y : list of str  (domain label)
    """
    csv_path = DATASETS_DIR / "student_performance.csv"
    if not csv_path.exists():
        logger.warning("student_performance.csv not found at %s — skipping CSV dataset", csv_path)
        return [], []

    X: List[np.ndarray] = []
    y: List[str] = []
    skipped = 0

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                feat = np.zeros(N_FEATURES, dtype=float)
                # [0:10] domain MCQ scores
                for i, domain in enumerate(DOMAINS):
                    feat[i] = float(row.get(domain, 0) or 0)
                # [10] completion_rate
                feat[N_DOMAINS] = float(row.get("completion_rate", 0) or 0)
                # [11] improvement_trend
                feat[N_DOMAINS + 1] = float(row.get("improvement_trend", 0) or 0)
                # [12] avg_mcq_score
                feat[N_DOMAINS + 2] = float(row.get("avg_mcq_score", 0) or 0)
                label = str(row.get("recommended_domain", "")).strip()
                if label not in DOMAINS:
                    skipped += 1
                    continue
                X.append(feat)
                y.append(label)
            except (ValueError, KeyError) as exc:
                logger.debug("Skipping malformed row: %s", exc)
                skipped += 1

    logger.info(
        "Loaded %d student performance samples from CSV (%d skipped)",
        len(X), skipped,
    )
    return X, y


# ─────────────────────────────────────────────────────────────────────────────
# freelancer_skills.csv → skill-domain mapping dict
# ─────────────────────────────────────────────────────────────────────────────

def load_freelancer_skills() -> List[Dict]:
    """
    Load freelancer_skills.csv.

    Returns a list of dicts with keys:
        job_title, primary_domain, secondary_domain,
        skills (list[str]), avg_hourly_rate_usd (float),
        experience_level, demand_score (int), task_type
    """
    csv_path = DATASETS_DIR / "freelancer_skills.csv"
    if not csv_path.exists():
        logger.warning("freelancer_skills.csv not found at %s", csv_path)
        return []

    jobs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            skills = [
                row.get("skill_1", ""), row.get("skill_2", ""),
                row.get("skill_3", ""), row.get("skill_4", ""),
            ]
            skills = [s.strip() for s in skills if s and s.strip()]
            try:
                jobs.append({
                    "job_title":          row.get("job_title", ""),
                    "primary_domain":     row.get("primary_domain", ""),
                    "secondary_domain":   row.get("secondary_domain", ""),
                    "skills":             skills,
                    "avg_hourly_rate_usd": float(row.get("avg_hourly_rate_usd", 0) or 0),
                    "experience_level":   row.get("experience_level", "Beginner"),
                    "demand_score":       int(float(row.get("demand_score", 5) or 5)),
                    "task_type":          row.get("task_type", ""),
                })
            except (ValueError, KeyError) as exc:
                logger.debug("Skipping malformed freelancer row: %s", exc)

    logger.info("Loaded %d freelancer job profiles from CSV", len(jobs))
    return jobs


def get_domain_skill_weights() -> Dict[str, Dict[str, float]]:
    """
    Derive skill → domain relevance weights from the freelancer skills CSV.

    Returns: { domain: { skill: weight (0-1) } }
    Used to enrich the content-based recommendation engine.
    """
    jobs = load_freelancer_skills()
    if not jobs:
        return {}

    # Count skill occurrences per domain (primary domain gets full weight,
    # secondary gets 0.5 weight)
    raw: Dict[str, Dict[str, float]] = {d: {} for d in DOMAINS}

    for job in jobs:
        primary = job["primary_domain"]
        secondary = job["secondary_domain"]
        demand = job["demand_score"] / 10.0  # normalise to 0-1

        for skill in job["skills"]:
            if not skill:
                continue
            if primary in raw:
                raw[primary][skill] = raw[primary].get(skill, 0.0) + demand
            if secondary in raw:
                raw[secondary][skill] = raw[secondary].get(skill, 0.0) + demand * 0.5

    # Normalise each domain's skill weights to 0-1
    result: Dict[str, Dict[str, float]] = {}
    for domain, skill_counts in raw.items():
        if not skill_counts:
            result[domain] = {}
            continue
        max_val = max(skill_counts.values())
        result[domain] = {
            skill: round(count / max_val, 4)
            for skill, count in sorted(skill_counts.items(), key=lambda x: -x[1])
        }

    return result


# ─────────────────────────────────────────────────────────────────────────────
# text_quality_samples.csv → NLP calibration data
# ─────────────────────────────────────────────────────────────────────────────

def load_text_quality_samples() -> List[Dict]:
    """
    Load text_quality_samples.csv.

    Returns a list of dicts with keys:
        sample_id (int), text_excerpt (str), word_count (int),
        approx_flesch_score (float), grammar_issues (int),
        vocabulary_diversity_pct (float), quality_label (str)
    """
    csv_path = DATASETS_DIR / "text_quality_samples.csv"
    if not csv_path.exists():
        logger.warning("text_quality_samples.csv not found at %s", csv_path)
        return []

    samples = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                samples.append({
                    "sample_id":              int(row["sample_id"]),
                    "text_excerpt":           row["text_excerpt"],
                    "word_count":             int(row["word_count"]),
                    "approx_flesch_score":    float(row["approx_flesch_score"]),
                    "grammar_issues":         int(row["grammar_issues"]),
                    "vocabulary_diversity_pct": float(row["vocabulary_diversity_pct"]),
                    "quality_label":          row["quality_label"],
                })
            except (ValueError, KeyError) as exc:
                logger.debug("Skipping malformed text sample row: %s", exc)

    logger.info("Loaded %d text quality samples from CSV", len(samples))
    return samples


def get_quality_threshold_stats() -> Dict[str, Dict[str, float]]:
    """
    Compute mean Flesch score and vocabulary diversity per quality label
    from the dataset.  Used to validate evaluation_service.py thresholds.

    Returns:
        {
          'Needs Work':   { 'flesch_mean': ..., 'vocab_mean': ..., 'n': ... },
          'Satisfactory': { ... },
          'Good':         { ... },
          'Excellent':    { ... },
        }
    """
    samples = load_text_quality_samples()
    if not samples:
        return {}

    buckets: Dict[str, list] = {}
    for s in samples:
        label = s["quality_label"]
        buckets.setdefault(label, []).append(s)

    stats = {}
    for label, items in buckets.items():
        stats[label] = {
            "flesch_mean": round(sum(i["approx_flesch_score"] for i in items) / len(items), 1),
            "vocab_mean":  round(sum(i["vocabulary_diversity_pct"] for i in items) / len(items), 1),
            "n":           len(items),
        }
    return stats
