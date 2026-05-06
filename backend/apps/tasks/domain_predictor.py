"""
ML-based domain predictor for student career/domain recommendations.

Architecture:
  - Feature vector: 13 dims
      [0:10]  domain MCQ scores (0-100), one per domain in DOMAINS order
      [10]    overall task completion rate (0-1)
      [11]    improvement trend (normalised slope of last-5 attempt scores, -1..1)
      [12]    average task MCQ score from TaskMCQAttempt (0-100)

  - Model: RandomForestClassifier (explainable via feature_importances_)
  - Label: domain with highest MCQ assessment score for that student
  - Fallback: heuristic recency-weighted softmax (existing DomainPredictor)

Storage (relative to this file's parent → backend/ml_models/):
  domain_predictor.pkl      trained model
  domain_predictor_meta.json  accuracy, date, feature names
"""

import json
import logging
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────────

DOMAINS: List[str] = [
    'Graphic Design', 'Content Writing', 'Programming', 'Freelancing',
    'E-Commerce', 'QuickBooks', 'AutoCAD', 'Data Analytics',
    'Digital Marketing', 'WordPress',
]
DOMAIN_INDEX: Dict[str, int] = {d: i for i, d in enumerate(DOMAINS)}
N_DOMAINS = len(DOMAINS)

FEATURE_NAMES: List[str] = (
    [f'score_{d.replace(" ", "_")}' for d in DOMAINS]
    + ['completion_rate', 'improvement_trend', 'avg_task_mcq_score']
)
N_FEATURES = N_DOMAINS + 3

# ── Model storage ─────────────────────────────────────────────────────────────

# backend/ml_models/
_ML_DIR   = Path(__file__).resolve().parent.parent.parent / 'ml_models'
MODEL_PATH = _ML_DIR / 'domain_predictor.pkl'
META_PATH  = _ML_DIR / 'domain_predictor_meta.json'


# ── Feature extraction ────────────────────────────────────────────────────────

def extract_student_features(student) -> np.ndarray:
    """
    Build the 13-dim feature vector for *student* (a User instance).

    Uses single-collection queries + Python iteration; safe for Djongo/MongoDB.
    """
    from apps.assessments.models import AssessmentAttempt
    from apps.tasks.models import TaskAssignment

    feat = np.zeros(N_FEATURES, dtype=float)

    # ── [0:10] domain MCQ scores (latest per domain) ──────────────────────
    attempts = list(
        AssessmentAttempt.objects.filter(student=student)
        .select_related('assessment')
        .order_by('attempted_at')          # ascending → last entry per domain wins
    )
    domain_latest: Dict[str, float] = {}
    for a in attempts:
        domain_latest[a.assessment.domain] = a.percentage

    for domain, score in domain_latest.items():
        idx = DOMAIN_INDEX.get(domain)
        if idx is not None:
            feat[idx] = float(score)

    # ── [10] completion rate ───────────────────────────────────────────────
    all_assignments = list(
        TaskAssignment.objects.filter(
            student=student,
            status__in=['accepted', 'in_progress', 'completed'],
        )
    )
    total     = len(all_assignments)
    completed = sum(1 for a in all_assignments if a.status == 'completed')
    feat[N_DOMAINS] = completed / max(1, total)

    # ── [11] improvement trend (normalised linear slope) ──────────────────
    if len(attempts) >= 2:
        recent   = np.array([a.percentage for a in attempts[-5:]], dtype=float)
        x        = np.arange(len(recent), dtype=float)
        x       -= x.mean()
        y_vals   = recent - recent.mean()
        denom    = float(np.dot(x, x))
        slope    = float(np.dot(x, y_vals) / denom) if denom > 0 else 0.0
        feat[N_DOMAINS + 1] = float(np.clip(slope / 30.0, -1.0, 1.0))

    # ── [12] avg task MCQ score ────────────────────────────────────────────
    try:
        from apps.tasks.models import TaskCompletion, TaskMCQAttempt
        completion_ids = list(
            TaskCompletion.objects.filter(
                task_assignment__student=student,
                is_submitted=True,
            ).values_list('id', flat=True)
        )
        if completion_ids:
            mcq_attempts = list(
                TaskMCQAttempt.objects.filter(
                    task_completion_id__in=completion_ids,
                    is_submitted=True,
                )
            )
            if mcq_attempts:
                feat[N_DOMAINS + 2] = sum(
                    float(a.mcq_score or 0) for a in mcq_attempts
                ) / len(mcq_attempts)
    except Exception:
        pass

    return feat


# ── Seed data generator ───────────────────────────────────────────────────────

def generate_seed_data(n_per_domain: int = 30) -> Tuple[List[np.ndarray], List[str]]:
    """
    Generate synthetic training samples to bootstrap the model when real
    student data is sparse.

    Each sample is a plausible student profile whose strongest domain equals
    the label.  Generates three archetypes per domain:
      - specialist: one very high domain, others low
      - mid-strength: one high domain, one moderate secondary
      - transitional: two moderate domains, one slightly higher

    Total samples: n_per_domain × 3 per domain.
    """
    rng = np.random.default_rng(seed=42)
    X: List[np.ndarray] = []
    y: List[str]        = []

    for domain_idx, domain in enumerate(DOMAINS):
        for archetype in ('specialist', 'mid_strength', 'transitional'):
            for _ in range(n_per_domain):
                feat = np.zeros(N_FEATURES, dtype=float)

                if archetype == 'specialist':
                    feat[domain_idx] = rng.uniform(72, 100)
                    for j in range(N_DOMAINS):
                        if j != domain_idx:
                            feat[j] = rng.uniform(0, 45)

                elif archetype == 'mid_strength':
                    feat[domain_idx] = rng.uniform(62, 90)
                    secondary = rng.choice(
                        [j for j in range(N_DOMAINS) if j != domain_idx]
                    )
                    feat[secondary] = rng.uniform(40, feat[domain_idx] - 10)
                    for j in range(N_DOMAINS):
                        if j != domain_idx and j != secondary:
                            feat[j] = rng.uniform(0, 40)

                else:  # transitional
                    feat[domain_idx] = rng.uniform(55, 75)
                    secondary = rng.choice(
                        [j for j in range(N_DOMAINS) if j != domain_idx]
                    )
                    feat[secondary] = rng.uniform(45, feat[domain_idx] - 5)
                    for j in range(N_DOMAINS):
                        if j != domain_idx and j != secondary:
                            feat[j] = rng.uniform(0, 35)

                # Task stats
                feat[N_DOMAINS]     = rng.uniform(0.2, 1.0)    # completion_rate
                feat[N_DOMAINS + 1] = rng.uniform(-0.4, 0.6)   # trend
                feat[N_DOMAINS + 2] = rng.uniform(30, 95)      # avg task MCQ score

                X.append(feat)
                y.append(domain)

    return X, y


# ── Helpers ────────────────────────────────────────────────────────────────────

def _score_to_skill_level(score_0_100: float) -> str:
    if score_0_100 >= 75:
        return 'Advanced'
    elif score_0_100 >= 45:
        return 'Intermediate'
    return 'Beginner'


# ── Main predictor class ──────────────────────────────────────────────────────

class DomainPredictorML:
    """
    sklearn RandomForest-based domain predictor.

    Usage:
        result = DomainPredictorML.predict(student_user)
        # → dict with predicted_domain, confidence, distribution, reasons …

    Training:
        from apps.tasks.domain_predictor import DomainPredictorML
        DomainPredictorML.train()
    """

    _model = None   # cached loaded model
    _meta: Optional[Dict] = None

    # ── Model lifecycle ───────────────────────────────────────────────────

    @classmethod
    def _load(cls) -> bool:
        """Load model from disk into class cache. Returns True on success."""
        if cls._model is not None:
            return True
        if not MODEL_PATH.exists():
            return False
        try:
            import joblib
            cls._model = joblib.load(MODEL_PATH)
            if META_PATH.exists():
                with open(META_PATH) as f:
                    cls._meta = json.load(f)
            return True
        except Exception as e:
            logger.warning("Could not load domain predictor model: %s", e)
            return False

    @classmethod
    def is_trained(cls) -> bool:
        return MODEL_PATH.exists()

    @classmethod
    def invalidate_cache(cls) -> None:
        cls._model = None
        cls._meta  = None

    # ── Public predict ────────────────────────────────────────────────────

    @classmethod
    def predict(cls, student) -> Dict:
        """
        Predict the most suitable freelancing domain(s) for *student*.

        Returns:
        {
          'predicted_domain':  str | None,
          'confidence':        float,          # 0-1 probability of top domain
          'distribution': [
            {domain, probability, score_basis, skill_level}, …
          ],
          'secondary_domains': [str, …],       # 2nd and 3rd predictions
          'key_features': [
            {feature, importance, value}, …
          ],
          'reasons':           [str, …],
          'method':            'ml' | 'heuristic',
          'model_accuracy':    float | None,   # training-set accuracy
        }
        """
        if cls._load():
            try:
                return cls._predict_ml(student)
            except Exception as e:
                logger.warning("ML prediction failed, falling back to heuristic: %s", e)

        return cls._predict_heuristic(student)

    # ── ML prediction ─────────────────────────────────────────────────────

    @classmethod
    def _predict_ml(cls, student) -> Dict:
        feat    = extract_student_features(student)
        feat_2d = feat.reshape(1, -1)

        probs   = cls._model.predict_proba(feat_2d)[0]
        classes = cls._model.classes_  # string domain names

        # Build probability map
        prob_map: Dict[str, float] = {
            str(cls_label): float(p)
            for cls_label, p in zip(classes, probs)
        }

        sorted_items = sorted(prob_map.items(), key=lambda x: x[1], reverse=True)
        top_domain, top_conf = sorted_items[0]
        secondary = [d for d, _ in sorted_items[1:4]]

        # Feature importances — top 5 by importance weight
        importances = cls._model.feature_importances_
        ranked = sorted(
            zip(FEATURE_NAMES, importances, feat),
            key=lambda t: t[1],
            reverse=True,
        )[:5]
        key_features = [
            {
                'feature':    fn,
                'importance': round(float(imp), 4),
                'value':      round(float(val), 1),
            }
            for fn, imp, val in ranked
            if imp > 0.01
        ]

        reasons = cls._build_reasons(top_domain, feat, top_conf)

        distribution = [
            {
                'domain':      domain,
                'probability': round(prob, 4),
                'score_basis': round(
                    feat[DOMAIN_INDEX[domain]] if domain in DOMAIN_INDEX else 0.0, 1
                ),
                'skill_level': _score_to_skill_level(
                    feat[DOMAIN_INDEX[domain]] if domain in DOMAIN_INDEX else 0.0
                ),
            }
            for domain, prob in sorted_items
            if prob > 0.005
        ]

        return {
            'predicted_domain':  top_domain,
            'confidence':        round(top_conf, 4),
            'distribution':      distribution,
            'secondary_domains': secondary,
            'key_features':      key_features,
            'reasons':           reasons,
            'method':            'ml',
            'model_accuracy':    cls._meta.get('accuracy') if cls._meta else None,
        }

    # ── Heuristic fallback ────────────────────────────────────────────────

    @classmethod
    def _predict_heuristic(cls, student) -> Dict:
        """Delegate to the existing recency-weighted DomainPredictor."""
        from apps.tasks.ml_engine import DomainPredictor

        results = DomainPredictor.predict(student)

        if not results:
            return {
                'predicted_domain':  None,
                'confidence':        0.0,
                'distribution':      [],
                'secondary_domains': [],
                'key_features':      [],
                'reasons':           ['Take domain assessments to get personalised predictions.'],
                'method':            'heuristic',
                'model_accuracy':    None,
            }

        top       = results[0]
        secondary = [r['domain'] for r in results[1:4]]

        return {
            'predicted_domain':  top['domain'],
            'confidence':        top['confidence'],
            'distribution': [
                {
                    'domain':      r['domain'],
                    'probability': r['confidence'],
                    'score_basis': r['score_basis'],
                    'skill_level': r['skill_level'],
                }
                for r in results
            ],
            'secondary_domains': secondary,
            'key_features':      [],
            'reasons':           [r['reasoning'] for r in results[:3]],
            'method':            'heuristic',
            'model_accuracy':    None,
        }

    # ── Reason builder ────────────────────────────────────────────────────

    @classmethod
    def _build_reasons(cls, top_domain: str, feat: np.ndarray, confidence: float) -> List[str]:
        reasons = []

        domain_idx = DOMAIN_INDEX.get(top_domain)
        if domain_idx is not None:
            score = feat[domain_idx]
            if score >= 75:
                reasons.append(
                    f"Strong {top_domain} MCQ score ({score:.0f}%) — you're ready to freelance."
                )
            elif score >= 45:
                reasons.append(
                    f"Solid {top_domain} foundation ({score:.0f}%) with room to grow."
                )
            elif score > 0:
                reasons.append(
                    f"Early {top_domain} engagement ({score:.0f}%) — keep practising."
                )

        completion = feat[N_DOMAINS]
        if completion >= 0.7:
            reasons.append(
                f"Excellent task completion rate ({completion * 100:.0f}%) shows dedication."
            )
        elif completion >= 0.4:
            reasons.append(
                f"Good task completion rate ({completion * 100:.0f}%)."
            )

        trend = feat[N_DOMAINS + 1]
        if trend > 0.15:
            reasons.append("Your assessment scores are on an upward trend.")
        elif trend < -0.15:
            reasons.append("Recent scores dipped — revisit weaker concepts.")

        if confidence >= 0.55:
            reasons.append(
                f"Model is {confidence * 100:.0f}% confident in this recommendation."
            )
        else:
            reasons.append(
                f"Moderate confidence ({confidence * 100:.0f}%) — more domain assessments will sharpen this."
            )

        return reasons[:4]

    # ── Training ──────────────────────────────────────────────────────────

    @classmethod
    def train(cls, include_seed: bool = True) -> Dict:
        """
        Train (or retrain) the RandomForest from DB data + optional seed data.

        Returns:
            {accuracy, n_samples, n_real, n_seed, trained_at, model_path}

        Raises:
            RuntimeError if sklearn/joblib are not installed or data is too sparse.
        """
        try:
            import joblib
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import accuracy_score
            from collections import Counter
            from datetime import datetime, timezone as dt_tz
        except ImportError as exc:
            raise RuntimeError(
                "scikit-learn and joblib are required: pip install scikit-learn joblib"
            ) from exc

        X_all, y_all = cls._build_training_data(include_seed=include_seed)

        if len(X_all) < 10:
            raise RuntimeError(
                f"Only {len(X_all)} training samples found. "
                "Need ≥ 10. Run with include_seed=True or add student data."
            )

        n_real_approx = sum(
            1 for _ in X_all
        )  # actual split is done below — rough count available in meta

        X = np.array(X_all)
        y = list(y_all)

        # Stratified split only if every class has ≥ 2 samples
        label_counts = Counter(y)
        can_stratify = len(X) >= 20 and all(c >= 2 for c in label_counts.values())

        if can_stratify:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
        else:
            X_train, X_test = X, X
            y_train, y_test = y, y

        model = RandomForestClassifier(
            n_estimators=150,
            max_depth=10,
            min_samples_leaf=2,
            random_state=42,
            class_weight='balanced',
        )
        model.fit(X_train, y_train)

        accuracy = float(accuracy_score(y_test, model.predict(X_test)))

        # Persist
        _ML_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, MODEL_PATH)

        meta = {
            'accuracy':      round(accuracy, 4),
            'n_samples':     len(X),
            'feature_names': FEATURE_NAMES,
            'domains':       DOMAINS,
            'trained_at':    datetime.now(dt_tz.utc).isoformat(),
        }
        with open(META_PATH, 'w') as f:
            json.dump(meta, f, indent=2)

        cls.invalidate_cache()

        return {
            'accuracy':   round(accuracy, 4),
            'n_samples':  len(X),
            'trained_at': meta['trained_at'],
            'model_path': str(MODEL_PATH),
        }

    @classmethod
    def _build_training_data(
        cls, include_seed: bool = True
    ) -> Tuple[List[np.ndarray], List[str]]:
        """
        Collect feature vectors + labels from three sources (priority order):

        1. Real student records from the PostgreSQL database
        2. Curated CSV dataset (student_performance.csv) — 500 rows based on
           Upwork/Freelancer.com market statistics 2024
        3. Programmatically generated synthetic seed data (when include_seed=True)
        """
        from apps.accounts.models import User

        X: List[np.ndarray] = []
        y: List[str]        = []

        # ── Source 1: Real students from DB ───────────────────────────────
        n_real = 0
        for student in User.objects.filter(role='Student').iterator():
            feat = extract_student_features(student)
            domain_vec = feat[:N_DOMAINS]
            if not np.any(domain_vec > 0):
                continue
            label = DOMAINS[int(np.argmax(domain_vec))]
            X.append(feat)
            y.append(label)
            n_real += 1

        # ── Source 2: CSV dataset (student_performance.csv) ───────────────
        try:
            from apps.tasks.dataset_loader import load_student_performance
            X_csv, y_csv = load_student_performance()
            X.extend(X_csv)
            y.extend(y_csv)
            logger.info(
                "Training data: %d real students + %d CSV samples loaded",
                n_real, len(X_csv),
            )
        except Exception as exc:
            logger.warning("Could not load CSV dataset: %s", exc)

        # ── Source 3: Synthetic seed data ─────────────────────────────────
        if include_seed:
            X_seed, y_seed = generate_seed_data()
            X.extend(X_seed)
            y.extend(y_seed)

        return X, y
