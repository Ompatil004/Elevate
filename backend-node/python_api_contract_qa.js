const fs = require('fs');
const path = require('path');

const repoRoot = path.join(__dirname, '..');
const frontendApiPath = path.join(repoRoot, 'frontend', 'src', 'api.js');
const pythonServerPath = path.join(repoRoot, 'backend-python', 'server.py');
const pythonProfilePath = path.join(repoRoot, 'backend-python', 'app', 'routes', 'profile.py');

const frontendApi = fs.readFileSync(frontendApiPath, 'utf8');
const pythonServer = fs.readFileSync(pythonServerPath, 'utf8');
const pythonProfile = fs.readFileSync(pythonProfilePath, 'utf8');

const frontendMustUse = [
  "FitnessAPI.put('/profile/update'",
  "FitnessAPI.get('/api/weekly-plan'",
  "FitnessAPI.get('/api/swap-options'",
  "FitnessAPI.post('/api/swap-rest-to-workout'",
  "FitnessAPI.post('/api/swap-workout-to-rest'",
  "FitnessAPI.post('/workout'",
  "FitnessAPI.post('/workout/async'",
  "FitnessAPI.get(`/workout/status/${jobId}`)",
  "FitnessAPI.post('/workout/cache/invalidate'",
  "FitnessAPI.post('/nutrition/daily'",
];

const pythonMustExposeInServer = [
  '@app.post("/workout")',
  '@app.post("/workout/async")',
  '@app.get("/workout/status/{job_id}")',
  '@app.post("/workout/cache/invalidate")',
  '@app.get("/api/models/status")',
  '@app.post("/api/models/warmup")',
  '@app.get("/api/weekly-plan")',
  '@app.get("/api/swap-options")',
  '@app.post("/api/swap-rest-to-workout")',
  '@app.post("/api/swap-workout-to-rest")',
];

const pythonMustExposeInProfileRouter = [
  'router = APIRouter(prefix="/profile"',
  '@router.put("/update")',
];

const missingFrontend = frontendMustUse.filter((snippet) => !frontendApi.includes(snippet));
const missingServer = pythonMustExposeInServer.filter((snippet) => !pythonServer.includes(snippet));
const missingProfile = pythonMustExposeInProfileRouter.filter((snippet) => !pythonProfile.includes(snippet));

if (missingFrontend.length || missingServer.length || missingProfile.length) {
  console.error('Python API contract QA failed.');

  if (missingFrontend.length) {
    console.error('Missing frontend contract calls:');
    missingFrontend.forEach((snippet) => console.error(` - ${snippet}`));
  }

  if (missingServer.length) {
    console.error('Missing Python server contract endpoints:');
    missingServer.forEach((snippet) => console.error(` - ${snippet}`));
  }

  if (missingProfile.length) {
    console.error('Missing Python profile router endpoints:');
    missingProfile.forEach((snippet) => console.error(` - ${snippet}`));
  }

  process.exit(1);
}

console.log('Python API contract QA passed: frontend and backend routes are aligned.');
