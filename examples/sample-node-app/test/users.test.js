'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const request = require('supertest');

process.env.JWT_SIGNING_SECRET = 'a'.repeat(64);
process.env.JWT_ISSUER = 'ascend-sample';
process.env.JWT_AUDIENCE = 'ascend-users';

const app = require('../src/index');

test('health endpoint returns 200', async () => {
  const res = await request(app).get('/healthz');
  assert.equal(res.status, 200);
  assert.deepEqual(res.body, { status: 'ok' });
});

test('readyz endpoint returns 200', async () => {
  const res = await request(app).get('/readyz');
  assert.equal(res.status, 200);
});

test('users endpoint requires auth', async () => {
  const res = await request(app).get('/api/v1/users');
  assert.equal(res.status, 401);
});

test('unknown route returns 404', async () => {
  const res = await request(app).get('/does-not-exist');
  assert.equal(res.status, 404);
});
