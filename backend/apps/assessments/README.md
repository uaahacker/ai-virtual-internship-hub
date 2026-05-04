# assessments — Skill Assessments & AI Evaluation Engine

The `assessments` app delivers domain-specific MCQ assessments, evaluates them with a multi-dimensional scoring engine, generates NLP-based personalized feedback, and writes skill scores back to the student's profile to drive task recommendations.

---

## Table of Contents

1. [Models](#models)
2. [URL Reference](#url-reference)
3. [Assessment Flow](#assessment-flow)
4. [Evaluation Engine](#evaluation-engine)
5. [NLP Feedback Generator](#nlp-feedback-generator)
6. [Domain Stats](#domain-stats)
7. [Serializers](#serializers)
8. [Management Commands](#management-commands)

---

## Models

### `Assessment`
A domain-specific skill test composed of multiple-choice questions.

| Field | Type | Notes |
|-------|------|-------|
| `title` | CharField | Assessment name |
| `domain` | CharField | e.g., "Web Development", "Graphic Design" |
| `description` | TextField | |
| `difficulty` | CharField | beginner / intermediate / advanced |
| `time_limit` | IntegerField | Minutes |
| `passing_score` | IntegerField | Minimum score to pass (default 60) |
| `is_active` | BooleanField | Only active assessments shown to students |
| `created_at` | DateTimeField | |

---

### `Question`
One MCQ question belonging to an Assessment.

| Field | Type | Notes |
|-------|------|-------|
| `assessment` | ForeignKey → Assessment | `related_name='questions'` |
| `question_text` | TextField | The question |
| `option_a` — `option_d` | CharField | 4 answer choices |
| `correct_answer` | CharField | `a`, `b`, `c`, or `d` |
| `concept` | CharField | Concept tag (e.g., "CSS", "React Hooks") |
| `difficulty_weight` | FloatField | 0.5 – 2.0; harder questions score higher |
| `explanation` | TextField | Shown in results |

---

### `AssessmentAttempt`
One student's completed attempt at an Assessment.

| Field | Type | Notes |
|-------|------|-------|
| `student` | ForeignKey → User | |
| `assessment` | ForeignKey → Assessment | |
| `answers` | JSONField | `{question_id: chosen_option}` |
| `domain_score` | FloatField | 0–100 score for this domain |
| `concept_scores` | JSONField | `{concept: score}` dict |
| `readiness_level` | CharField | Novice / Developing / Competent / Proficient / Expert |
| `skill_profile_vector` | JSONField | `{concept: proficiency}` 0–1 per concept |
| `improvement_delta` | FloatField | Score change vs. previous attempt |
| `feedback` | TextField | NLP-generated text feedback |
| `recommended_task_type` | CharField | Design / Development / Content / etc. |
| `next_steps` | JSONField | List of recommended focus areas |
| `completed_at` | DateTimeField | Auto-set |

---

## URL Reference

All URLs prefixed with `/api/assessments/`.

| Method | Path | Permission | Description |
|--------|------|-----------|-------------|
| GET | `/` | Student | List all active assessments |
| GET | `/:id/` | Student | Get assessment with questions |
| POST | `/:id/submit/` | Student | Submit answers → triggers evaluation |
| GET | `/my-attempts/` | Student | All of student's attempt history |
| GET | `/my-attempts/:id/` | Student | Detail for a single attempt |
| GET | `/admin/` | Admin | List all assessments (incl. inactive) |
| POST | `/admin/create/` | Admin | Create new assessment |
| PUT | `/admin/:id/update/` | Admin | Update assessment |
| DELETE | `/admin/:id/delete/` | Admin | Delete assessment |
| POST | `/admin/:id/add-question/` | Admin | Add question to assessment |
| DELETE | `/admin/questions/:id/delete/` | Admin | Delete a question |

---

## Assessment Flow

```
1.  Student calls GET /assessments/:id/   → receives questions (correct_answer hidden)
2.  Student answers questions
3.  Student calls POST /assessments/:id/submit/
        body: { "answers": {"1": "a", "2": "c", ...} }
4.  Backend:
        a. EvaluationEngine.evaluate(assessment, answers) → result dict
        b. NLPFeedbackGenerator.generate(result) → feedback text
        c. AssessmentAttempt saved with all scores
        d. StudentProfile updated:
              - skill_scores_by_domain[domain] = domain_score
              - strongest_domain / weakest_domain recalculated
              - cluster updated via StudentClusterer.update_student_cluster()
5.  Response: full attempt result including feedback, concept scores, readiness level
```

---

## Evaluation Engine

`apps/assessments/evaluation_engine.py` — `EvaluationEngine` class.

**No external APIs used — pure Python computation.**

### Algorithm

1. For each question answered:
   - Check correctness
   - Apply `difficulty_weight` multiplier to the score contribution
   - Accumulate score per concept

2. Calculate overall `domain_score`:
   ```
   domain_score = (weighted_correct / max_weighted_score) × 100
   ```

3. Map `domain_score` to `readiness_level`:
   | Score Range | Level |
   |-------------|-------|
   | 0–39 | Novice |
   | 40–54 | Developing |
   | 55–69 | Competent |
   | 70–84 | Proficient |
   | 85–100 | Expert |

4. Build `skill_profile_vector` — normalized 0–1 proficiency per concept

5. Calculate `improvement_delta`:
   ```
   improvement_delta = current_domain_score - previous_domain_score
   ```
   (0.0 on first attempt)

6. Determine `recommended_task_type` based on domain + readiness level

7. Generate `next_steps` list (concepts with lowest scores)

### Return Value

```python
{
    "domain_score": 72.5,
    "concept_scores": {"React Hooks": 80, "State Management": 65, ...},
    "readiness_level": "Proficient",
    "skill_profile_vector": {"React Hooks": 0.80, "State Management": 0.65, ...},
    "improvement_delta": 5.3,
    "recommended_task_type": "Development",
    "next_steps": ["State Management", "Testing"]
}
```

---

## NLP Feedback Generator

`apps/assessments/nlp_feedback.py` — `NLPFeedbackGenerator` class.

Generates human-sounding feedback paragraphs — **no external LLM used**.

### Mechanism

1. Templates are organized per `readiness_level` and score range bucket
2. Key variables (domain name, strongest concept, weakest concept, score, improvement) are injected
3. NLTK WordNet is used to vary synonyms in template sentences — different wording each run
4. Graceful fallback to plain templates if NLTK `wordnet` corpus is unavailable

### Example Output

> "Your Web Development skills are developing well — you scored 72.5%, showing solid understanding of React Hooks. Focus on strengthening State Management to advance further. Your score improved by 5.3 points since your last attempt, which reflects consistent progress."

---

## Domain Stats

`apps/assessments/domain_stats.py` — `DomainStatsService`

Provides aggregated statistics per domain across all students, used by admin analytics:
- Average score per domain
- Pass rate per domain
- Attempt count

---

## Serializers

| Serializer | Purpose |
|-----------|---------|
| `AssessmentSerializer` | Assessment list/detail (questions excluded in list) |
| `AssessmentWithQuestionsSerializer` | Full assessment + questions (for taking the test) |
| `QuestionSerializer` | Question detail (correct_answer omitted for students) |
| `SubmitAttemptSerializer` | Validates submitted answers dict |
| `AssessmentAttemptSerializer` | Full attempt result including feedback and scores |

---

## Management Commands

```bash
# Seed the database with pre-built domain assessment questions
python manage.py seed_assessments
```

Seeds assessments for all 10 supported domains:
- Web Development
- Graphic Design  
- Content Writing
- Digital Marketing
- Video Editing
- Data Analysis
- Mobile Development
- UI/UX Design
- Cybersecurity
- Cloud Computing
