const app = require('./app');
const PORT = process.env.PORT || 5000;

// Only start server if this file is run directly (not imported for testing)
if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
  });
}