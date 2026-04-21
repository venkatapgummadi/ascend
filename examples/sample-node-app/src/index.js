/**
 * Sample Node.js Express application for demonstrating ASCEND integration.
 */

'use strict';

const express = require('express');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');

const healthRouter = require('./routes/health');
const usersRouter = require('./routes/users');

const app = express();

// Security headers — Helmet sets a sensible defaults set.
app.use(helmet({
  contentSecurityPolicy: {
    useDefaults: true,
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'"],
      objectSrc: ["'none'"],
      upgradeInsecureRequests: [],
    },
  },
  strictTransportSecurity: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true,
  },
}));

// Rate limiting — prevents brute-force against auth endpoints.
const globalLimiter = rateLimit({
  windowMs: 60 * 1000,      // 1 minute
  max: 300,                 // 300 requests per IP per minute
  standardHeaders: true,
  legacyHeaders: false,
});
app.use(globalLimiter);

// Body parsing with a size limit (defense against memory exhaustion).
app.use(express.json({ limit: '100kb' }));

// Routes
app.use('/', healthRouter);
app.use('/api/v1/users', usersRouter);

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'not found' });
});

// Centralized error handler — never leaks stack traces in production.
// eslint-disable-next-line no-unused-vars
app.use((err, req, res, next) => {
  const requestId = req.headers['x-request-id'] || 'unknown';
  console.error(`[${requestId}] ${err.stack}`);
  const message = process.env.NODE_ENV === 'production'
    ? 'internal server error'
    : err.message;
  res.status(err.status || 500).json({ error: message, requestId });
});

const PORT = Number.parseInt(process.env.PORT || '3000', 10);

if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`Listening on port ${PORT}`);
  });
}

module.exports = app;
