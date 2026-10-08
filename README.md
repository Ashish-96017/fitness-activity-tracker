# Fitness Activity Tracker & Progress Analyzer

A Tkinter-based Python application for recording walking, running and cycling activities, storing records persistently in CSV, filtering/searching records, calculating progress metrics, comparing activity types and periods, and generating Matplotlib visual reports.

## Technical requirements covered

- Python functions and data structures
- CSV file handling for persistent storage
- 4 user-defined modules: `main.py`, `activity_manager.py`, `analytics.py`, `validation.py`
- Pandas and NumPy for storage processing and calculations
- Tkinter GUI with dashboard, forms, records, search/filter and analytics
- Matplotlib visualizations: daily distance trend and activity comparison
- Input validation and exception handling
- Unit tests in `tests/test_activity_tracker.py`

## Run

```bash
pip install -r requirements.txt
python main.py
```

The first run seeds a small demonstration dataset automatically when `data/activities.csv` is empty. Delete the CSV and relaunch to restore the demo data.

## Screens / workflow

1. Dashboard: quick progress metrics.
2. Add / Edit Activity: validated activity entry.
3. Activity Records: search, filter, edit and delete.
4. Analytics & Reports: comparisons, period analysis and two PNG reports.

## Output files

- `reports/activity_trend.png`
- `reports/activity_comparison.png`
- `data/activities.csv`

## Test

```bash
python -m unittest discover -s tests -v
```
