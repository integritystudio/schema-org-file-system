# D1 Quick Start

Fast-track setup for file-organization D1 hosting.

## TL;DR

```bash
# 1. Export data
python scripts/d1/export_to_d1.py

# 2. Setup D1 schema
wrangler d1 execute file-organization-db --file scripts/d1/schema.sql

# 3. Load data (optional)
wrangler d1 execute file-organization-db < results/d1_dump.sql

# 4. Deploy Worker API
cd workers/file-org-api
npm install
wrangler deploy

# 5. Use in Python
export D1_API_URL="https://file-org-api.YOUR_ACCOUNT.workers.dev"

# Then:
from src.storage.graph_store_http import GraphStoreHTTP
store = GraphStoreHTTP(os.getenv('D1_API_URL'))
```

## Database Info

| Property | Value |
|----------|-------|
| **Database** | `file-organization-db` |
| **ID** | `ec22b612-34da-48c7-ba44-df91875b296c` |
| **Account** | Alyshia@integritystudio.ai |
| **Region** | ENAM (Eastern North America) |

## Worker Configuration

**File**: `workers/file-org-api/wrangler.toml`

Update for production:

```toml
[env.production]
name = "file-org-api-prod"
route = "api.file-org.dev/*"
zone_id = "YOUR_ZONE_ID"  # Get from dashboard
```

Deploy to production:

```bash
wrangler deploy --env production
```

## URLs

| Environment | URL |
|-------------|-----|
| **Local Dev** | `http://localhost:8787` |
| **Staging** | `https://file-org-api.YOUR_ACCOUNT.workers.dev` |
| **Production** | `https://api.file-org.dev` (after domain config) |

## Environment Variables

```bash
# .env or shell
export D1_API_URL="https://file-org-api.YOUR_ACCOUNT.workers.dev"
export D1_API_KEY="optional-auth-key"  # Add in Worker if needed
```

## Common Operations

### Check API Health

```bash
curl https://file-org-api.YOUR_ACCOUNT.workers.dev/health
```

### Query Files

```bash
curl "https://file-org-api.YOUR_ACCOUNT.workers.dev/api/files?status=organized&limit=10"
```

### Python: List Organized Files

```python
from src.storage.graph_store_http import GraphStoreHTTP
from src.storage.models import FileStatus

store = GraphStoreHTTP("https://file-org-api.YOUR_ACCOUNT.workers.dev")
files = store.get_files(status=FileStatus.ORGANIZED, limit=10)
print(len(files), "organized files")
```

### View Database

```bash
wrangler d1 execute file-organization-db "SELECT COUNT(*) as total FROM files;"
```

### Backup Database

```bash
wrangler d1 export file-organization-db > backups/backup_$(date +%Y%m%d_%H%M%S).sql
```

## Debugging

### Worker Logs

```bash
wrangler tail
```

### Database Logs

```bash
wrangler d1 execute file-organization-db "PRAGMA query_only = true; SELECT * FROM sqlite_master;"
```

### Test Connection

```python
import requests

response = requests.get("https://file-org-api.YOUR_ACCOUNT.workers.dev/health")
print(response.json())  # Should show: {"status": "ok", "timestamp": "..."}
```

## Cost Estimates

| Operation | Rate | Notes |
|-----------|------|-------|
| **D1 Reads** | Free tier: 25k/day | Scales per million after |
| **D1 Writes** | Free tier: 100k/day | Scales per million after |
| **Worker Requests** | Free tier: 100k/day | Included CPU |
| **Data Storage** | Free tier: 5 GB | Included with D1 |

See [Cloudflare Pricing](https://www.cloudflare.com/en-gb/pricing/workers/d1/) for details.

## Support

- API Issues: Check `wrangler tail` logs
- DB Issues: Use `wrangler d1 execute file-organization-db "SELECT ..."`
- Python Client: See `src/storage/graph_store_http.py`
- Full Guide: `docs/D1_MIGRATION.md`
