const mongoose = require('mongoose');
require('dotenv').config();

console.log('Connecting to MongoDB...');

async function testConnection() {
  try {
    await mongoose.connect(process.env.MONGODB_URI, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });
    console.log('✅ MongoDB connection successful');
    
    // Test with a simple operation
    const db = mongoose.connection.db;
    const result = await db.admin().ping();
    console.log('✅ Database ping successful:', result.ok);
    
    mongoose.connection.close();
    console.log('Connection closed');
  } catch (err) {
    console.error('❌ MongoDB connection failed:', err.message);
  }
}

testConnection();