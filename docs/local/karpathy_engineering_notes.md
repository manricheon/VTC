# Karpathy Engineering Notes

This is local guidance and must be excluded from future public branches.

Invoke the project-local skill with:

```text
Use $karpathy-engineering for this task.
```

Use it for all new VTC work. It is especially important before:

- new code
- refactors
- blocker resolution
- environment scripts
- external/HF asset setup
- profiling changes
- model integration
- worktree handoff

The skill lives at:

```text
.agents/skills/karpathy-engineering/SKILL.md
```

The short version: write simple code, keep contracts explicit, measure token/timing/memory behavior, verify before handoff, and keep local guidance separate from public code commits.
