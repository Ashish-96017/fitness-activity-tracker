from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

import pandas as pd

from activity_manager import ActivityManager
from analytics import FitnessAnalytics
from validation import validate_activity

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "activities.csv"
REPORT_DIR = BASE_DIR / "reports"


class FitnessApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Fitness Activity Tracker & Progress Analyzer")
        self.geometry("1120x720")
        self.minsize(980, 650)
        self.configure(padx=12, pady=12)

        self.manager = ActivityManager(DATA_FILE)
        self.analytics = FitnessAnalytics(REPORT_DIR)
        self.selected_id: int | None = None

        self._build_styles()
        self._build_header()
        self._build_notebook()
        self._build_dashboard()
        self._build_activity_form()
        self._build_records()
        self._build_analytics()
        self._clear_form()
        self._refresh_all()

    def _build_styles(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Title.TLabel", font=("Segoe UI", 19, "bold"))
        style.configure("Sub.TLabel", font=("Segoe UI", 10))
        style.configure("Card.TFrame", relief="solid", borderwidth=1, padding=14)
        style.configure("CardValue.TLabel", font=("Segoe UI", 20, "bold"))
        style.configure("CardLabel.TLabel", font=("Segoe UI", 9))
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))

    def _build_header(self) -> None:
        frame = ttk.Frame(self)
        frame.pack(fill="x", pady=(0, 10))
        ttk.Label(frame, text="FITNESS ACTIVITY TRACKER", style="Title.TLabel").pack(anchor="w")
        ttk.Label(frame, text="Record • Analyze • Compare • Visualize", style="Sub.TLabel").pack(anchor="w")

    def _build_notebook(self) -> None:
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)
        self.dashboard_tab = ttk.Frame(self.notebook, padding=12)
        self.form_tab = ttk.Frame(self.notebook, padding=12)
        self.records_tab = ttk.Frame(self.notebook, padding=12)
        self.analytics_tab = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.form_tab, text="Add / Edit Activity")
        self.notebook.add(self.records_tab, text="Activity Records")
        self.notebook.add(self.analytics_tab, text="Analytics & Reports")

    def _build_dashboard(self) -> None:
        cards = ttk.Frame(self.dashboard_tab)
        cards.pack(fill="x")
        self.card_vars = {}
        items = [("activities", "Activities"), ("distance", "Distance (km)"), ("duration", "Duration (min)"), ("average_speed", "Avg Speed (km/h)"), ("top_activity", "Top Activity")]
        for idx, (key, label) in enumerate(items):
            card = ttk.Frame(cards, style="Card.TFrame")
            card.grid(row=0, column=idx, sticky="nsew", padx=4)
            cards.columnconfigure(idx, weight=1)
            var = tk.StringVar(value="-")
            self.card_vars[key] = var
            ttk.Label(card, textvariable=var, style="CardValue.TLabel").pack()
            ttk.Label(card, text=label, style="CardLabel.TLabel").pack(pady=(4, 0))

        tips = ttk.Frame(self.dashboard_tab, padding=8)
        tips.pack(fill="both", expand=True)
        ttk.Label(tips, text="Project capabilities", font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(14, 6))
        text = (
            "• Record walking, running and cycling sessions\n"
            "• Persist data in CSV using Pandas\n"
            "• Search and filter by activity, date and notes\n"
            "• Calculate totals, averages and period changes\n"
            "• Generate two Matplotlib reports: daily trend and activity comparison\n"
            "• Apply input validation and exception handling"
        )
        ttk.Label(tips, text=text, justify="left", font=("Segoe UI", 11), padding=8).pack(anchor="w")

    def _build_activity_form(self) -> None:
        wrapper = ttk.Frame(self.form_tab)
        wrapper.pack(anchor="n", pady=25)
        labels = ["Date (YYYY-MM-DD)", "Activity Type", "Duration (minutes)", "Distance (km)", "Notes"]
        self.form_vars = [tk.StringVar() for _ in labels]
        for r, label in enumerate(labels):
            ttk.Label(wrapper, text=label).grid(row=r, column=0, sticky="w", padx=8, pady=8)
        ttk.Entry(wrapper, textvariable=self.form_vars[0], width=36).grid(row=0, column=1, padx=8, pady=8)
        self.activity_combo = ttk.Combobox(wrapper, textvariable=self.form_vars[1], values=["Walking", "Running", "Cycling"], state="readonly", width=33)
        self.activity_combo.grid(row=1, column=1, padx=8, pady=8)
        ttk.Entry(wrapper, textvariable=self.form_vars[2], width=36).grid(row=2, column=1, padx=8, pady=8)
        ttk.Entry(wrapper, textvariable=self.form_vars[3], width=36).grid(row=3, column=1, padx=8, pady=8)
        ttk.Entry(wrapper, textvariable=self.form_vars[4], width=36).grid(row=4, column=1, padx=8, pady=8)

        buttons = ttk.Frame(wrapper)
        buttons.grid(row=5, column=0, columnspan=2, pady=16)
        ttk.Button(buttons, text="Save Activity", command=self._save_activity, style="Accent.TButton").pack(side="left", padx=5)
        ttk.Button(buttons, text="Clear", command=self._clear_form).pack(side="left", padx=5)
        ttk.Button(buttons, text="Cancel Edit", command=self._clear_form).pack(side="left", padx=5)
        ttk.Label(wrapper, text="Select a record from Activity Records to edit/delete it.", font=("Segoe UI", 9)).grid(row=6, column=0, columnspan=2, pady=4)

    def _build_records(self) -> None:
        filters = ttk.Frame(self.records_tab)
        filters.pack(fill="x", pady=(0, 10))
        self.query_var = tk.StringVar()
        self.filter_type_var = tk.StringVar(value="All")
        self.filter_start_var = tk.StringVar()
        self.filter_end_var = tk.StringVar()
        ttk.Label(filters, text="Search").grid(row=0, column=0, padx=4)
        ttk.Entry(filters, textvariable=self.query_var, width=22).grid(row=0, column=1, padx=4)
        ttk.Label(filters, text="Type").grid(row=0, column=2, padx=4)
        ttk.Combobox(filters, textvariable=self.filter_type_var, values=["All", "Walking", "Running", "Cycling"], state="readonly", width=12).grid(row=0, column=3, padx=4)
        ttk.Label(filters, text="From").grid(row=0, column=4, padx=4)
        ttk.Entry(filters, textvariable=self.filter_start_var, width=12).grid(row=0, column=5, padx=4)
        ttk.Label(filters, text="To").grid(row=0, column=6, padx=4)
        ttk.Entry(filters, textvariable=self.filter_end_var, width=12).grid(row=0, column=7, padx=4)
        ttk.Button(filters, text="Apply Filter", command=self._refresh_records).grid(row=0, column=8, padx=5)
        ttk.Button(filters, text="Reset", command=self._reset_filters).grid(row=0, column=9, padx=5)

        columns = [("id", "ID", 60), ("date", "Date", 100), ("activity_type", "Activity", 120), ("duration_minutes", "Duration (min)", 120), ("distance_km", "Distance (km)", 120), ("notes", "Notes", 300)]
        table_frame = ttk.Frame(self.records_tab)
        table_frame.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(table_frame, columns=[c[0] for c in columns], show="headings", height=17)
        for key, title, width in columns:
            self.tree.heading(key, text=title)
            self.tree.column(key, width=width, anchor="center" if key != "notes" else "w")
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", self._load_selected_record)

        actions = ttk.Frame(self.records_tab)
        actions.pack(fill="x", pady=10)
        ttk.Button(actions, text="Edit Selected", command=self._load_selected_record).pack(side="left", padx=4)
        ttk.Button(actions, text="Delete Selected", command=self._delete_selected).pack(side="left", padx=4)
        ttk.Label(actions, text="Tip: double-click a row to edit.", font=("Segoe UI", 9)).pack(side="right")

    def _build_analytics(self) -> None:
        top = ttk.Frame(self.analytics_tab)
        top.pack(fill="x")
        ttk.Label(top, text="Report generation", font=("Segoe UI", 13, "bold")).pack(anchor="w")
        ttk.Label(top, text="Charts are saved automatically in the reports/ folder.").pack(anchor="w", pady=(2, 10))
        ttk.Button(top, text="Generate Both Reports", command=self._generate_reports, style="Accent.TButton").pack(anchor="w")

        self.analytics_text = tk.Text(self.analytics_tab, height=19, wrap="word", state="disabled", font=("Consolas", 10))
        self.analytics_text.pack(fill="both", expand=True, pady=12)

    def _read_form(self) -> tuple[str, str, float, float, str]:
        date, activity_type, duration, distance = self.form_vars[:4]
        clean_date, clean_type, clean_duration, clean_distance = validate_activity(
            date.get(), activity_type.get(), duration.get(), distance.get()
        )
        notes = self.form_vars[4].get().strip()
        return clean_date, clean_type, clean_duration, clean_distance, notes

    def _save_activity(self) -> None:
        try:
            date, activity_type, duration, distance, notes = self._read_form()
            if self.selected_id is None:
                self.manager.add_activity(date, activity_type, duration, distance, notes)
                messagebox.showinfo("Saved", "Activity recorded successfully.")
            else:
                self.manager.update_activity(self.selected_id, date, activity_type, duration, distance, notes)
                messagebox.showinfo("Updated", "Activity updated successfully.")
            self._clear_form()
            self._refresh_all()
            self.notebook.select(self.records_tab)
        except (ValueError, RuntimeError, KeyError) as exc:
            messagebox.showerror("Validation / Storage Error", str(exc))
        except Exception as exc:  # defensive exception handling for viva requirement
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {exc}")

    def _clear_form(self) -> None:
        self.selected_id = None
        self.form_vars[0].set(datetime.now().strftime("%Y-%m-%d"))
        self.form_vars[1].set("Walking")
        self.form_vars[2].set(30)
        self.form_vars[3].set(2.5)
        self.form_vars[4].set("")

    def _get_selected_id(self) -> int | None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select a record", "Please select an activity record first.")
            return None
        values = self.tree.item(selected[0], "values")
        return int(values[0])

    def _load_selected_record(self, _event=None) -> None:
        activity_id = self._get_selected_id()
        if activity_id is None:
            return
        df = self.manager.load()
        row = df[df["id"] == activity_id]
        if row.empty:
            messagebox.showerror("Not Found", "The selected activity no longer exists.")
            return
        item = row.iloc[0]
        self.selected_id = activity_id
        self.form_vars[0].set(str(item["date"]))
        self.form_vars[1].set(str(item["activity_type"]))
        self.form_vars[2].set(str(item["duration_minutes"]))
        self.form_vars[3].set(str(item["distance_km"]))
        self.form_vars[4].set(str(item["notes"]))
        self.notebook.select(self.form_tab)

    def _delete_selected(self) -> None:
        activity_id = self._get_selected_id()
        if activity_id is None:
            return
        if not messagebox.askyesno("Confirm Delete", f"Delete activity ID {activity_id}?"):
            return
        try:
            self.manager.delete_activity(activity_id)
            self._refresh_all()
            messagebox.showinfo("Deleted", "Activity deleted successfully.")
        except (KeyError, RuntimeError) as exc:
            messagebox.showerror("Delete Error", str(exc))

    def _refresh_records(self) -> None:
        try:
            start = self.filter_start_var.get().strip() or None
            end = self.filter_end_var.get().strip() or None
            if start:
                start = validate_activity(start, "Walking", "1", "1")[0]
            if end:
                end = validate_activity(end, "Walking", "1", "1")[0]
            df = self.manager.search(self.query_var.get(), self.filter_type_var.get(), start, end)
            for child in self.tree.get_children():
                self.tree.delete(child)
            for _, row in df.iterrows():
                self.tree.insert("", "end", values=(int(row["id"]), row["date"], row["activity_type"], f"{float(row['duration_minutes']):.1f}", f"{float(row['distance_km']):.2f}", row["notes"]))
        except (ValueError, RuntimeError) as exc:
            messagebox.showerror("Filter Error", str(exc))

    def _reset_filters(self) -> None:
        self.query_var.set("")
        self.filter_type_var.set("All")
        self.filter_start_var.set("")
        self.filter_end_var.set("")
        self._refresh_records()

    def _generate_reports(self) -> None:
        try:
            df = self.manager.load()
            self.analytics.create_activity_comparison_chart(df)
            self.analytics.create_daily_trend_chart(df)
            self._refresh_analytics_text(df)
            messagebox.showinfo("Reports Generated", "Both Matplotlib reports were generated in the reports/ folder.")
        except Exception as exc:
            messagebox.showerror("Report Error", str(exc))

    def _refresh_analytics_text(self, df: pd.DataFrame) -> None:
        summary = self.analytics.summary(df)
        comparison = self.analytics.activity_comparison(df)
        period = self.analytics.period_comparison(df)
        lines = [
            "FITNESS PROGRESS ANALYSIS",
            "=" * 70,
            f"Total activities       : {summary['activities']}",
            f"Total distance        : {summary['distance']:.2f} km",
            f"Total duration        : {summary['duration']:.1f} minutes ({summary['duration'] / 60:.2f} hours)",
            f"Average speed         : {summary['average_speed']:.2f} km/h",
            f"Most frequent activity: {summary['top_activity']}",
            "",
            "ACTIVITY COMPARISON",
            "-" * 70,
        ]
        if comparison.empty:
            lines.append("No records available.")
        else:
            for _, row in comparison.iterrows():
                lines.append(f"{row['activity_type']:<12} | {int(row['count']):>3} sessions | {row['distance_km']:>7.2f} km | {row['duration_minutes']:>7.1f} min")
        lines.extend(
            [
                "",
                "7-DAY PERIOD COMPARISON",
                "-" * 70,
                f"Latest 7-day distance   : {period['current_distance']:.2f} km",
                f"Previous 7-day distance : {period['previous_distance']:.2f} km",
                f"Change                   : {period['change_pct']:+.1f}%",
                "",
                "Generated reports:",
                f"  • {REPORT_DIR / 'activity_trend.png'}",
                f"  • {REPORT_DIR / 'activity_comparison.png'}",
            ]
        )
        self.analytics_text.configure(state="normal")
        self.analytics_text.delete("1.0", "end")
        self.analytics_text.insert("1.0", "\n".join(lines))
        self.analytics_text.configure(state="disabled")

    def _refresh_all(self) -> None:
        self._refresh_records()
        df = self.manager.load()
        summary = self.analytics.summary(df)
        self.card_vars["activities"].set(str(summary["activities"]))
        self.card_vars["distance"].set(f"{summary['distance']:.1f}")
        self.card_vars["duration"].set(f"{summary['duration']:.0f}")
        self.card_vars["average_speed"].set(f"{summary['average_speed']:.1f}")
        self.card_vars["top_activity"].set(str(summary["top_activity"]))
        self.analytics.create_activity_comparison_chart(df)
        self.analytics.create_daily_trend_chart(df)
        self._refresh_analytics_text(df)


def seed_demo_data(manager: ActivityManager) -> None:
    """Create a realistic demo dataset only when the CSV is empty."""
    if not manager.load().empty:
        return
    demo = [
        ("2026-09-20", "Walking", 35, 2.8, "Morning walk"),
        ("2026-09-21", "Running", 28, 4.2, "Easy run"),
        ("2026-09-22", "Cycling", 45, 12.5, "Evening cycling"),
        ("2026-09-24", "Walking", 50, 4.0, "Campus walk"),
        ("2026-09-25", "Running", 32, 5.0, "Interval practice"),
        ("2026-09-27", "Cycling", 55, 15.8, "Weekend ride"),
        ("2026-09-28", "Walking", 40, 3.1, "Recovery day"),
        ("2026-09-29", "Running", 35, 5.4, "Tempo run"),
        ("2026-10-01", "Cycling", 48, 13.6, "Evening ride"),
        ("2026-10-02", "Walking", 42, 3.5, "Low intensity"),
        ("2026-10-03", "Running", 30, 4.8, "Steady run"),
        ("2026-10-04", "Cycling", 60, 17.2, "Long ride"),
    ]
    for item in demo:
        manager.add_activity(*item)


if __name__ == "__main__":
    manager = ActivityManager(DATA_FILE)
    seed_demo_data(manager)
    app = FitnessApp()
    app.mainloop()
