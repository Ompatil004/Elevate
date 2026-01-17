const http = require('http');

// Simple test to check if the server is responding
function testServer() {
  const options = {
    hostname: 'localhost',
    port: 5000,
    path: '/',
    method: 'GET'
  };

  const req = http.request(options, (res) => {
    console.log(`Status: ${res.statusCode}`);
    res.on('data', (chunk) => {
      console.log(`Response: ${chunk}`);
    });
    res.on('end', () => {
      console.log('Request completed');
    });
  });

  req.on('error', (e) => {
    console.error(`Problem with request: ${e.message}`);
  });

  req.end();
}

testServer();