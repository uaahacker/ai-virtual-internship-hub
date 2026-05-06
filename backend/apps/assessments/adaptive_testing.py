"""
Adaptive Testing via Q-Learning (Reinforcement Learning).

Implements the "Adaptive Testing" component of FR2 (Skill Assessment).

Architecture
-----------
This module uses a tabular Q-Learning agent to decide the optimal question
difficulty sequence for each student.  The goal is to present questions at
an appropriate challenge level — not too easy (boring, little information
gained) and not too hard (demoralising, also little signal) — maximising the
information gain about the student's true competence.

State Space  (4 states)
  0 — Unknown / first question  (no answers yet)
  1 — Struggling                (current accuracy < 40%)
  2 — On-track                  (current accuracy 40-70%)
  3 — Excelling                 (current accuracy > 70%)

Action Space  (3 actions)
  0 — Serve an EASY   question  (difficulty_weight < 0.85)
  1 — Serve a  MEDIUM question  (0.85 ≤ difficulty_weight ≤ 1.15)
  2 — Serve a  HARD   question  (difficulty_weight > 1.15)

Reward Function
  +1.0  Correct answer to a HARD   question (high information gain)
  +0.7  Correct answer to a MEDIUM question
  +0.3  Correct answer to an EASY  question
  -0.5  Wrong   answer to a HARD   question
  -0.2  Wrong   answer to a MEDIUM question
  -0.0  Wrong   answer to an EASY  question (expected, no penalty)

Q-Table Update  (standard Bellman equation)
  Q[s][a] ← Q[s][a] + α × (r + γ × max Q[s'] - Q[s][a])
  α (learning rate) = 0.3
  γ (discount)      = 0.8

The Q-table is persisted to ml_models/adaptive_qtable.json and updated
after every assessment submission.  On first run the table is initialised
with slightly optimistic values that favour medium difficulty, which
encodes the common-sense prior.

Usage
-----
  # When serving an assessment to a student:
  from apps.assessments.adaptive_testing import AdaptiveTesting
  ordered_questions = AdaptiveTesting.order_questions(questions, student)

  # After a student submits their answers:
  from apps.assessments.adaptive_testing import AdaptiveTesting
  AdaptiveTesting.update_qtable(question_sequence, answer_results)
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

N_STATES  = 4   # Unknown, Struggling, On-track, Excelling
N_ACTIONS = 3   # Easy, Medium, Hard

ALPHA = 0.3   # learning rate
GAMMA = 0.8   # discount factor

EASY_THRESHOLD   = 0.85
HARD_THRESHOLD   = 1.15

# Reward table: reward[action][correct]
REWARDS: Dict[int, Dict[bool, float]] = {
    0: {True: 0.3,  False:  0.0},   # Easy
    1: {True: 0.7,  False: -0.2},   # Medium
    2: {True: 1.0,  False: -0.5},   # Hard
}

_ML_DIR    = Path(__file__).resolve().parent.parent.parent.parent / "ml_models"
QTABLE_PATH = _ML_DIR / "adaptive_qtable.json"

# ─────────────────────────────────────────────────────────────────────────────
# Q-Table I/O
# ─────────────────────────────────────────────────────────────────────────────

def _default_qtable() -> List[List[float]]:
    """
    Initialise Q-table with a prior that slightly favours medium difficulty
    in most states, with escalation to hard when excelling.
    """
    return [
        # Easy,  Medium, Hard
        [0.20,   0.40,   0.30],   # state 0: Unknown
        [0.40,   0.30,   0.10],   # state 1: Struggling  → prefer easy
        [0.20,   0.50,   0.40],   # state 2: On-track    → prefer medium/hard
        [0.10,   0.35,   0.60],   # state 3: Excelling   → prefer hard
    ]


def _load_qtable() -> List[List[float]]:
    if QTABLE_PATH.exists():
        try:
            with open(QTABLE_PATH) as f:
                data = json.load(f)
            if isinstance(data, list) and len(data) == N_STATES:
                return data
        except Exception as exc:
            logger.warning("Could not load Q-table, using default: %s", exc)
    return _default_qtable()


def _save_qtable(qtable: List[List[float]]) -> None:
    try:
        _ML_DIR.mkdir(parents=True, exist_ok=True)
        with open(QTABLE_PATH, "w") as f:
            json.dump(qtable, f, indent=2)
    except Exception as exc:
        logger.warning("Could not save Q-table: %s", exc)


# ─────────────────────────────────────────────────────────────────────────────
# State encoding
# ─────────────────────────────────────────────────────────────────────────────

def _get_state(correct_so_far: int, total_so_far: int) -> int:
    """Map current running accuracy to a Q-learning state (0-3)."""
    if total_so_far == 0:
        return 0  # Unknown
    acc = correct_so_far / total_so_far
    if acc < 0.40:
        return 1  # Struggling
    if acc <= 0.70:
        return 2  # On-track
    return 3      # Excelling


def _classify_question(difficulty_weight: float) -> int:
    """Map difficulty_weight to action index (0=easy, 1=medium, 2=hard)."""
    if difficulty_weight < EASY_THRESHOLD:
        return 0
    if difficulty_weight <= HARD_THRESHOLD:
        return 1
    return 2


# ─────────────────────────────────────────────────────────────────────────────
# Core Q-Learning agent
# ─────────────────────────────────────────────────────────────────────────────

class AdaptiveTesting:
    """
    Q-Learning based adaptive question ordering for MCQ assessments.

    The adaptive ordering is applied server-side before returning the question
    list to the student — the frontend API response format is unchanged.
    Mentors and admins can observe the difficulty progression in the
    detailed_breakdown of each AssessmentAttempt.
    """

    @staticmethod
    def order_questions(questions: list, student=None) -> list:
        """
        Return *questions* sorted in adaptive difficulty order using the
        current Q-table policy.

        Strategy
        --------
        Simulate the greedy Q-policy through the question sequence:
          1. Start in state 0 (Unknown).
          2. At each position, choose the action (difficulty tier) with the
             highest Q-value for the current state.
          3. Among all questions in that tier, pick the one whose weight is
             closest to the tier midpoint (most representative).
          4. Transition state using the expected accuracy for that tier
             (Easy: 80% correct, Medium: 60%, Hard: 35%).
          5. Remaining questions that don't fit the preferred tier fill the
             remaining slots in weight order.

        If the student has prior assessment attempts, their historical
        domain accuracy is used to set the starting state instead of
        state 0.

        Returns the same list of question objects in a new order.
        """
        if not questions:
            return questions

        qtable = _load_qtable()

        # Determine starting state from student history (if available)
        start_state = 0
        if student is not None:
            try:
                from apps.assessments.models import AssessmentAttempt
                attempts = AssessmentAttempt.objects.filter(
                    student=student
                ).order_by('-attempted_at')[:5]
                if attempts.exists():
                    scores = [a.percentage for a in attempts]
                    avg = sum(scores) / len(scores)
                    # Map average historical score to state
                    if avg < 40:
                        start_state = 1
                    elif avg <= 70:
                        start_state = 2
                    else:
                        start_state = 3
            except Exception:
                start_state = 0

        # Bucket questions by difficulty tier
        buckets: Dict[int, list] = {0: [], 1: [], 2: []}
        for q in questions:
            weight = float(getattr(q, 'difficulty_weight', 1.0))
            tier   = _classify_question(weight)
            buckets[tier].append(q)

        # Sort each bucket by weight (easiest-first within tier)
        for tier in buckets:
            buckets[tier].sort(key=lambda q: float(getattr(q, 'difficulty_weight', 1.0)))

        ordered = []
        correct_sim  = 0
        answered_sim = 0
        state = start_state

        # Greedy policy: pick best action at each step
        for _ in range(len(questions)):
            q_values = qtable[state]
            # Prefer actions with available questions; fall back in order
            action_pref = sorted(range(N_ACTIONS), key=lambda a: q_values[a], reverse=True)

            picked = None
            for action in action_pref:
                if buckets[action]:
                    picked = buckets[action].pop(0)
                    chosen_action = action
                    break

            if picked is None:
                break

            ordered.append(picked)

            # Simulate transition using expected accuracy per tier
            EXPECTED_CORRECT = {0: 0.80, 1: 0.60, 2: 0.35}
            answered_sim += 1
            correct_sim  += EXPECTED_CORRECT[chosen_action]
            state = _get_state(int(correct_sim), answered_sim)

        # Append any leftovers (shouldn't normally happen)
        for tier in (0, 1, 2):
            ordered.extend(buckets[tier])

        return ordered

    @staticmethod
    def update_qtable(
        question_sequence: List[Dict],
        answer_results: List[bool],
    ) -> None:
        """
        Update the Q-table using the Bellman equation after a completed
        assessment.

        Parameters
        ----------
        question_sequence : list of dicts
            Each dict must have 'difficulty_weight' (float).
        answer_results : list of bool
            True = answered correctly, False = wrong.  Must be same length
            as question_sequence.

        The Q-table update is:
            Q[s][a] ← Q[s][a] + α × (r + γ × max Q[s'] - Q[s][a])
        """
        if not question_sequence or not answer_results:
            return
        if len(question_sequence) != len(answer_results):
            logger.warning(
                "update_qtable: sequence length %d ≠ results length %d — skipping",
                len(question_sequence), len(answer_results),
            )
            return

        qtable = _load_qtable()

        correct_so_far = 0
        total_so_far   = 0

        for i, (q_info, correct) in enumerate(zip(question_sequence, answer_results)):
            weight  = float(q_info.get('difficulty_weight', 1.0))
            action  = _classify_question(weight)
            state   = _get_state(correct_so_far, total_so_far)
            reward  = REWARDS[action][correct]

            # Update running counters
            total_so_far   += 1
            correct_so_far += int(correct)

            # Next state after this answer
            next_state = _get_state(correct_so_far, total_so_far)
            max_next_q = max(qtable[next_state])

            # Bellman update
            old_q = qtable[state][action]
            qtable[state][action] = round(
                old_q + ALPHA * (reward + GAMMA * max_next_q - old_q), 4
            )

        _save_qtable(qtable)
        logger.info("Q-table updated from %d question responses", len(question_sequence))

    @staticmethod
    def get_qtable_info() -> Dict:
        """Return a human-readable summary of the current Q-table for display."""
        qtable = _load_qtable()
        state_names  = ["Unknown", "Struggling", "On-track", "Excelling"]
        action_names = ["Easy", "Medium", "Hard"]
        summary = {}
        for s, row in enumerate(qtable):
            best_action = action_names[row.index(max(row))]
            summary[state_names[s]] = {
                action_names[a]: round(row[a], 3) for a in range(N_ACTIONS)
            }
            summary[state_names[s]]["recommended_difficulty"] = best_action
        return {"qtable": summary, "file": str(QTABLE_PATH)}
