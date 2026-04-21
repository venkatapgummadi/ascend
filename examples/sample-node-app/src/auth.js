/**
 * JWT authentication middleware for Express.
 * Uses HS256 with strict expiry enforcement.
 */

'use strict';

const jwt = require('jsonwebtoken');

function getSecret() {
  const secret = process.env.JWT_SIGNING_SECRET;
  if (!secret || secret.length < 32) {
    throw new Error(
      'JWT_SIGNING_SECRET env var must be set to a value >= 32 characters. '
        + 'Configure via your secrets manager.'
    );
  }
  return secret;
}

function authenticate(req, res, next) {
  const header = req.headers.authorization || '';
  if (!header.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'unauthorized' });
  }

  const token = header.slice('Bearer '.length).trim();
  if (!token) {
    return res.status(401).json({ error: 'unauthorized' });
  }

  try {
    const claims = jwt.verify(token, getSecret(), {
      algorithms: ['HS256'],
      // Require the expected registered claims.
      issuer: process.env.JWT_ISSUER,
      audience: process.env.JWT_AUDIENCE,
    });

    // Additional defense — verify expiry explicitly.
    if (!claims.exp || Date.now() / 1000 >= claims.exp) {
      return res.status(401).json({ error: 'unauthorized' });
    }

    req.user = { id: claims.sub };
    return next();
  } catch (err) {
    // Avoid leaking details about why the token failed.
    return res.status(401).json({ error: 'unauthorized' });
  }
}

module.exports = { authenticate };
