// Test MongoDB connection
const mongoose = require('mongoose');
require('dotenv').config();

async function testConnection() {
  try {
    // Connect to MongoDB
    await mongoose.connect(process.env.MONGODB_URI);

    console.log('✅ Successfully connected to MongoDB Atlas');

    // Test creating a simple document
    const testSchema = new mongoose.Schema({
      name: String,
      createdAt: { type: Date, default: Date.now }
    });

    const TestModel = mongoose.model('TestConnection', testSchema);

    // Insert a test document
    const testDoc = new TestModel({ name: 'Connection Test' });
    await testDoc.save();

    console.log('✅ Successfully inserted test document');

    // Retrieve the test document
    const retrievedDoc = await TestModel.findOne({ name: 'Connection Test' });
    console.log('✅ Successfully retrieved test document:', retrievedDoc);

    // Clean up - remove the test document
    await TestModel.deleteMany({ name: 'Connection Test' });
    console.log('✅ Successfully cleaned up test document');

    // Close the connection
    await mongoose.connection.close();
    console.log('✅ Connection closed');

  } catch (error) {
    console.error('❌ Error connecting to MongoDB:', error.message);
  }
}

testConnection();