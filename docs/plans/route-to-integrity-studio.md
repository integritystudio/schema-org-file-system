# Fix: Route logo.png to Organization/IntegrityStudio

## Context
`logo.png` on Desktop is misclassified as `GameAssets/Sprites` because a catch-all pattern `^[a-z]+$` (single lowercase word) at line 2560 matches before the actual logo check at line 2575 runs.

## File
`scripts/file_organizer_content_based.py`

## Changes

### 1. Add branding terms to the exclusion set (line 2556)
Add `'logo'`, `'logos'`, `'logotype'`, `'favicon'`, `'brandmark'`, `'wordmark'` to `data_viz_terms` (or rename to a broader exclusion set) so the single-word game asset catch-all skips them.

### 2. Update logo check destination (lines 2575-2578)
Change from:
```python
return ('media', 'photos_logos', None, [])
```
To:
```python
return ('organization', 'other', 'Integrity Studio', [])
```

This routes `logo.png`, `logotype.png`, and any `*logo*` image to `Organization/IntegrityStudio/`.

## Verification
```bash
source venv/bin/activate && organize-files content --source ~/Desktop --dry-run --limit 5
```
Confirm `logo.png` → `~/Documents/Organization/Integrity Studio/logo.png` (not GameAssets).
