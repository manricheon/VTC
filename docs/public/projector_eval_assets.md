# Projector Eval Assets

This file records the default checkpoint assets for the LLaVA-1.5 projector
comparison harness. It is a mapping document only; it does not authorize or run
downloads.

All checkpoint payloads must live under `weights/checkpoints/`.

## Default Checkpoints

| Projector | HF repo | Local path | Base | Visual tokens | Runtime knob |
| --- | --- | --- | --- | ---: | --- |
| Fourier-LLaVA-v1.5-7B-144 | `whyisverysmart/Fourier-LLaVA-v1.5-7B-144` | `weights/checkpoints/Fourier-LLaVA-v1.5-7B-144` | LLaVA-v1.5-7B | 144 | `FOURIER_RESERVE=12` |
| DiVT0.65 | `hyunlee86/llava-v1.5-7b-divt-0.65` | `weights/checkpoints/llava-v1.5-7b-divt-0.65` | LLaVA-v1.5-7B | 74.1 | `DIVT_THRESHOLD=0.65` |

## Notes

- Fourier default uses the paper checkpoint listed in the Fourier-Compressor
  README. The `vtc_fourier_llava15` wrapper still applies Fourier's LLaVA
  runtime patch before model load.
- DiVT default uses the official `0.65` checkpoint listed in the DiVT README.
- Override paths with `FOURIER_CKPT` and `DIVT_CKPT` when testing another
  checkpoint.
- Keep downloaded weights out of git. The repository should only commit source,
  docs, scripts, and tests.

## Expected Download Targets

The intended local layout is:

```text
weights/checkpoints/
|-- Fourier-LLaVA-v1.5-7B-144/
`-- llava-v1.5-7b-divt-0.65/
```

After assets are present, verify with:

```bash
bash scripts/run_projector_eval_limit1.sh
```

The runner should stop reporting missing checkpoint blockers before real
`RUN_PROJECTOR_EVAL=1` execution is attempted.
