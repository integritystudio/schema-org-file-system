# Repomix Documentation

Generated repository bundles for analysis and reference.

## Generated Files

| File | Source Script | Description |
|------|---|---|
| `repomix.xml` | `generate-repomix.sh` | Full repository bundle with all files, metadata, and directory structure |
| `repomix-docs.xml` | `generate-repomix-docs.sh` | Documentation-focused bundle (excludes repomix artifacts, code, and generated files) |
| `repomix-git-ranked.xml` | `generate-repomix-git-ranked.sh` | Bundle ranked by git change frequency with diffs and commit logs from recent commits |
| `repo-compressed.xml` | `generate-repo-compressed.sh` | Compressed/optimized bundle for reduced file size and faster processing |
| `token-tree.txt` | `generate-token-tree.sh` | Token count analysis and distribution across directories |
| `gitlog-top20.txt` | Git log extraction | Top 20 commits with affected files and metadata |

## Generation

All files are auto-generated during the build/documentation pipeline. Scripts are invoked by CI/CD workflows or manual regeneration commands. See `scripts/repomix/` for individual script details.

### Configuration Files
- `repomix.config.json` - Base configuration with ignore patterns
- `repomix-docs.config.json` - Docs-specific include rules and filters
