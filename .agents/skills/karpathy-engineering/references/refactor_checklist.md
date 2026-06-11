# Refactor Checklist

Use this before changing structure without changing behavior.

## Safe Sequence

1. Run baseline tests.
2. Make one small change.
3. Run focused tests.
4. Run synthetic smoke when affected.
5. Compare profile output when token/timing behavior is affected.
6. Commit only after checks pass or blocker evidence is documented.

## Red Flags

- Duplicated token formulas.
- Duplicated profile field names.
- Too many tiny helpers.
- Unexplained classes.
- Hidden environment coupling.
- Silent fallback.
- Broad exceptions.
- Mixed public/local files in the same commit.
- Refactor changes that alter artifact schema without explicit migration.
- Source inspection being treated as runtime proof.
