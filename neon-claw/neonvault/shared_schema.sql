-- Shared Vault Database Schema (Synchronized across authorized nodes)

CREATE TABLE IF NOT EXISTS shared_memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT 'general',
    content TEXT NOT NULL,
    embedding BLOB,
    confidence REAL DEFAULT 1.0,
    tags TEXT DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_shared_memories_user ON shared_memories(user_id);
CREATE INDEX IF NOT EXISTS idx_shared_memories_category ON shared_memories(category);

-- Reusable Skills acquired and synthesized by Hermes Agent
CREATE TABLE IF NOT EXISTS reusable_skills (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    code_definition TEXT NOT NULL,
    parameters_schema TEXT NOT NULL,
    created_by_agent TEXT NOT NULL DEFAULT 'hermes',
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cross-Device Distributed Task History
CREATE TABLE IF NOT EXISTS task_history (
    id TEXT PRIMARY KEY,
    prompt TEXT NOT NULL,
    origin_node TEXT NOT NULL DEFAULT 'phone_telegram',
    assigned_worker TEXT NOT NULL DEFAULT 'home_server',
    status TEXT NOT NULL DEFAULT 'queued',
    result_summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
