# Cloudflare D1 Integration

Complete setup for hosting `file_organization.db` on Cloudflare D1 with edge-accessible Worker API.

## What's Included

✅ **D1 Database** – Managed SQLite on Cloudflare
✅ **Worker API** – TypeScript/Hono server for querying
✅ **Python HTTP Client** – Drop-in replacement for local GraphStore
✅ **Data Export Tool** – SQLite → D1 migration script
✅ **Documentation** – Full setup guide + quick start

## Architecture

```
Local Files (Python)
        ↓
GraphStoreHTTP (HTTP Client)
        ↓
Cloudflare Worker (TypeScript API)
        ↓
D1 Database (SQLite @ Edge)
```

## Quick Setup (5 minutes)

```bash
# 1. Export existing data
python scripts/d1/export_to_d1.py

# 2. Create D1 schema
wrangler d1 execute file-organization-db --file scripts/d1/schema.sql

# 3. Load data
wrangler d1 execute file-organization-db < results/d1_dump.sql

# 4. Deploy API
cd workers/file-org-api && npm install && wrangler deploy

# 5. Update Python to use remote API
export D1_API_URL="https://file-org-api.YOUR_ACCOUNT.workers.dev"
```

Usage in code:

```python
from src.storage.graph_store_http import GraphStoreHTTP

store = GraphStoreHTTP("https://file-org-api.YOUR_ACCOUNT.workers.dev")
file = store.add_file("/path/file.txt", "file.txt")
```

## File Structure

```
schema-org-file-system/
├── scripts/d1/
│   ├── schema.sql              # D1 table definitions
│   └── export_to_d1.py         # SQLite → SQL dump tool
├── workers/file-org-api/       # Cloudflare Worker (TypeScript)
│   ├── src/index.ts            # Hono API routes
│   ├── wrangler.toml           # Worker config
│   └── package.json
├── src/storage/
│   ├── graph_store.py          # Original local SQLite adapter
│   └── graph_store_http.py     # NEW: HTTP client adapter
└── docs/
    ├── D1_MIGRATION.md         # Full setup guide
    ├── D1_QUICKSTART.md        # TL;DR reference
    └── D1_README.md            # This file
```

## API Endpoints

All endpoints available at `https://file-org-api.YOUR_ACCOUNT.workers.dev`

### Files
- `GET /api/files?status=organized&limit=100` – List files
- `GET /api/files/{id}` – Get file by ID
- `POST /api/files` – Create file
- `PUT /api/files/{id}/status` – Update status

### Categories
- `GET /api/categories` – Hierarchy tree
- `POST /api/categories` – Create category

### Stats & Search
- `GET /api/stats` – Overall statistics
- `GET /api/search?q=query` – Full-text search
- `GET /health` – Health check

## Python Usage

### Create a Store Instance

```python
from src.storage.graph_store_http import GraphStoreHTTP
from src.storage.models import FileStatus

# Production
store = GraphStoreHTTP("https://file-org-api.YOUR_ACCOUNT.workers.dev")

# Local development
store = GraphStoreHTTP("http://localhost:8787")
```

### Common Operations

```python
# Add file
file = store.add_file(
  "/path/to/file.pdf",
  "file.pdf",
  file_size=1024,
  mime_type="application/pdf"
)

# Get files
files = store.get_files(
  status=FileStatus.ORGANIZED,
  extension=".pdf",
  limit=10
)

# Update status
store.update_file_status(
  file_id="hash...",
  status=FileStatus.ORGANIZED,
  destination="/Documents/..."
)

# Statistics
stats = store.get_statistics()
print(stats['total_files'], stats['organized_files'])

# Search
results = store.search_files("invoice", limit=20)

# Categories
categories = store.get_category_tree()
store.get_or_create_category("Financial", parent_name="Documents")
```

## Deployment

### Local Development

```bash
cd workers/file-org-api
npm install
npm run dev
# Opens http://localhost:8787
```

Test with Python:

```python
store = GraphStoreHTTP("http://localhost:8787")
print(store.health())  # Should return {"status": "ok", ...}
```

### Production Deployment

```bash
cd workers/file-org-api
wrangler deploy

# Output: Deployed to https://file-org-api.YOUR_ACCOUNT.workers.dev
```

### Custom Domain (Optional)

In Cloudflare Dashboard:
1. Workers → Routes → Create Route
2. Pattern: `api.your-domain.com/*`
3. Script: `file-org-api`
4. Update `D1_API_URL` environment variable

## Performance & Limits

| Feature | Limit | Notes |
|---------|-------|-------|
| **Query Size** | 1 MB | SQL result set |
| **Request Body** | 100 KB | Worker input |
| **Concurrent Writes** | High | SQLite with WAL enabled |
| **Geographic** | Global | CDN-cached read replicas |

D1 automatically distributes reads globally. Writes go to primary (ENAM).

## Troubleshooting

### Can't connect to API?

```bash
# Check Worker is running
wrangler tail

# Test locally
curl http://localhost:8787/health

# Check D1 binding
wrangler d1 list
```

### Database queries slow?

```bash
# Check indexes
wrangler d1 execute file-organization-db "
  SELECT name, sql FROM sqlite_master WHERE type='index'
"

# Add index if needed
wrangler d1 execute file-organization-db "
  CREATE INDEX idx_custom ON files(custom_column)
"
```

### Data migration failed?

```bash
# Check row count
wrangler d1 execute file-organization-db "SELECT COUNT(*) FROM files"

# Re-run export if needed
python scripts/d1/export_to_d1.py
```

## Migration from Local SQLite

1. **Backup** existing database:
   ```bash
   cp results/file_organization.db backups/local_backup_$(date +%s).db
   ```

2. **Export** data:
   ```bash
   python scripts/d1/export_to_d1.py
   ```

3. **Deploy** schema + data (steps in Quick Setup above)

4. **Test** API connectivity:
   ```bash
   curl https://file-org-api.YOUR_ACCOUNT.workers.dev/health
   ```

5. **Update** Python code to use `GraphStoreHTTP`

6. **Keep** local DB as fallback (can revert anytime)

## Monitoring

### View Logs

```bash
# Real-time Worker logs
wrangler tail

# Last 100 lines
wrangler tail --lines 100
```

### Check Metrics (Dashboard)

In Cloudflare Dashboard:
- Workers → Metrics → file-org-api
- Shows: Requests, errors, CPU time, bandwidth

### Database Stats

```bash
wrangler d1 execute file-organization-db "
  SELECT name, page_count * 4096 / 1024 / 1024 as size_mb
  FROM pragma_page_count() AS pages, pragma_page_size() AS psize
"
```

## Backup & Recovery

### Automated Backup

```bash
# Schedule this in cron/CI
wrangler d1 export file-organization-db > backups/d1_$(date +%Y%m%d_%H%M%S).sql
```

### Restore from Backup

```bash
wrangler d1 execute file-organization-db < backups/d1_20260320_112345.sql
```

## Cost

- **Free tier**: 25k reads/day + 100k writes/day + 5 GB storage
- **After**: $0.75 per million reads + $1.50 per million writes
- **Workers**: 100k requests/day free

See [Cloudflare Pricing](https://www.cloudflare.com/pricing/workers/)

## Related Resources

- Full Migration Guide: [D1_MIGRATION.md](./D1_MIGRATION.md)
- Quick Reference: [D1_QUICKSTART.md](./D1_QUICKSTART.md)
- API Code: `workers/file-org-api/src/index.ts`
- Python Client: `src/storage/graph_store_http.py`
- Schema: `scripts/d1/schema.sql`

## Support & Issues

- **Worker deployment fails**: Check `wrangler publish` errors, ensure `npm install` completed
- **D1 connection issues**: Verify database ID in `wrangler.toml`
- **Slow queries**: Check indexes, use `PRAGMA query_only` to inspect execution
- **Data sync issues**: Run export/import script again, clear Worker cache if needed
