#!/usr/bin/env bash

if command -v git >/dev/null 2>&1; then
    _vtc_git_root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
else
    _vtc_git_root=""
fi

if [ -n "${_vtc_git_root}" ]; then
    export VTC_ROOT="${_vtc_git_root}"
elif [ -n "${VTC_ROOT:-}" ] && [ -d "${VTC_ROOT}/.git" ]; then
    export VTC_ROOT
elif [ -d ".git" ] && [ -d "weights" ]; then
    export VTC_ROOT="$(pwd)"
else
    echo "Unable to resolve VTC_ROOT. Source this script from inside the VTC repository." >&2
    return 1 2>/dev/null || exit 1
fi

export HF_HOME="${VTC_ROOT}/weights/hf_home"
export HF_HUB_CACHE="${VTC_ROOT}/weights/hf_home/hub"

mkdir -p \
    "${HF_HOME}" \
    "${HF_HUB_CACHE}" \
    "${VTC_ROOT}/weights/checkpoints" \
    "${VTC_ROOT}/weights/checkpoints/AutoGaze" \
    "${VTC_ROOT}/weights/checkpoints/onevision-encoder-large" \
    "${VTC_ROOT}/weights/checkpoints/LLaVA-OneVision-2-8B-Instruct"

echo "VTC_ROOT=${VTC_ROOT}"
echo "HF_HOME=${HF_HOME}"
echo "HF_HUB_CACHE=${HF_HUB_CACHE}"
echo "CHECKPOINTS=${VTC_ROOT}/weights/checkpoints"
