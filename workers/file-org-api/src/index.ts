import { Hono } from 'hono'
import { cors } from 'hono/cors'

interface Env {
  DB: D1Database
}

const app = new Hono<{ Bindings: Env }>()

// Enable CORS for the Python client
app.use(cors({
  origin: '*',
  allowMethods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowHeaders: ['Content-Type'],
}))

// Health check
app.get('/health', (c) => {
  return c.json({ status: 'ok', timestamp: new Date().toISOString() })
})

// =========================================================================
// File Endpoints
// =========================================================================

// Get all files with filters
app.get('/api/files', async (c) => {
  const db = c.env.DB
  const { status, category, company, extension, limit = '100', offset = '0' } = c.req.query()

  let query = 'SELECT * FROM files WHERE 1=1'
  const params: string[] = []

  if (status) {
    query += ' AND status = ?'
    params.push(status)
  }
  if (extension) {
    query += ' AND file_extension = ?'
    params.push(extension.toLowerCase())
  }

  query += ` ORDER BY organized_at DESC LIMIT ? OFFSET ?`
  params.push(limit, offset)

  try {
    const result = await db.prepare(query).bind(...params).all()
    return c.json(result)
  } catch (err) {
    return c.json({ error: 'Failed to query files', details: String(err) }, 500)
  }
})

// Get single file
app.get('/api/files/:id', async (c) => {
  const db = c.env.DB
  const id = c.req.param('id')

  try {
    const file = await db.prepare('SELECT * FROM files WHERE id = ?').bind(id).first()
    if (!file) return c.json({ error: 'File not found' }, 404)

    // Get relationships
    const categories = await db
      .prepare(`
        SELECT c.* FROM categories c
        JOIN file_categories fc ON c.id = fc.category_id
        WHERE fc.file_id = ?
      `)
      .bind(id)
      .all()

    const companies = await db
      .prepare(`
        SELECT c.* FROM companies c
        JOIN file_companies fc ON c.id = fc.company_id
        WHERE fc.file_id = ?
      `)
      .bind(id)
      .all()

    return c.json({
      ...file,
      categories: categories.results,
      companies: companies.results,
    })
  } catch (err) {
    return c.json({ error: 'Failed to fetch file', details: String(err) }, 500)
  }
})

// Add new file
app.post('/api/files', async (c) => {
  const db = c.env.DB
  const body = await c.req.json()

  const {
    id,
    canonical_id,
    filename,
    original_path,
    file_extension,
    status = 'pending',
    ...rest
  } = body

  if (!id || !filename || !original_path) {
    return c.json(
      { error: 'Missing required fields: id, filename, original_path' },
      400
    )
  }

  const columns = [
    'id',
    'canonical_id',
    'filename',
    'original_path',
    'file_extension',
    'status',
    ...Object.keys(rest),
  ]
  const placeholders = columns.map(() => '?').join(', ')
  const values = [id, canonical_id, filename, original_path, file_extension, status, ...Object.values(rest)]

  try {
    await db
      .prepare(`INSERT INTO files (${columns.join(', ')}) VALUES (${placeholders})`)
      .bind(...values)
      .run()

    return c.json({ id, message: 'File created' }, 201)
  } catch (err) {
    return c.json({ error: 'Failed to create file', details: String(err) }, 500)
  }
})

// Update file status
app.put('/api/files/:id/status', async (c) => {
  const db = c.env.DB
  const id = c.req.param('id')
  const { status, destination, reason } = await c.req.json()

  if (!status) {
    return c.json({ error: 'Missing required field: status' }, 400)
  }

  try {
    const result = await db
      .prepare(`
        UPDATE files
        SET status = ?, current_path = ?, organization_reason = ?, organized_at = CURRENT_TIMESTAMP
        WHERE id = ?
      `)
      .bind(status, destination || null, reason || null, id)
      .run()

    if (!result.success) {
      return c.json({ error: 'File not found' }, 404)
    }

    return c.json({ message: 'File status updated' })
  } catch (err) {
    return c.json({ error: 'Failed to update file', details: String(err) }, 500)
  }
})

// =========================================================================
// Category Endpoints
// =========================================================================

// Get category tree
app.get('/api/categories', async (c) => {
  const db = c.env.DB

  try {
    const categories = await db
      .prepare('SELECT * FROM categories ORDER BY level, name')
      .all()

    // Build tree
    const categoryMap = new Map()
    const roots: any[] = []

    for (const cat of categories.results) {
      const node = { ...cat, subcategories: [] }
      categoryMap.set(cat.id, node)
      if (!cat.parent_id) roots.push(node)
    }

    for (const cat of categories.results) {
      const node = categoryMap.get(cat.id)
      if (cat.parent_id) {
        const parent = categoryMap.get(cat.parent_id)
        if (parent) parent.subcategories.push(node)
      }
    }

    return c.json(roots)
  } catch (err) {
    return c.json({ error: 'Failed to fetch categories', details: String(err) }, 500)
  }
})

// Get or create category
app.post('/api/categories', async (c) => {
  const db = c.env.DB
  const { name, parent_name } = await c.req.json()

  if (!name) {
    return c.json({ error: 'Missing required field: name' }, 400)
  }

  try {
    // Check if exists
    let existing = await db
      .prepare('SELECT * FROM categories WHERE name = ?')
      .bind(name)
      .first()

    if (existing) return c.json(existing)

    // Get parent if specified
    let parentId = null
    let level = 0
    if (parent_name) {
      const parent = await db
        .prepare('SELECT id, level FROM categories WHERE name = ?')
        .bind(parent_name)
        .first()
      if (parent) {
        parentId = parent.id
        level = parent.level + 1
      }
    }

    // Create canonical ID (simple hash)
    const canonicalId = `urn:category:${Buffer.from(name).toString('base64')}`

    const result = await db
      .prepare(`
        INSERT INTO categories (canonical_id, name, parent_id, level)
        VALUES (?, ?, ?, ?)
      `)
      .bind(canonicalId, name, parentId, level)
      .run()

    const newCategory = await db
      .prepare('SELECT * FROM categories WHERE canonical_id = ?')
      .bind(canonicalId)
      .first()

    return c.json(newCategory, 201)
  } catch (err) {
    return c.json({ error: 'Failed to create category', details: String(err) }, 500)
  }
})

// =========================================================================
// Statistics Endpoints
// =========================================================================

// Get overall statistics
app.get('/api/stats', async (c) => {
  const db = c.env.DB

  try {
    const stats = await Promise.all([
      db.prepare('SELECT COUNT(*) as count FROM files').first(),
      db.prepare('SELECT COUNT(*) as count FROM files WHERE status = "organized"').first(),
      db.prepare('SELECT COUNT(*) as count FROM categories').first(),
      db.prepare('SELECT COUNT(*) as count FROM companies').first(),
    ])

    return c.json({
      total_files: stats[0]?.count || 0,
      organized_files: stats[1]?.count || 0,
      total_categories: stats[2]?.count || 0,
      total_companies: stats[3]?.count || 0,
    })
  } catch (err) {
    return c.json({ error: 'Failed to fetch statistics', details: String(err) }, 500)
  }
})

// Search files
app.get('/api/search', async (c) => {
  const db = c.env.DB
  const { q, limit = '50' } = c.req.query()

  if (!q) {
    return c.json({ error: 'Missing search query parameter: q' }, 400)
  }

  try {
    const results = await db
      .prepare(`
        SELECT * FROM files
        WHERE filename LIKE ? OR extracted_text LIKE ?
        LIMIT ?
      `)
      .bind(`%${q}%`, `%${q}%`, limit)
      .all()

    return c.json(results)
  } catch (err) {
    return c.json({ error: 'Search failed', details: String(err) }, 500)
  }
})

// 404
app.notFound((c) => {
  return c.json({ error: 'Not found' }, 404)
})

// Error handler
app.onError((err, c) => {
  console.error('Error:', err)
  return c.json({ error: 'Internal server error' }, 500)
})

export default app
