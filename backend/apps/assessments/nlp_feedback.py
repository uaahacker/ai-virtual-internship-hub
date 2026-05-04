"""
Local NLP Feedback Generator.

Generates human-sounding feedback paragraphs from structured assessment data
using NLTK WordNet synonym variation and rule-based sentence planning.
No external API calls. Falls back gracefully if NLTK data is not downloaded.

Usage:
    from apps.assessments.nlp_feedback import generate_feedback

    text = generate_feedback(
        domain='Programming',
        percentage=72.5,
        skill_level='Intermediate',
        correct_count=9,
        total_count=12,
        strengths=['Good understanding of loops'],
        weaknesses=['Struggled with recursion'],
        improvement_areas=['Practice recursion problems', 'Review data structures'],
        attempt_number=2,        # which attempt this is (for progress language)
        previous_percentage=58,  # percentage in last attempt (optional)
    )
"""

import random
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# NLTK bootstrap (graceful fallback if unavailable)
# ─────────────────────────────────────────────

_NLTK_AVAILABLE = False
_WORDNET_AVAILABLE = False

try:
    import nltk  # noqa: F401
    _NLTK_AVAILABLE = True
    try:
        from nltk.corpus import wordnet as wn
        # Test the corpus is downloaded
        wn.synsets('good')
        _WORDNET_AVAILABLE = True
    except Exception:
        # Download silently if possible
        try:
            nltk.download('wordnet', quiet=True)
            nltk.download('omw-1.4', quiet=True)
            from nltk.corpus import wordnet as wn
            wn.synsets('good')
            _WORDNET_AVAILABLE = True
        except Exception:
            pass
except ImportError:
    pass


def _synonyms(word: str, pos: str = 'a') -> List[str]:
    """
    Return a short list of synonyms for word using WordNet.
    pos: 'a'=adjective, 'v'=verb, 'n'=noun, 'r'=adverb
    Falls back to empty list if NLTK unavailable.
    """
    if not _WORDNET_AVAILABLE:
        return []
    try:
        from nltk.corpus import wordnet as wn
        synsets = wn.synsets(word, pos=pos)
        synonyms = set()
        for syn in synsets[:3]:
            for lemma in syn.lemmas():
                name = lemma.name().replace('_', ' ')
                if name.lower() != word.lower() and len(name) < 20:
                    synonyms.add(name)
        return list(synonyms)[:4]
    except Exception:
        return []


def _vary(word: str, pos: str = 'a', default: Optional[str] = None) -> str:
    """
    Return word or a synonym at random.
    Used to add lexical variety to generated text.
    """
    syns = _synonyms(word, pos)
    candidates = [word] + syns
    # Use a deterministic seed so results are stable per word
    rng = random.Random(word)
    result = rng.choice(candidates)
    return default if result is None else result


# ─────────────────────────────────────────────
# Sentence templates (grouped by context)
# ─────────────────────────────────────────────

_OPENING_ADVANCED = [
    "Your {domain} assessment reflects {strong_adj} mastery — you scored {pct:.0f}%.",
    "An {impressive_adj} result of {pct:.0f}% demonstrates your deep understanding of {domain}.",
    "You achieved {pct:.0f}% in {domain}, placing you firmly at the Advanced level.",
    "With {pct:.0f}% correct, your {domain} skills are clearly at an Advanced level.",
]

_OPENING_INTERMEDIATE = [
    "You scored {pct:.0f}% in {domain}, showing a solid Intermediate-level foundation.",
    "Your {domain} result of {pct:.0f}% indicates meaningful {developing_adj} knowledge.",
    "A score of {pct:.0f}% in {domain} positions you at the Intermediate level — well done.",
    "You are making {steady_adj} progress in {domain}, scoring {pct:.0f}% this time.",
]

_OPENING_BEGINNER = [
    "You scored {pct:.0f}% in {domain}, placing you at the Beginner level right now.",
    "This {domain} result ({pct:.0f}%) shows you are building early foundations in this field.",
    "A score of {pct:.0f}% in {domain} means there is {positive_adj} room to grow.",
    "You are at the beginning of your {domain} journey with {pct:.0f}% on this assessment.",
]

_PROGRESS_IMPROVED = [
    " You improved by {delta:.0f}% since your last attempt — keep this momentum going.",
    " Compared to your previous score, you gained {delta:.0f} percentage points.",
    " Your {delta:.0f}% improvement since last time shows your study efforts are paying off.",
]

_PROGRESS_SAME = [
    " Your score is consistent with your previous attempt.",
    " You maintained a similar level compared to last time.",
]

_PROGRESS_DECLINED = [
    " Your score dipped slightly from the previous attempt; reviewing the missed questions will help.",
    " A small drop from last time is normal — focus on the areas highlighted below.",
]

_STRENGTH_SENTENCES = [
    "You showed {strong_adj} understanding of {strength}.",
    "Your grasp of {strength} was clearly {confident_adj}.",
    "{strength} is already a strong area for you.",
]

_WEAKNESS_SENTENCES = [
    "The main area to improve is {weakness}.",
    "You found {weakness} {challenging_adj} — dedicating focused study here will accelerate progress.",
    "Revisiting {weakness} will have the biggest impact on your next score.",
]

_CLOSING_ADVANCED = [
    "You are {ready_adj} to pursue freelancing opportunities in {domain}.",
    "Consider building a portfolio of {domain} projects and applying to client work.",
    "Your skill level supports taking on {domain} client projects — start with smaller gigs to build reviews.",
]

_CLOSING_INTERMEDIATE = [
    "With some {targeted_adj} practice, you will reach Advanced level in {domain}.",
    "Review the recommended resources and retake this assessment in 2–3 weeks to track your progress.",
    "Continue practising {domain} concepts and you will be freelance-ready soon.",
]

_CLOSING_BEGINNER = [
    "Start with the recommended beginner resources for {domain} and aim to retake this in a few weeks.",
    "Build a strong foundation in {domain} by completing structured courses before attempting advanced work.",
    "Everyone starts here — consistent practice is the key to moving up quickly in {domain}.",
]


def _pick(templates: List[str], seed: int) -> str:
    """Deterministically pick a template based on a seed."""
    return templates[seed % len(templates)]


def generate_feedback(
    domain: str,
    percentage: float,
    skill_level: str,
    correct_count: int,
    total_count: int,
    strengths: Optional[List[str]] = None,
    weaknesses: Optional[List[str]] = None,
    improvement_areas: Optional[List[str]] = None,
    attempt_number: int = 1,
    previous_percentage: Optional[float] = None,
) -> str:
    """
    Generate a localised 3-5 sentence feedback paragraph.

    The output varies with:
    - domain, skill level, score
    - progress vs previous attempt
    - identified strengths and weaknesses
    - attempt count (first-time vs returning student language)

    Args:
        domain: e.g. 'Programming'
        percentage: 0-100 float
        skill_level: 'Beginner' | 'Intermediate' | 'Advanced'
        correct_count: number of correct answers
        total_count: total number of questions
        strengths: list of strength strings (from AssessmentAttempt.strengths)
        weaknesses: list of weakness strings (from AssessmentAttempt.weaknesses)
        improvement_areas: list of improvement areas (from recommendation)
        attempt_number: 1-based index of this attempt for this domain
        previous_percentage: score from previous attempt, if any

    Returns:
        feedback string (plain text, 3-5 sentences)
    """
    strengths = strengths or []
    weaknesses = weaknesses or []
    improvement_areas = improvement_areas or []

    # Seed for deterministic variation across skill-level/domain combos
    seed = int(percentage) + len(domain) + (correct_count * 7)

    sentences = []

    # ── 1. Opening sentence ────────────────────────────────────────────────
    strong_adj = _vary('excellent', 'a', 'excellent')
    impressive_adj = _vary('impressive', 'a', 'impressive')
    developing_adj = _vary('developing', 'v', 'developing')
    steady_adj = _vary('steady', 'a', 'steady')
    positive_adj = _vary('significant', 'a', 'significant')

    if skill_level == 'Advanced':
        tpl = _pick(_OPENING_ADVANCED, seed)
        opening = tpl.format(
            domain=domain, pct=percentage,
            strong_adj=strong_adj, impressive_adj=impressive_adj,
        )
    elif skill_level == 'Intermediate':
        tpl = _pick(_OPENING_INTERMEDIATE, seed)
        opening = tpl.format(
            domain=domain, pct=percentage,
            developing_adj=developing_adj, steady_adj=steady_adj,
        )
    else:
        tpl = _pick(_OPENING_BEGINNER, seed)
        opening = tpl.format(
            domain=domain, pct=percentage, positive_adj=positive_adj,
        )
    sentences.append(opening)

    # ── 2. Progress sentence (if previous attempt exists) ─────────────────
    if previous_percentage is not None and attempt_number > 1:
        delta = percentage - previous_percentage
        if delta > 2:
            prog_tpl = _pick(_PROGRESS_IMPROVED, seed)
            sentences.append(prog_tpl.format(delta=abs(delta)))
        elif delta < -2:
            sentences.append(_pick(_PROGRESS_DECLINED, seed))
        else:
            sentences.append(_pick(_PROGRESS_SAME, seed))

    # ── 3. Strength sentence ──────────────────────────────────────────────
    if strengths:
        strength_text = strengths[0] if len(strengths[0]) < 80 else strengths[0][:77] + '...'
        str_tpl = _pick(_STRENGTH_SENTENCES, seed + 1)
        confident_adj = _vary('confident', 'a', 'confident')
        sentences.append(str_tpl.format(
            strength=strength_text,
            strong_adj=strong_adj,
            confident_adj=confident_adj,
        ))

    # ── 4. Weakness / improvement sentence ────────────────────────────────
    if weaknesses:
        weak_text = weaknesses[0] if len(weaknesses[0]) < 80 else weaknesses[0][:77] + '...'
        weak_tpl = _pick(_WEAKNESS_SENTENCES, seed + 2)
        challenging_adj = _vary('challenging', 'a', 'challenging')
        sentences.append(weak_tpl.format(
            weakness=weak_text,
            challenging_adj=challenging_adj,
        ))
    elif improvement_areas:
        area = improvement_areas[0]
        sentences.append(f"Focus on: {area}.")

    # ── 5. Closing sentence ───────────────────────────────────────────────
    ready_adj = _vary('ready', 'a', 'ready')
    targeted_adj = _vary('targeted', 'a', 'targeted')

    if skill_level == 'Advanced':
        closing = _pick(_CLOSING_ADVANCED, seed).format(
            domain=domain, ready_adj=ready_adj,
        )
    elif skill_level == 'Intermediate':
        closing = _pick(_CLOSING_INTERMEDIATE, seed).format(
            domain=domain, targeted_adj=targeted_adj,
        )
    else:
        closing = _pick(_CLOSING_BEGINNER, seed).format(domain=domain)

    sentences.append(closing)

    return ' '.join(sentences)


# ─────────────────────────────────────────────
# Domain-specific vocabulary
# ─────────────────────────────────────────────

_DOMAIN_VERBS = {
    'Graphic Design':     ('design', 'create visual assets', 'apply design principles'),
    'Content Writing':    ('write', 'craft compelling content', 'communicate clearly'),
    'Programming':        ('code', 'build software', 'solve problems algorithmically'),
    'Freelancing':        ('manage client work', 'deliver projects', 'communicate professionally'),
    'E-Commerce':         ('operate online stores', 'optimise conversions', 'manage product listings'),
    'QuickBooks':         ('manage accounts', 'record financial data', 'prepare reports'),
    'AutoCAD':            ('draft technical drawings', 'model structures', 'produce CAD designs'),
    'Data Analytics':     ('analyse data', 'extract insights', 'visualise findings'),
    'Digital Marketing':  ('run campaigns', 'grow online presence', 'analyse performance metrics'),
    'WordPress':          ('build websites', 'customise themes', 'manage WordPress sites'),
}

_CLUSTER_PHRASES = {
    'Explorer': (
        'As someone early in your learning journey, every assessment you complete builds '
        'critical foundations for the domains ahead.'
    ),
    'Developing': (
        'Your progress puts you in the Developing cluster — you are building consistent skills '
        'across multiple areas.'
    ),
    'Competent': (
        'You are performing at a Competent level overall, which means you are ready to take on '
        'practical, real-world projects.'
    ),
    'Expert': (
        'Your performance places you in the Expert cluster — you are well-positioned for advanced '
        'freelancing and leadership roles.'
    ),
}

_TASK_TYPE_GUIDANCE = {
    'practice': 'Working through structured practice exercises will reinforce the concepts tested here.',
    'project':  'Taking on a guided project in {domain} will help you apply these skills in a practical context.',
    'challenge': 'You are ready for advanced challenge tasks in {domain} — push your boundaries further.',
}


# ─────────────────────────────────────────────
# Mentor notes keyword extractor
# ─────────────────────────────────────────────

_STOP_WORDS = {
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'shall', 'can', 'need', 'dare', 'ought',
    'and', 'but', 'or', 'nor', 'for', 'yet', 'so', 'although', 'because',
    'since', 'while', 'after', 'before', 'when', 'where', 'which', 'who',
    'that', 'this', 'these', 'those', 'it', 'its', 'of', 'to', 'in', 'on',
    'at', 'by', 'from', 'with', 'as', 'into', 'through', 'during', 'about',
    'up', 'down', 'out', 'off', 'over', 'then', 'your', 'you', 'student',
    'work', 'task', 'very', 'good', 'nice', 'well', 'also', 'not', 'no',
}


def _extract_mentor_keywords(notes: str, n: int = 3) -> List[str]:
    """
    Extract the n most meaningful words from mentor notes using
    simple frequency filtering (no external NLP library needed).
    """
    import re
    tokens = re.findall(r'[a-z]{4,}', notes.lower())
    freq: dict = {}
    for t in tokens:
        if t not in _STOP_WORDS:
            freq[t] = freq.get(t, 0) + 1
    ranked = sorted(freq, key=lambda w: -freq[w])
    return ranked[:n]


def _mentor_sentence(notes: str, domain: str) -> Optional[str]:
    """
    Build a single natural sentence referencing key mentor feedback keywords.
    Returns None if notes are too short to extract meaningful signal.
    """
    if not notes or len(notes.strip()) < 15:
        return None

    keywords = _extract_mentor_keywords(notes, n=3)
    if not keywords:
        return None

    # Detect overall sentiment via simple keyword presence
    praise_words = {'excellent', 'great', 'outstanding', 'impressive', 'strong',
                    'good', 'well', 'fantastic', 'brilliant', 'solid'}
    concern_words = {'improve', 'weak', 'missing', 'incorrect', 'incomplete',
                     'revise', 'redo', 'wrong', 'lacking', 'needs'}

    words_lower = set(notes.lower().split())
    if words_lower & praise_words:
        topic = keywords[0].replace('_', ' ')
        return (
            f"Your mentor highlighted positive progress, particularly around {topic} — "
            "this aligns with your assessment results."
        )
    elif words_lower & concern_words:
        topic = ', '.join(keywords[:2]).replace('_', ' ')
        return (
            f"Your mentor's notes suggest focusing on {topic} — "
            "addressing these will strengthen your overall {domain} proficiency."
        ).replace('{domain}', domain)
    else:
        # Neutral — just reference the topic
        topic = keywords[0].replace('_', ' ')
        return f"Your mentor noted aspects related to {topic} as worth paying attention to."


# ─────────────────────────────────────────────
# Structured feedback generator
# ─────────────────────────────────────────────

def generate_structured_feedback(
    domain: str,
    percentage: float,
    skill_level: str,
    correct_count: int,
    total_count: int,
    readiness_level: str = 'Novice',
    suggested_task_type: str = 'practice',
    strengths: Optional[List[str]] = None,
    weaknesses: Optional[List[str]] = None,
    improvement_areas: Optional[List[str]] = None,
    concept_scores: Optional[dict] = None,
    attempt_number: int = 1,
    previous_percentage: Optional[float] = None,
    improvement_delta: Optional[float] = None,
    cluster_label: str = 'Explorer',
    completed_tasks_count: int = 0,
    mentor_notes: str = '',
) -> dict:
    """
    Generate a structured feedback object from assessment result data.

    Returns a dict with these keys:
        summary          - 1-2 sentence performance overview
        strength         - key strength sentence
        weakness         - key weakness / improvement sentence
        recommendation   - actionable next-step recommendation
        suggested_task_type - 'practice' | 'project' | 'challenge'
        tone             - 'positive' | 'encouraging' | 'constructive'
        cluster_insight  - sentence referencing cluster context
        mentor_insight   - sentence derived from mentor notes (or None)
        full_text        - complete feedback paragraph (all parts joined)
    """
    strengths         = strengths or []
    weaknesses        = weaknesses or []
    improvement_areas = improvement_areas or []
    concept_scores    = concept_scores or {}

    seed = int(percentage) + len(domain) + correct_count * 7

    # ── Tone ──────────────────────────────────────────────────────────────
    if percentage >= 70:
        tone = 'positive'
    elif percentage >= 45:
        tone = 'encouraging'
    else:
        tone = 'constructive'

    # ── 1. Summary ─────────────────────────────────────────────────────────
    strong_adj       = _vary('excellent',   'a', 'excellent')
    impressive_adj   = _vary('impressive',  'a', 'impressive')
    developing_adj   = _vary('developing',  'v', 'developing')
    steady_adj       = _vary('steady',      'a', 'steady')
    positive_adj     = _vary('significant', 'a', 'significant')

    if skill_level == 'Advanced':
        tpl    = _pick(_OPENING_ADVANCED, seed)
        summary = tpl.format(
            domain=domain, pct=percentage,
            strong_adj=strong_adj, impressive_adj=impressive_adj,
        )
    elif skill_level == 'Intermediate':
        tpl    = _pick(_OPENING_INTERMEDIATE, seed)
        summary = tpl.format(
            domain=domain, pct=percentage,
            developing_adj=developing_adj, steady_adj=steady_adj,
        )
    else:
        tpl    = _pick(_OPENING_BEGINNER, seed)
        summary = tpl.format(
            domain=domain, pct=percentage, positive_adj=positive_adj,
        )

    # Add progress note to summary if available
    delta = improvement_delta
    if delta is None and previous_percentage is not None and attempt_number > 1:
        delta = percentage - previous_percentage

    if delta is not None and attempt_number > 1:
        if delta > 2:
            prog = _pick(_PROGRESS_IMPROVED, seed)
            summary += prog.format(delta=abs(delta))
        elif delta < -2:
            summary += _pick(_PROGRESS_DECLINED, seed)
        else:
            summary += _pick(_PROGRESS_SAME, seed)

    # ── 2. Strength sentence ───────────────────────────────────────────────
    # Prefer best concept from concept_scores over generic strength tag
    best_concept = None
    if concept_scores:
        best_concept = max(
            concept_scores,
            key=lambda c: concept_scores[c].get('score_pct', 0),
        )
        best_score = concept_scores[best_concept]['score_pct']
        # Only use if meaningful
        if best_score < 50:
            best_concept = None

    strength_source = (
        best_concept
        or (strengths[0] if strengths else None)
        or f'{domain} fundamentals'
    )
    str_tpl     = _pick(_STRENGTH_SENTENCES, seed + 1)
    confident_adj = _vary('confident', 'a', 'confident')
    strength_sentence = str_tpl.format(
        strength=strength_source,
        strong_adj=strong_adj,
        confident_adj=confident_adj,
    )

    # ── 3. Weakness / improvement sentence ────────────────────────────────
    worst_concept = None
    if concept_scores:
        worst_concept = min(
            concept_scores,
            key=lambda c: concept_scores[c].get('score_pct', 100),
        )
        worst_score = concept_scores[worst_concept]['score_pct']
        # Only highlight as a weakness if genuinely below threshold
        if worst_score >= 60:
            worst_concept = None

    weakness_source = (
        worst_concept
        or (weaknesses[0] if weaknesses else None)
    )
    if weakness_source:
        weak_tpl = _pick(_WEAKNESS_SENTENCES, seed + 2)
        challenging_adj = _vary('challenging', 'a', 'challenging')
        weakness_sentence = weak_tpl.format(
            weakness=weakness_source,
            challenging_adj=challenging_adj,
        )
    elif improvement_areas:
        weakness_sentence = f"Priority focus: {improvement_areas[0]}."
    else:
        weakness_sentence = (
            f"Continue exploring advanced {domain} topics to maintain and grow your edge."
        )

    # ── 4. Recommendation ─────────────────────────────────────────────────
    ready_adj    = _vary('ready',    'a', 'ready')
    targeted_adj = _vary('targeted', 'a', 'targeted')

    if skill_level == 'Advanced':
        rec_closing = _pick(_CLOSING_ADVANCED, seed).format(
            domain=domain, ready_adj=ready_adj,
        )
    elif skill_level == 'Intermediate':
        rec_closing = _pick(_CLOSING_INTERMEDIATE, seed).format(
            domain=domain, targeted_adj=targeted_adj,
        )
    else:
        rec_closing = _pick(_CLOSING_BEGINNER, seed).format(domain=domain)

    # Append task-type guidance
    task_guidance = _TASK_TYPE_GUIDANCE.get(suggested_task_type, '').format(domain=domain)
    recommendation = f"{rec_closing} {task_guidance}".strip()

    # ── 5. Cluster insight ─────────────────────────────────────────────────
    cluster_insight = _CLUSTER_PHRASES.get(cluster_label, _CLUSTER_PHRASES['Explorer'])

    # Add completed_tasks context if meaningful
    if completed_tasks_count >= 5:
        cluster_insight += (
            f" Having completed {completed_tasks_count} tasks, "
            "you are building practical experience alongside your assessment results."
        )

    # ── 6. Mentor insight ──────────────────────────────────────────────────
    mentor_insight = _mentor_sentence(mentor_notes, domain) if mentor_notes else None

    # ── Assemble full text ─────────────────────────────────────────────────
    parts = [summary, strength_sentence, weakness_sentence, recommendation]
    if mentor_insight:
        parts.append(mentor_insight)
    full_text = ' '.join(parts)

    return {
        'summary':            summary,
        'strength':           strength_sentence,
        'weakness':           weakness_sentence,
        'recommendation':     recommendation,
        'suggested_task_type': suggested_task_type,
        'tone':               tone,
        'cluster_insight':    cluster_insight,
        'mentor_insight':     mentor_insight,
        'full_text':          full_text,
    }


def generate_task_feedback(
    domain: str,
    mcq_score: float,
    mentor_score: Optional[float],
    final_score: float,
    strengths: Optional[List[str]] = None,
    weaknesses: Optional[List[str]] = None,
    mentor_feedback: str = '',
) -> str:
    """
    Generate a short NLP feedback summary for a completed task evaluation.

    Args:
        domain: task domain
        mcq_score: MCQ score 0-100
        mentor_score: mentor's evaluation score 0-100 (optional)
        final_score: combined final score 0-100
        strengths: list of strengths
        weaknesses: list of weaknesses
        mentor_feedback: raw mentor feedback text

    Returns:
        2-3 sentence summary string
    """
    strengths = strengths or []
    weaknesses = weaknesses or []
    seed = int(final_score) + len(domain)

    parts = []

    # Opening based on final score
    if final_score >= 80:
        parts.append(
            f"Excellent work on this {domain} task — your final score of "
            f"{final_score:.0f}% reflects strong performance."
        )
    elif final_score >= 60:
        parts.append(
            f"Good effort on this {domain} task. Your final score of "
            f"{final_score:.0f}% shows solid progress."
        )
    else:
        parts.append(
            f"You completed this {domain} task with a score of {final_score:.0f}%. "
            "There is room to improve, and this feedback will help you get there."
        )

    # MCQ vs mentor breakdown
    if mentor_score is not None:
        if abs(mcq_score - mentor_score) > 15:
            if mentor_score > mcq_score:
                parts.append(
                    f"Your mentor scored you higher ({mentor_score:.0f}%) than the MCQ alone "
                    f"({mcq_score:.0f}%), recognising the quality of your practical approach."
                )
            else:
                parts.append(
                    f"Your MCQ score ({mcq_score:.0f}%) was strong, but the mentor evaluation "
                    f"({mentor_score:.0f}%) indicates areas in the practical work to refine."
                )

    # Strength highlight
    if strengths:
        parts.append(f"Highlighted strength: {strengths[0]}.")

    # Weakness
    if weaknesses:
        parts.append(f"Key area for improvement: {weaknesses[0]}.")

    return ' '.join(parts)
