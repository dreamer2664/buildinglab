#!/usr/bin/env bash
# secret_scan.sh — Fails if any secret, token, ntfy topic, or .env fragment
# appears anywhere under buildinglab/crystal or buildinglab/agents/paxton (§2.4, §26).
# Adapted from daedalus (underworks/tools/secret_scan.sh, Appendix A).
set -uo pipefail

R="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "$R/.." && pwd)"
cd "$REPO_ROOT"

if [ -z "${NTFY_TOPIC:-}" ]; then
  [ -r /home/user/.private/paxton.env ] && set -a && . /home/user/.private/paxton.env && set +a
fi

FOUND=0
hit() { printf 'SECRET  %-14s %s\n' "$1" "$2"; FOUND=1; }

TARGETS=$(find crystal agents/paxton -type f 2>/dev/null | sort -u)

while IFS= read -r f; do
  [ -f "$f" ] || continue
  if [ -n "${NTFY_TOPIC:-}" ] && grep -qF "$NTFY_TOPIC" "$f" 2>/dev/null; then hit "NTFY_TOPIC" "$f"; fi
  if [ -n "${GITHUB_TOKEN:-}" ] && grep -qF "$GITHUB_TOKEN" "$f" 2>/dev/null; then hit "GITHUB_TOKEN" "$f"; fi
  if [ -n "${CHATCODE_TOKEN:-}" ] && grep -qF "$CHATCODE_TOKEN" "$f" 2>/dev/null; then hit "CHATCODE_TOKEN" "$f"; fi
  if grep -qEoh 'github_pat_[A-Za-z0-9_]{60,}|gh[pousr]_[A-Za-z0-9]{30,}' "$f" 2>/dev/null; then hit "PAT-SHAPE" "$f"; fi
  if grep -qEoh 'cy-paxton-[0-9a-f]{32}' "$f" 2>/dev/null; then hit "TOPIC-SHAPE" "$f"; fi
done <<< "$TARGETS"

if [ "$FOUND" -eq 0 ]; then
  echo "secret_scan: CLEAN — no topic, token or PAT found under crystal/ or agents/paxton/"
  exit 0
fi
echo "secret_scan: FAIL — secret detected! Purge immediately before committing." >&2
exit 1
