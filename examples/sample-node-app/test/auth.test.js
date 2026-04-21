'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const request = require('supertest');

// Set required env vars before requiring the app.
process.env.JWT_SIGNING_SECRET = 'a'.repeat(64);
process.env.JWT_ISSUER = 'ascend-sample';
process.env.JWT_AUDIENCE = 'ascend-users';

const jwt = require('jsonwebtoken');
const app = require('../src/index');

function token(expiresInSeconds = 300, subject = 'user-1') {
  const now = Math.floor(Date.now() / 1000);
  return jwt.sign(
    {
      sub: subject,
      iat: now,
      exp: now + expiresInSeconds,
      iss: process.env.JWT_ISSUER,
      aud: process.env.JWT_AUDIENCE,
    },
    process.env.JWT_SIGNING_SECRET,
    { algorithm: 'HS256' }
  );
}

test('valid token permits access', async () => {
  const res = await request(app)
    .get('/api/v1/users')
    .set('Authorization', `Bearer ${token()}`);
  assert.notEqual(res.status, 401);
});

test('expired token rejected', async () => {
  const res = await request(app)
    .get('/api/v1/users')
    .set('Authorization', `Bearer ${token(-1)}`);
  assert.equal(res.status, 401);
});

test('missing authorization rejected', async () => {
  const res = await request(app).get('/api/v1/users');
  assert.equal(res.status, 401);
});

test('wrong scheme rejected', async () => {
  const res = await request(app)
    .get('/api/v1/users')
    .set('Authorization', 'Basic something');
  assert.equal(res.status, 401);
});

test('garbage token rejected', async () => {
  const res = await request(app)
    .get('/api/v1/users')
    .set('Authorization', 'Bearer not-a-jwt');
  assert.equal(res.status, 401);
});
