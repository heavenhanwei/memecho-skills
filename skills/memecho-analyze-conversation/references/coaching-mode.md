# Coaching mode

Use this reference only for interactive practice.

## Candidate selection

Choose moments supported by evidence where the speaker stalls or abandons a point, fuses facts with judgments and requests, receives resistance or confusion, shows an expressed VAD shift, or leaves no actionable next step. Editing and ASR gaps are alternative explanations. Do not score fluency, intelligence, personality, or mental health.

## Exercise shape

Give only one exercise at a time:

```text
场景：…
对方刚刚说：…
练习目标：…
请用你自己的话回答；我会在你回答后评分。
```

Set `status: awaiting_user`. Do not generate a model answer before the user attempts unless explicitly requested.

## Scoring rubric

Score each dimension from 1 to 5:

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| clarity | intent is unclear | main point is understandable | one clear intent and bounded request |
| acknowledgment | ignores the other line | partial recognition | accurately reflects the other viewpoint |
| emotional_load | global or accusatory wording | mixed pressure | specific, low-pressure wording |
| evidence_separation | judgment presented as fact | some separation | fact, interpretation, and need are explicit |
| actionability | no next step | broad suggestion | feasible next action or check |

Total score is the mean of answered dimensions, not a judgment of the person. Attach evidence from the user's practice response.

## Feedback order

1. One observable strength.
2. One highest-leverage improvement.
3. One low-pressure rewrite.
4. Optional harder follow-up with consent.
