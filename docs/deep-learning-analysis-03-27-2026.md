# Schema.org File System — ML/AI Audit

**Date:** 2026-03-27
**Version:** 1.3.0
**Scope:** 191 files | ~305K LOC

---

## ML/AI Stack

| Component | Technology | Status |
|-----------|-----------|--------|
| Vision classification | CLIP (`openai/clip-vit-base-patch32`) | Conditional (optional dep) |
| OCR | Tesseract via `pytesseract` | Core |
| PDF → image | `pdf2image` | Optional |
| Device detection | MPS → CUDA → CPU auto-select | Solid |
| Cost tracking | Custom decorator/context manager | Built-in |

---

## Top Issues

### High Priority

- **No model caching** — CLIP reloads from disk on every run (~10–15 sec penalty). Needs singleton or module-level cache.
- **Single-image inference** — no batch processing; ~3–5 sec per image with no GPU parallelization. Estimated 4–8x gain with batching.
- **No lock file** — `requirements.txt` uses `>=` bounds with no `pip.lock`; installs are not reproducible.

### Medium Priority

- **God class** — `file_organizer_content_based.py` is 2,691 LOC with a 1,577-LOC `ContentBasedFileOrganizer` class. A refactor plan already exists in `docs/ARCHITECTURE_REFACTOR.md`.
- **N+1 queries** — no `joinedload` on graph relationships; category queries hit the DB per file.
- **No fp16/int8 quantization** — CLIP runs full fp32 (~2 GB RAM). Half-precision would cut that in half with ~2x speedup.
- **No retry on OCR failure** — failed extractions are silently skipped.

### Low Priority

- No CI/CD (only manual GitHub Pages deploy)
- No benchmark suite — performance regressions go undetected
- CLIP embeddings not cached by content hash — duplicate files re-processed

---

## What's Good

- Graceful degradation on all optional deps (AI, docs, monitoring)
- ~85% type annotation coverage, mypy configured
- Graph storage schema is solid — confidence scores on all ML predictions, SHA-256 dedup IDs
- 12 test files (unit + integration + 6 Playwright E2E specs)
- Sentry error tracking with decorator/context manager patterns
- Cost-per-feature ROI tracking built into the pipeline

---

## Recommended Next Steps

| Priority | Task | Effort | Status |
|----------|------|--------|--------|
| 1 | Add `pip-compile` lock file | 1–2 hrs | Done |
| 2 | CLIP singleton/module-level cache | 2–4 hrs | Done |
| 3 | Batch CLIP inference (8–32 images) | 6–8 hrs | Open |
| 4 | `joinedload` on graph queries | 2–3 hrs | Open |
| 5 | Split `file_organizer_content_based.py` per refactor plan | 1–2 days | Open |
| 6 | fp16 quantization for CLIP | 1–2 hrs | Open |
