-- Personal Vault Database Schema (Private to local node - Never synced over network)

CREATE TABLE IF NOT EXISTS local_secrets (
    key TEXT PRIMARY KEY,
    encrypted_value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS node_telemetry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id TEXT NOT NULL,
    node_role TEXT NOT NULL,      -- 'home_server' or 'laptop'
    cpu_percent REAL,
    ram_used_mb INTEGER,
    disk_free_gb REAL,
    network_mode TEXT DEFAULT 'live',
    battery_level INTEGER,        -- For laptop node
    tailscale_ip TEXT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS local_workspace_paths (
    alias TEXT PRIMARY KEY,
    absolute_path TEXT NOT NULL,
    access_policy TEXT DEFAULT 'read_only' -- 'read_only' or 'read_write'
);
