const fs = require('fs');
const path = require('path');

const serverPath = path.join(__dirname, 'server.js');
const serverCode = fs.readFileSync(serverPath, 'utf8');

const requiredSnippets = [
  "app.use('/api/auth', authRoutes)",
  "app.use('/api/profile', profileRoutes)",
  "app.use('/api/users', usersRoutes)",
  "app.use('/api/admin', checkAdminIP)",
  "app.use('/api/admin', (req, res, next) =>",
  "return adminApiLimiter(req, res, next);",
  "app.use('/api/admin', adminAuthRoutes)",
  "app.use('/api/admin/users', adminUserRoutes)",
  "app.use('/api/admin/system', adminSystemRoutes)",
  "app.use('/api/admin/content', adminContentRoutes)",
  "app.get('/health'",
];

const missing = requiredSnippets.filter((snippet) => !serverCode.includes(snippet));

if (missing.length > 0) {
  console.error('Persistence QA failed. Missing server route wiring:');
  missing.forEach((snippet) => console.error(` - ${snippet}`));
  process.exit(1);
}

console.log('Persistence QA passed: route persistence wiring looks correct.');
