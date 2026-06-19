import unittest
from pathlib import Path


class PythonApiContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        repo_root = Path(__file__).resolve().parents[2]
        cls.server_source = (repo_root / 'backend-python' / 'server.py').read_text(encoding='utf-8')
        cls.profile_source = (repo_root / 'backend-python' / 'app' / 'routes' / 'profile.py').read_text(encoding='utf-8')

    def test_server_exposes_required_workout_endpoints(self):
        required = [
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
            '@app.post("/nutrition")',
        ]
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, self.server_source)

    def test_profile_router_exposes_update_endpoint(self):
        self.assertIn('router = APIRouter(prefix="/profile"', self.profile_source)
        self.assertIn('@router.put("/update")', self.profile_source)


if __name__ == '__main__':
    unittest.main()
