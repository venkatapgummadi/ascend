/**
 * SQLite database access using better-sqlite3.
 * All queries are prepared / parameterized to prevent SQL injection.
 */

'use strict';

const Database = require('better-sqlite3');

const DB_PATH = process.env.DATABASE_URL || ':memory:';
const db = new Database(DB_PATH);

db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );
`);

// Prepared statements — safe from SQL injection.
const listUsersStmt = db.prepare(
  'SELECT id, username, email, created_at FROM users ORDER BY id LIMIT ?'
);

const getUserByIdStmt = db.prepare(
  'SELECT id, username, email, created_at FROM users WHERE id = ?'
);

function listUsers(limit = 50) {
  const clamped = Math.max(1, Math.min(100, Number.parseInt(limit, 10) || 50));
  return listUsersStmt.all(clamped);
}

function getUserById(id) {
  const parsed = Number.parseInt(id, 10);
  if (!Number.isFinite(parsed) || parsed <= 0) {
    return null;
  }
  return getUserByIdStmt.get(parsed) || null;
}

module.exports = { listUsers, getUserById };
