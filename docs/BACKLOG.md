# Backlog

Derived from session sweep of uncommitted changes and codebase state.
Context: repomix-output.xml (scripts/ directory snapshot, 2026-02-25).

## Open Items

### Migrate CLIP backend to `open-clip-torch`

**Status:** Open
**Priority:** Medium
**Effort:** 3–4 hrs
**Depends on:** Batch CLIP inference cache layer fix (Phase 1–3)

Replace the current dual CLIP implementations (`transformers.CLIPModel` in `scripts/file_organizer_content_based.py` + `src/analyzers/image_analyzer.py`, and `sentence-transformers` in `scripts/shared/clip_utils.py`) with a single `open-clip-torch` backend.

**Motivation:**
- Eliminates two separate model instances loading the same weights
- Direct tensor API (`model.encode_image(pixel_values)`) removes DataLoader overhead present in `sentence-transformers`, improving small-to-medium batch latency
- Native fp16 support via `model.to(torch.float16)` — resolves the fp16 open item in `docs/deep-learning-analysis-03-27-2026.md` simultaneously
- Opens path to larger model variants (ViT-L/14, ViT-H/14) without code changes

**Scope:**
- Replace `SentenceTransformer('clip-ViT-B-32')` in `scripts/shared/clip_utils.py:CLIPClassifier` with `open_clip.create_model_and_transforms('ViT-B-32', pretrained='openai')`
- Replace `CLIPModel.from_pretrained` + `CLIPProcessor.from_pretrained` in `scripts/file_organizer_content_based.py` and `src/analyzers/image_analyzer.py` with the same `open_clip` instance (via `CLIPClassifier.get_instance()`)
- Update `_run_batch()` to use `model.encode_image()` + `model.encode_text()` directly
- Add `open-clip-torch` to `pyproject.toml`; remove `sentence-transformers` if no other consumers remain
- Update `scripts/shared/constants.py:CLIP_BATCH_SIZE` if optimal batch size changes

**Out of scope:** model variant upgrade (ViT-B-32 → ViT-L/14) — treat as a separate backlog item.
