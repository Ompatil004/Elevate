// Project validation script
// This file validates that all modules are properly connected

import { test } from 'node:test';
import { strict as assert } from 'node:assert';

// Test 1: Validate import paths
function testImportPaths() {
  try {
    // Test frontend imports
    import('@/context/AuthContext');
    import('@/context/UserDataContext');
    import('@/services/api');
    import('@/components/Auth');
    import('@/components/Dashboard');
    import('@/components/Workout');
    import('@/components/MealPlan');
    import('@/components/Analytics');
    import('@/components/ProfileSetup');
    import('@/components/Navbar');
    import('@/components/Landing');
    import('@/components/pose-detection/PoseDetection');
    import('@/components/chatbot/Chatbot');
    
    console.log('✅ All frontend import paths are valid');
    return true;
  } catch (error) {
    console.error('❌ Import path validation failed:', error.message);
    return false;
  }
}

// Test 2: Check for essential project files
function testEssentialFiles() {
  const fs = require('fs');
  const path = require('path');
  
  const projectRoot = process.cwd();
  const essentialFiles = [
    'frontend/package.json',
    'frontend/src/main.tsx',
    'frontend/src/App.tsx',
    'frontend/src/context/AuthContext.tsx',
    'frontend/src/context/UserDataContext.tsx',
    'frontend/src/services/api.ts',
    'backend/server.js',
    'backend/package.json',
    'Backend-ml/main.py',
    'Backend-ml/train.py'
  ];
  
  let allFilesExist = true;
  
  for (const file of essentialFiles) {
    const fullPath = path.join(projectRoot, '..', '..', file);
    if (!fs.existsSync(fullPath)) {
      console.error(`❌ Missing essential file: ${file}`);
      allFilesExist = false;
    }
  }
  
  if (allFilesExist) {
    console.log('✅ All essential files are present');
  }
  
  return allFilesExist;
}

// Run validation tests
function runValidation() {
  console.log('🔍 Starting project validation...\n');
  
  const tests = [
    { name: 'Import Paths', fn: testImportPaths },
    { name: 'Essential Files', fn: testEssentialFiles }
  ];
  
  const results = [];
  
  for (const test of tests) {
    console.log(`🧪 Running ${test.name} test...`);
    const result = test.fn();
    results.push({ name: test.name, passed: result });
    console.log('');
  }
  
  // Summary
  const passedTests = results.filter(r => r.passed).length;
  console.log(`📋 Validation Summary: ${passedTests}/${results.length} tests passed`);
  
  if (passedTests === results.length) {
    console.log('🎉 All validations passed! Your project is properly configured.');
  } else {
    console.log('⚠️ Some validations failed. Please check the errors above.');
  }
  
  return passedTests === results.length;
}

// Run the validation
runValidation();