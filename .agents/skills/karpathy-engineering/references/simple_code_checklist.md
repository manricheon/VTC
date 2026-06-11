# Simple Code Checklist

Use this before and after any nontrivial VTC change.

- Can a new contributor understand this file in 5 minutes?
- Is there a simpler inline version?
- Is this helper justified?
- Is this class justified by real stateful behavior?
- Are paths explicit?
- Are environment variables explicit?
- Are errors actionable?
- Are broad exceptions avoided or reported with exact errors?
- Are token formulas centralized?
- Are profile fields centralized?
- Are artifact schemas documented?
- Are tests meaningful beyond shape checks?
- Does the change avoid silent fallback?
- Does the change avoid hidden coupling between envs?
- Is unverifed behavior labeled as unverified?
- Is public code kept separate from local/private guidance?
