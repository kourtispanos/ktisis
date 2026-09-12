import os
import sys
import tempfile
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "database"))

import db
from create_db import create_tables

REAL_DB_PATH = os.path.abspath(os.path.join(PROJECT_ROOT, "ktisis.db"))


class DBTestCase(unittest.TestCase):
    """
    Κάθε τεστ τρέχει σε δική του προσωρινή βάση. Υπάρχουν ρητοί έλεγχοι
    που σταματούν αμέσως το τεστ αν κάτι προσπαθήσει να συνδεθεί στο
    πραγματικό ktisis.db, αντί να αφήνουν να γίνει σιωπηλά.
    """

    def setUp(self):
        fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)

        assert os.path.abspath(self.temp_db_path) != REAL_DB_PATH, \
            "Το προσωρινό path ταυτίζεται με την πραγματική βάση - διακοπή."

        self.original_db_path = db.DB_PATH
        db.DB_PATH = self.temp_db_path

        assert os.path.abspath(db.DB_PATH) != REAL_DB_PATH, \
            "db.DB_PATH δείχνει στην πραγματική βάση μετά την αλλαγή - διακοπή."

        create_tables()

        assert os.path.abspath(db.DB_PATH) != REAL_DB_PATH, \
            "db.DB_PATH άλλαξε στην πραγματική βάση μετά το create_tables() - διακοπή."

    def tearDown(self):
        db.DB_PATH = self.original_db_path
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)
