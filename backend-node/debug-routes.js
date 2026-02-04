// Simple test to verify the route exists
const express = require('express');
const app = express();

app.use(express.json());

// Load the users route
const usersRoute = require('./routes/users');
app.use('/api/users', usersRoute);

// Test the route directly
app.get('/test', (req, res) => {
  res.json({ message: 'Server is running and route is loaded' });
});

// Print all registered routes for debugging
app.get('/routes', (req, res) => {
  const routes = [];
  for (let layer of app._router.stack) {
    if (layer.route) {
      routes.push({
        path: layer.route.path,
        methods: layer.route.methods
      });
    }
  }
  res.json(routes);
});

const PORT = 3001;
app.listen(PORT, () => {
  console.log(`Test server running on port ${PORT}`);
  console.log(`Test endpoints:`);
  console.log(`GET http://localhost:${PORT}/test`);
  console.log(`GET http://localhost:${PORT}/routes`);
  console.log(`POST http://localhost:${PORT}/api/users/save (requires auth token)`);
});