# Integrating Repomix Bundles into Claude Workflows

Guide for efficient codebase reading and review operations using repomix bundles in Claude Code and related AI workflows.

---

## Bundle Selection Strategy

Choose bundles based on context window budget and task scope:

| Bundle | Size | Best For | Token Budget | Load Time |
|--------|------|----------|--------------|-----------|
| `repomix-docs.xml` | 179 KB | Architecture, dependency docs | ✓ Tight budgets | <1s |
| `repomix-git-ranked.xml` | 1.6 MB | Active development, code review | ✓ Most sessions | ~5s |
| `repo-compressed.xml` | 58 MB | Deep codebase analysis | ✗ Large window only | ~30s |
| `repomix.xml` | 59 MB | Full context exploration | ✗ Large window only | ~30s |
| `token-tree.txt` | 10 KB | Budget planning | ✓ Always load | <1s |

---

## Context Window Mathematics

**Available capacity (Claude Sonnet 4.6):**
- Raw context: 200K tokens
- System overhead: ~30-40K tokens (system prompt, tool defs, MCP schemas)
- CLAUDE.md files: ~500-2K tokens
- Output buffer: 33-45K tokens (reserved for Claude's response generation)
- **Usable capacity: ~110-120K tokens**

**Bundle token costs:**
- `token-tree.txt` breakpoints:
  - `src/`: ~8-12K tokens
  - `scripts/`: ~4-6K tokens
  - `tests/`: ~3-5K tokens
  - Full `repomix-git-ranked.xml`: ~35-45K tokens (prioritized recent files)

**Strategy:**
1. Load `token-tree.txt` first to understand per-directory costs
2. For code review: load `repomix-git-ranked.xml` (~40K tokens), leaving ~70-80K for task work
3. For architecture: load `repomix-docs.xml` (~3K tokens), leaving ~110K for deep exploration
4. Never load both `repomix.xml` AND additional large files in the same session

---

## Session Startup Pattern

**Optimal workflow for code review/feature work:**

```bash
# 1. Start session with repomix git-ranked bundle
#    (user loads the bundle at session start)

# 2. Claude Code reads token-tree.txt
#    → Understands file token costs
#    → Budgets reads strategically

# 3. For each task:
#    - Use Glob to find relevant files (no token cost)
#    - Use Grep to locate specific definitions (minimal cost)
#    - Read only target file sections with offset/limit
#    → Preserve context for task reasoning

# 4. End-of-session:
#    - Run `npm run repomix` to regenerate bundles
#    - Bundles capture latest code state
#    - Next session has fresh git-ranked snapshot
```

---

## Task-Specific Integration Patterns

### Pattern 1: Code Review (Most Common)

**Setup:**
```
Load: repomix-git-ranked.xml + token-tree.txt
Budget: 40K tokens for bundle, 70K for review logic
```

**Workflow:**
1. Claude reads git log from bundle (`gitlog-top20.txt`) to understand recent changes
2. Uses Grep to search for functions/classes mentioned in commit messages
3. Reads affected files only (1-3 at a time max)
4. Uses Glob to find related test files
5. Executes tests to validate changes

**Memory integration:**
- Store review checklist in `~/.claude/memory/code_review_checklist.md`
- Store project-specific patterns in `CLAUDE.md` (already done)
- No per-file context needed in memory (bundles refresh each session)

### Pattern 2: Refactoring / Large Changes

**Setup:**
```
Load: repomix-git-ranked.xml (recent files most important)
Budget: 45K for bundle, 65K for refactor planning
Use: Plan Mode (Shift+Tab)
```

**Workflow:**
1. Enter Plan Mode to analyze impact scope
2. Read structural summary from bundle
3. Grep for usages across codebase (no file reads)
4. Execute targeted reads for files requiring modification
5. Use subagents for parallel modification of independent modules

**Subagent pattern:**
```typescript
// Main session orchestrates; subagents execute in parallel contexts
Agent {
  subagent_type: "general-purpose"
  description: "Refactor database layer to use async/await"
  prompt: """
  Refactor src/storage/graph_store.py to use async/await.
  Context bundle: [relevant excerpt from repomix-git-ranked.xml]
  Related tests: [search results from main session]
  """
}
```

### Pattern 3: Documentation & Architecture Questions

**Setup:**
```
Load: repomix-docs.xml only
Budget: 3K tokens for bundle, 110K for exploration/analysis
```

**Workflow:**
1. Read docs-only bundle to understand project structure
2. Use Explore agent with Glob/Grep to find specific implementations
3. Deep-dive reads into source files as needed
4. Cross-reference with project README and CLAUDE.md

**Why docs-only here:**
- No code overhead in context
- Full breathing room for understanding and explanation
- Docs bundle embeds CLAUDE.md for project context

---

## Memory System Integration

### Session-Persistent State

Store in `~/.claude/projects/-Users-alyshialedlie-schema-org-file-system/memory/`:

**File: `code_review_context.md`**
```markdown
---
name: Code Review Context
type: reference
---
Recent active modules (from git-ranked bundle):
- src/cli.py (100+ commits)
- scripts/file_organizer_content_based.py (80+ commits)
- tests/e2e/ (integration tests)

Known pain points:
- OCR reliability varies by image quality
- CLIP model loading has cold-start overhead
- Graph store migration path for canonical IDs
```

**File: `user_code_review_style.md`**
```markdown
---
name: Code Review Style
type: feedback
---
User prefers:
- Concrete examples over general advice
- Test-driven approach (write test first)
- No over-engineering; minimal feature creep
- Concise comments; no verbose docstrings
```

### What NOT to store in memory:
- File content (bundles refresh each session)
- Recent change history (git log is in bundles)
- File paths (read from current directory state)
- Code snippets (grep them fresh)

---

## Plan Mode for Large Tasks

**When to use:** Multi-file changes, architectural decisions, refactors

**Example:** Refactoring error handling across src/ and scripts/

```
1. User: "Refactor error tracking to use Sentry consistently"

2. Claude activates Plan Mode (Shift+Tab)
   - Thinks: Which files import error_tracking.py?
   - Thinks: Where is sentry DSN configured?
   - Thinks: What tests validate error flows?

3. Plan output (italic gray):
   "Identified 12 files touching error handling.
    Test coverage: 8/12 files have tests.
    Impact scope: Medium (3-4 hours estimated)"

4. Plan approval/refinement with user

5. Execution (no more planning overhead):
   - Reads only planned files
   - Uses allocated context for task logic
   - No re-analyzing scope mid-task
```

**Token savings:** Plan mode thinking is separate from conversation tokens; actual execution uses 40-50% fewer tokens because scope is pre-decided.

---

## Subagent Coordination for Parallel Work

**Scenario:** Add new classifier category to 5 independent modules

**Orchestration:**
```bash
# Main session (you):
# - Reads repomix-git-ranked.xml
# - Identifies 5 classifier modules
# - Creates 5 independent tasks

# Spawn subagents in parallel:
Agent("Refactor org classifier") {
  prompt: """
  Module: src/classifiers/org_classifier.py
  Add: "startup" category
  Tests: tests/unit/test_org_classifier.py
  Context: [excerpt from git-ranked bundle for this module]
  """
}

Agent("Refactor person classifier") {
  # Similar structure, independent context
}

# ... 3 more agents

# Main session waits for all to complete
# Then integrates results (no rework needed)
```

**Benefits:**
- Each subagent operates in a fresh 200K token window
- No contention for context with main session
- Results integrate cleanly because tasks are independent
- Parallelism: 5 tasks complete in ~1/5 the time

---

## MCP Integration for Dynamic Bundle Generation

### Option 1: Pre-Generated Bundles (Current)

**Pros:** Bundles always available, no computation overhead, static reference
**Cons:** Requires manual regeneration or post-commit hooks

**Setup already in place:**
- `generate-repomix-git-ranked.sh` creates `repomix-git-ranked.xml`
- `generate-repomix-docs.sh` creates `repomix-docs.xml`
- `token-tree.sh` creates `token-tree.txt`

**Recommended next step:** Add post-commit hook in `.claude/settings.json`
```json
{
  "hooks": {
    "post_commit": {
      "command": "bash scripts/repomix/generate-repomix-git-ranked.sh . docs/repomix/repomix-git-ranked.xml",
      "enabled": true
    }
  }
}
```

### Option 2: MCP Server for On-Demand Generation

**For future scaling** (when repo exceeds 200K tokens):

```json
{
  "mcp_servers": {
    "repomix": {
      "command": "npx",
      "args": ["-y", "repomix", "--mcp"]
    }
  }
}
```

**Claude can then:**
```typescript
// Request bundle scoped to specific directory
repomix.pack_codebase({
  include: ["src/classifiers/**"],
  exclude: ["**/__pycache__"],
  output: "scoped-bundle.xml"
})

// Returns only classifier code (~5K tokens vs 40K for full git-ranked)
```

### Option 3: Semantic Search MCP (Very Large Repos)

**For repos > 80K tokens:**
```json
{
  "mcp_servers": {
    "zilliz_context": {
      "command": "python",
      "args": ["-m", "zilliz_claude_context"]
    }
  }
}
```

**Claude can:**
```typescript
// Retrieve only top-5 relevant code chunks
zilliz_context.search("error handling", {
  top_k: 5,
  include_tests: true
})

// Returns ~2-3K tokens of highest-relevance code
```

---

## Hooks Integration for Automated Regeneration

**Current setup** (from your `~/.claude/CLAUDE.md`):
- `post-tool.ts` routes Write/Edit/Bash operations
- `post-commit-review` hook runs after commits

**Enhancement: Auto-regen bundles on commit**

Add to `handlers/post-tool.ts` after `post-commit-review`:

```typescript
// After commit succeeds, refresh git-ranked bundle
if (toolName === 'Bash' && toolResult.includes('commit created')) {
  await exec(
    'bash scripts/repomix/generate-repomix-git-ranked.sh . docs/repomix/repomix-git-ranked.xml'
  )
  // Emit OTEL span for observability
  instrumentHook('repomix.regenerated', {
    'bundle': 'git-ranked',
    'timestamp': new Date().toISOString()
  })
}
```

**Result:**
- Every commit automatically updates `repomix-git-ranked.xml`
- Next session always has fresh file-change rankings
- No manual `npm run repomix` needed

---

## Efficient Read Operations Checklist

✓ **Before starting a session:**
- [ ] Load `token-tree.txt` first (budget planning)
- [ ] Load `repomix-git-ranked.xml` (default bundle)
- [ ] Check git status to understand what changed since last session

✓ **During code review:**
- [ ] Use Glob to find files (0 tokens)
- [ ] Use Grep to locate definitions (minimal tokens, high signal)
- [ ] Read only relevant sections with offset/limit
- [ ] Load one file at a time; read results before next read
- [ ] Keep "currently in context" files to 2-3 max

✓ **For large refactors:**
- [ ] Use Plan Mode to scope changes upfront
- [ ] Identify independent modules → spawn subagents
- [ ] Each subagent loads only its module's repomix excerpt
- [ ] Main session coordinates integration

✓ **For architecture questions:**
- [ ] Load `repomix-docs.xml` instead of full bundle
- [ ] Use Explore agent to investigate specific areas
- [ ] Save findings to project memory for future sessions

✓ **End of session:**
- [ ] If made changes, run `npm run repomix`
- [ ] Next session will have updated git-ranked bundle

---

## Performance Benchmarks

| Operation | Token Cost | Duration | Notes |
|-----------|-----------|----------|-------|
| Load `repomix-git-ranked.xml` | ~35-40K | ~2-3s | Default; prioritizes recent files |
| Load `repomix-docs.xml` | ~3K | <1s | Fast; use for docs questions |
| Load `token-tree.txt` | ~200 | <1s | Always load first |
| Read one source file (500 lines) | ~1.2-1.5K | <1s | Use offset/limit for large files |
| Grep search (10 matches) | ~200-300 | <1s | No file injection, minimal cost |
| Glob pattern search | 0 | <1s | Zero token cost |
| Subagent spawn | 0 | ~1s | Each gets fresh 200K window |

---

## Troubleshooting

**"Context window nearly full" warning appears**
→ Stop reading new files; use Grep instead
→ Check token-tree.txt to see which files are expensive
→ Switch to subagent pattern for remaining work

**Git-ranked bundle is stale**
→ Run `npm run repomix` to regenerate
→ Or enable post-commit hook (see Hooks section)

**Bundle generation times out**
→ Set `REPOMIX_TIMEOUT_SECONDS=180` (default: 120)
→ Use `repomix-docs.xml` for faster iterations (excludes code)

**"Too many files loaded" in a single read operation**
→ Use Grep to find specific definition first
→ Then read only the target file section with offset/limit
→ Avoid reading entire directories of code at once

---

## Summary: Recommended Workflow

1. **Start session:** Load `token-tree.txt` + `repomix-git-ranked.xml`
2. **Understand scope:** Grep for definitions, Glob for file locations
3. **Read strategically:** One file at a time, offset/limit for large files
4. **Plan big changes:** Use Plan Mode before multi-file edits
5. **Parallelize:** Spawn subagents for independent modules
6. **Store learnings:** Update project memory (code patterns, review style)
7. **End session:** Run `npm run repomix` to refresh bundles

**Result:** 40-50% fewer wasted tokens, faster code review cycles, better scalability as codebase grows.
