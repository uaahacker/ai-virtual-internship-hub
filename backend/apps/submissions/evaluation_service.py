"""
NLP-based evaluation service for text submissions.

Implements FR4: Automated Evaluation for content writing tasks.
Uses only existing deps: nltk, scikit-learn (no new packages needed).

Metrics computed:
  - Readability score  (Flesch Reading Ease – manual formula, no textstat)
  - Vocabulary diversity  (Type-Token Ratio)
  - Content length  (words / sentences)
  - Originality score  (1 – TF-IDF cosine similarity vs other submissions)
  - Overall AI score  (weighted composite 0-100)
"""

import re
import math
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Low-level text helpers
# ---------------------------------------------------------------------------

def _count_syllables(word: str) -> int:
    """Estimate syllables in a word using a vowel-cluster heuristic."""
    word = word.lower().strip(".,;:!?\"'()-")
    if not word:
        return 0
    vowels = "aeiouy"
    count = 0
    prev_vowel = False
    for ch in word:
        is_vowel = ch in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    # Silent trailing 'e'
    if word.endswith('e') and count > 1:
        count -= 1
    return max(count, 1)


def _tokenize_sentences(text: str) -> List[str]:
    """Split text into sentences using basic punctuation rules."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s for s in sentences if s.strip()]


def _tokenize_words(text: str) -> List[str]:
    """Return a list of alphabetic words (lowercased)."""
    return re.findall(r"[a-zA-Z']+", text.lower())


# ---------------------------------------------------------------------------
# Individual metric functions
# ---------------------------------------------------------------------------

def compute_flesch_score(text: str) -> float:
    """
    Flesch Reading Ease = 206.835 - 1.015*(words/sentences) - 84.6*(syllables/words)
    Clamped to [0, 100].  Higher = easier to read.
    """
    sentences = _tokenize_sentences(text)
    words = _tokenize_words(text)
    if not sentences or not words:
        return 0.0
    n_sent = len(sentences)
    n_words = len(words)
    n_syl = sum(_count_syllables(w) for w in words)
    score = 206.835 - 1.015 * (n_words / n_sent) - 84.6 * (n_syl / n_words)
    return round(max(0.0, min(100.0, score)), 2)


def compute_vocabulary_diversity(text: str) -> float:
    """
    Type-Token Ratio (TTR) = unique_words / total_words * 100.
    Indicates richness of vocabulary.
    """
    words = _tokenize_words(text)
    if not words:
        return 0.0
    ttr = len(set(words)) / len(words) * 100
    return round(ttr, 2)


def compute_content_length_score(text: str) -> dict:
    """Returns word count, sentence count, and a length-adequacy score (0-100)."""
    words = _tokenize_words(text)
    sentences = _tokenize_sentences(text)
    word_count = len(words)
    sentence_count = len(sentences)
    # Score based on word count: 200+ words = full score, scales linearly below
    length_score = round(min(100.0, (word_count / 200) * 100), 2)
    return {
        'word_count': word_count,
        'sentence_count': sentence_count,
        'length_score': length_score,
    }


def compute_plagiarism_score(text: str, existing_texts: List[str]) -> float:
    """
    Returns originality score (0-100) where 100 = fully original.
    Uses TF-IDF cosine similarity vs. existing submissions.
    Requires scikit-learn (already in requirements).
    """
    if not existing_texts:
        return 100.0
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np

        corpus = existing_texts + [text]
        vectorizer = TfidfVectorizer(stop_words='english', min_df=1)
        tfidf_matrix = vectorizer.fit_transform(corpus)
        # Compare new text (last row) against all existing
        new_vec = tfidf_matrix[-1]
        existing_vecs = tfidf_matrix[:-1]
        similarities = cosine_similarity(new_vec, existing_vecs).flatten()
        max_similarity = float(np.max(similarities)) if len(similarities) else 0.0
        originality = round((1.0 - max_similarity) * 100, 2)
        return max(0.0, originality)
    except Exception as exc:
        logger.warning(f"Plagiarism check failed: {exc}")
        return 100.0  # fallback: assume original


def compute_grammar_issues(text: str) -> dict:
    """
    Basic grammar issue detection using regex patterns.
    Returns issue_count and a grammar_score (0-100).
    No external APIs needed.
    """
    issues = []
    # Repeated words (the the, is is)
    repeated = re.findall(r'\b(\w+)\s+\1\b', text.lower())
    issues.extend([f"Repeated word: '{w}'" for w in set(repeated)])
    # Missing space after punctuation
    missing_space = re.findall(r'[.!?,][a-zA-Z]', text)
    if missing_space:
        issues.append(f"Missing space after punctuation ({len(missing_space)} occurrence(s))")
    # Sentences starting with lowercase (after first one)
    sentences = _tokenize_sentences(text)
    for s in sentences[1:]:
        stripped = s.strip()
        if stripped and stripped[0].islower():
            issues.append(f"Sentence starts with lowercase: '{stripped[:30]}...'")
    # Multiple exclamation / question marks
    multi_punct = re.findall(r'[!?]{2,}', text)
    if multi_punct:
        issues.append(f"Multiple punctuation marks ({len(multi_punct)} occurrence(s))")

    issue_count = len(issues)
    # Deduct 5 points per issue, min 40 if there is content
    words = _tokenize_words(text)
    if not words:
        grammar_score = 0.0
    else:
        grammar_score = round(max(40.0, 100.0 - (issue_count * 5)), 2)

    return {
        'issue_count': issue_count,
        'issues': issues[:10],  # cap at 10 for readability
        'grammar_score': grammar_score,
    }


# ---------------------------------------------------------------------------
# Main evaluation function
# ---------------------------------------------------------------------------

def evaluate_text_submission(
    text: str,
    existing_submissions: Optional[List[str]] = None,
) -> dict:
    """
    Full NLP evaluation of a text submission.

    Returns a structured result dict with:
      - individual metric scores
      - overall ai_score (0-100)
      - feedback summary
      - readiness_label (Needs Work / Satisfactory / Good / Excellent)
    """
    if not text or not text.strip():
        return {
            'ai_score': 0.0,
            'readability_score': 0.0,
            'vocabulary_diversity': 0.0,
            'grammar_score': 0.0,
            'originality_score': 100.0,
            'word_count': 0,
            'sentence_count': 0,
            'feedback': 'No text submitted.',
            'readiness_label': 'Needs Work',
            'strengths': [],
            'improvements': ['Submit your written work for evaluation.'],
            'grammar_issues': [],
        }

    existing = existing_submissions or []

    flesch = compute_flesch_score(text)
    vocab = compute_vocabulary_diversity(text)
    length_data = compute_content_length_score(text)
    originality = compute_plagiarism_score(text, existing)
    grammar_data = compute_grammar_issues(text)

    # Convert Flesch to 0-100 readability score
    # Flesch: 0-30 = very difficult, 60-70 = standard, 90-100 = very easy
    # For academic/professional writing, target 50-70 is ideal.
    # Map: flesch ≥ 30 starts scoring, peak at 60, taper off at 90+
    if flesch < 30:
        readability_score = flesch * 0.5  # max 15
    elif flesch < 60:
        readability_score = 15.0 + ((flesch - 30) / 30) * 70  # 15-85
    elif flesch <= 80:
        readability_score = 85.0 + ((flesch - 60) / 20) * 15  # 85-100
    else:
        readability_score = max(60.0, 100.0 - (flesch - 80) * 1.5)  # too simple
    readability_score = round(readability_score, 2)

    # Weighted composite score
    # Readability: 25% | Vocabulary: 20% | Grammar: 25% | Originality: 20% | Length: 10%
    ai_score = round(
        0.25 * readability_score
        + 0.20 * vocab
        + 0.25 * grammar_data['grammar_score']
        + 0.20 * originality
        + 0.10 * length_data['length_score'],
        2,
    )
    ai_score = max(0.0, min(100.0, ai_score))

    # Readiness label
    if ai_score >= 80:
        readiness_label = 'Excellent'
    elif ai_score >= 65:
        readiness_label = 'Good'
    elif ai_score >= 50:
        readiness_label = 'Satisfactory'
    else:
        readiness_label = 'Needs Work'

    # Build feedback strings
    strengths = []
    improvements = []

    if readability_score >= 70:
        strengths.append('Your writing is clear and easy to follow.')
    else:
        improvements.append('Try shorter sentences and simpler vocabulary to improve readability.')

    if vocab >= 60:
        strengths.append('Good vocabulary diversity — you used a wide range of words.')
    else:
        improvements.append('Use more varied vocabulary to strengthen your writing.')

    if grammar_data['grammar_score'] >= 80:
        strengths.append('No significant grammar issues detected.')
    else:
        improvements.append('Fix grammar issues: ' + '; '.join(grammar_data['issues'][:3]))

    if originality >= 85:
        strengths.append('Content appears original — no significant matches with other submissions.')
    elif originality >= 60:
        improvements.append('Moderate similarity with other submissions detected. Ensure original work.')
    else:
        improvements.append('High similarity with existing submissions detected. Please submit original work.')

    if length_data['word_count'] >= 200:
        strengths.append(f"Good length — {length_data['word_count']} words.")
    else:
        improvements.append(
            f"Your submission is short ({length_data['word_count']} words). "
            f"Aim for at least 200 words for a thorough response."
        )

    feedback = (
        f"AI Evaluation: {readiness_label}. "
        f"Overall score: {ai_score}/100. "
        f"Word count: {length_data['word_count']}. "
        f"Readability: {readability_score}/100. "
        f"Vocabulary diversity: {vocab}%. "
        f"Originality: {originality}%."
    )

    return {
        'ai_score': ai_score,
        'readability_score': readability_score,
        'vocabulary_diversity': vocab,
        'grammar_score': grammar_data['grammar_score'],
        'originality_score': originality,
        'word_count': length_data['word_count'],
        'sentence_count': length_data['sentence_count'],
        'feedback': feedback,
        'readiness_label': readiness_label,
        'strengths': strengths,
        'improvements': improvements,
        'grammar_issues': grammar_data['issues'],
    }
