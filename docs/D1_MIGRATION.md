# D1 Migration Guide

Migrate from local SQLite to Cloudflare D1 with remote Worker API.

## Overview

- **D1 Database**: `file-organization-db` (UUID: `ec22b612-34da-48c7-ba44-df91875b296c`)
- **Worker API**: TypeScript/Hono server at `workers/file-org-api/`
- **Python Client**: HTTP adapter at `src/storage/graph_store_http.py`

## Step 1: Export Data

Export existing SQLite database:

```bash
python scripts/d1/export_to_d1.py \
  --db-path results/file_organization.db \
  --output results/d1_dump.sql
```

This generates `results/d1_dump.sql` with all data in D1-compatible format.

## Step 2: Deploy Schema to D1

Install Wrangler CLI:

```bash
npm install -g @cloudflare/wrangler
wrangler login
```

Deploy schema:

```bash
wrangler d1 execute file-organization-db --file scripts/d1/schema.sql
```

Verify tables:

```bash
wrangler d1 execute file-organization-db "SELECT name FROM sqlite_master WHERE type='table';"
```

## Step 3: Load Data (Optional)

If you have existing data:

```bash
wrangler d1 execute file-organization-db < results/d1_dump.sql
```

**Note**: This may take a while for large databases. Progress is reported in batches.

## Step 4: Deploy Worker API

Setup:

```bash
cd workers/file-org-api
npm install
wrangler deploy
```

This publishes the Worker to your Cloudflare account. It will output a URL like:
```
https://file-org-api.YOUR_ACCOUNT.workers.dev
```

### Local Development

Start local Worker:

```bash
cd workers/file-org-api
npm run dev
```

This starts a local server at `http://localhost:8787` that mirrors the D1 database.

## Step 5: Update Python Client

### Option A: Use HTTP Client (Recommended)

```python
from src.storage.graph_store_http import GraphStoreHTTP

# Production
store = GraphStoreHTTP("https://file-org-api.YOUR_ACCOUNT.workers.dev")

# Local development
store = GraphStoreHTTP("http://localhost:8787")

# Use same interface as GraphStore
file = store.add_file("/path/to/file.txt", "file.txt")
stats = store.get_statistics()
files = store.get_files(status=FileStatus.ORGANIZED)
```

### Option B: Switch Implementation in CLI

Edit `src/cli.py` to detect environment and switch:

```python
import os

if os.getenv('USE_D1'):
  from storage.graph_store_http import GraphStoreHTTP as GraphStore
else:
  from storage.graph_store import GraphStore
```

Then use:

```bash
export USE_D1=1
organize-files content --source ~/Downloads
```

## API Endpoints

### Files

- `GET /api/files?status=organized&limit=100&offset=0` – List files
- `GET /api/files/{id}` – Get single file
- `POST /api/files` – Create file
- `PUT /api/files/{id}/status` – Update status

### Categories

- `GET /api/categories` – Get tree
- `POST /api/categories` – Create category

### Statistics

- `GET /api/stats` – Overall stats
- `GET /api/search?q=query` – Full-text search

### Health

- `GET /health` – Health check

## Testing

Test local Worker:

```bash
# Start Worker
cd workers/file-org-api
npm run dev &

# Test API
curl http://localhost:8787/health
curl "http://localhost:8787/api/stats"
```

Test Python client:

```python
from src.storage.graph_store_http import GraphStoreHTTP

store = GraphStoreHTTP("http://localhost:8787")
print(store.health())
print(store.get_statistics())
```

## Troubleshooting

### D1 Connection Issues

Check database status:

```bash
wrangler d1 list
```

Verify binding in `wrangler.toml`:

```toml
[[d1_databases]]
binding = "DB"
database_name = "file-organization-db"
database_id = "ec22b612-34da-48c7-ba44-df91875b296c"
```

### Worker Deployment Fails

Check logs:

```bash
wrangler tail
```

Verify dependencies:

```bash
cd workers/file-org-api
npm install
npm run type-check
```

### Slow Data Migration

For large databases, split the dump:

```bash
# Split into 1000-line chunks
split -l 1000 results/d1_dump.sql results/d1_dump_

# Load each chunk
for file in results/d1_dump_*; do
  wrangler d1 execute file-organization-db < "$file"
done
```

## Performance Notes

### Query Performance

D1 SQLite is optimized for read-heavy workloads. Key indexes are pre-created:

- Files: `filename`, `status`, `organized_at`, `extension`
- Categories: `name`, `parent_id`
- Companies: `normalized_name`

For custom queries, create indexes via:

```bash
wrangler d1 execute file-organization-db "CREATE INDEX ... "
```

### Caching

Add caching headers to Worker responses:

```typescript
// In worker src/index.ts
c.header('Cache-Control', 'public, max-age=300')
```

### Rate Limiting

D1 limits concurrent writes. For bulk operations:

```python
import time

for file in files:
  store.add_file(...)
  time.sleep(0.1)  # Rate limit
```

## Rollback

To revert to local SQLite:

1. Stop using `GraphStoreHTTP`
2. Switch back to `GraphStore` with local database
3. Continue as before (data still in `results/file_organization.db`)

## Next Steps

1. Monitor Worker usage in Cloudflare Dashboard → Workers
2. Set up Worker Routes in Dashboard (optional, for custom domain)
3. Configure backups:
   ```bash
   wrangler d1 export file-organization-db > backups/d1_backup_$(date +%s).sql
   ```
4. Add authentication if exposing to team:
   - Add API key check in Worker
   - Use Bearer tokens or OAuth

## References

- [Cloudflare D1 Docs](https://developers.cloudflare.com/d1/)
- [Hono Framework](https://hono.dev/)
- [Wrangler CLI](https://developers.cloudflare.com/workers/wrangler/)
