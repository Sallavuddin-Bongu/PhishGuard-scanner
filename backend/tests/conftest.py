import os
import sys
import tempfile
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))

# Test settings only. These are not real secrets.
_tmp = tempfile.mkdtemp(prefix="phishguard_test_")
os.environ["JWT_SECRET_KEY"] = "test-only-secret-key-not-for-production"
os.environ["ADMIN_EMAIL"] = "admin@example.com"
os.environ["DATABASE_URL"] = f"sqlite:///{Path(_tmp) / 'test.db'}"
