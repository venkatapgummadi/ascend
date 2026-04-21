'use strict';

const express = require('express');
const { authenticate } = require('../auth');
const { listUsers, getUserById } = require('../db');

const router = express.Router();

router.get('/', authenticate, (req, res) => {
  const limit = Number.parseInt(req.query.limit || '50', 10);
  if (!Number.isFinite(limit) || limit < 1) {
    return res.status(400).json({ error: 'limit must be a positive integer' });
  }
  const users = listUsers(limit);
  return res.json({ users });
});

router.get('/:id', authenticate, (req, res) => {
  const user = getUserById(req.params.id);
  if (!user) {
    return res.status(404).json({ error: 'user not found' });
  }
  return res.json({ user });
});

module.exports = router;
