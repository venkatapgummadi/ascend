'use strict';

const express = require('express');
const router = express.Router();

router.get('/healthz', (req, res) => {
  res.status(200).json({ status: 'ok' });
});

router.get('/readyz', (req, res) => {
  // In a real app, verify DB and downstream service reachability here.
  res.status(200).json({ status: 'ready' });
});

module.exports = router;
