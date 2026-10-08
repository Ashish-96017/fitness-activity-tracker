from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from activity_manager import ActivityManager
from analytics import FitnessAnalytics
from validation import validate_activity


class FitnessActivityTrackerTests(unittest.TestCase):
    def test_validation_success(self):
        result = validate_activity("2026-10-04", "running", "30", "5.5")
        self.assertEqual(result[:2], ("2026-10-04", "Running"))
        self.assertEqual(result[2:], (30.0, 5.5))

    def test_validation_failure(self):
        with self.assertRaises(ValueError):
            validate_activity("04-10-2026", "Running", "30", "5")

    def test_crud_and_search(self):
        with tempfile.TemporaryDirectory() as temp:
            manager = ActivityManager(Path(temp) / "activities.csv")
            activity_id = manager.add_activity("2026-10-04", "Running", 30, 5, "Tempo")
            self.assertEqual(len(manager.load()), 1)
            result = manager.search("tempo")
            self.assertEqual(int(result.iloc[0]["id"]), activity_id)
            manager.update_activity(activity_id, "2026-10-04", "Walking", 40, 3, "Recovery")
            self.assertEqual(manager.load().iloc[0]["activity_type"], "Walking")
            manager.delete_activity(activity_id)
            self.assertTrue(manager.load().empty)

    def test_analytics(self):
        df = pd.DataFrame(
            [
                {"id": 1, "date": "2026-10-03", "activity_type": "Running", "duration_minutes": 30, "distance_km": 5, "notes": ""},
                {"id": 2, "date": "2026-10-04", "activity_type": "Cycling", "duration_minutes": 60, "distance_km": 15, "notes": ""},
            ]
        )
        analytics = FitnessAnalytics(tempfile.mkdtemp())
        summary = analytics.summary(df)
        self.assertEqual(summary["activities"], 2)
        self.assertAlmostEqual(summary["distance"], 20)
        self.assertEqual(analytics.activity_comparison(df).shape[0], 2)


if __name__ == "__main__":
    unittest.main()
