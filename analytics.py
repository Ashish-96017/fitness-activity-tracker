from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class FitnessAnalytics:
    """Calculations and Matplotlib reporting for fitness activity data."""

    def __init__(self, report_dir: str | Path = "reports") -> None:
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def summary(df: pd.DataFrame) -> dict[str, float | int | str]:
        if df.empty:
            return {
                "activities": 0,
                "distance": 0.0,
                "duration": 0.0,
                "average_speed": 0.0,
                "top_activity": "-",
            }
        distances = df["distance_km"].to_numpy(dtype=float)
        durations = df["duration_minutes"].to_numpy(dtype=float)
        total_hours = durations.sum() / 60.0
        avg_speed = distances.sum() / total_hours if total_hours else 0.0
        top_activity = df["activity_type"].value_counts().idxmax()
        return {
            "activities": int(len(df)),
            "distance": float(np.sum(distances)),
            "duration": float(np.sum(durations)),
            "average_speed": float(avg_speed),
            "top_activity": str(top_activity),
        }

    @staticmethod
    def activity_comparison(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame(columns=["activity_type", "distance_km", "duration_minutes", "count"])
        grouped = (
            df.groupby("activity_type", as_index=False)
            .agg(distance_km=("distance_km", "sum"), duration_minutes=("duration_minutes", "sum"), count=("id", "count"))
        )
        return grouped.sort_values("distance_km", ascending=False)

    @staticmethod
    def daily_trend(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame(columns=["date", "distance_km", "duration_minutes"])
        trend = (
            df.assign(date=pd.to_datetime(df["date"]))
            .groupby("date", as_index=False)
            .agg(distance_km=("distance_km", "sum"), duration_minutes=("duration_minutes", "sum"))
            .sort_values("date")
        )
        return trend

    @staticmethod
    def period_comparison(df: pd.DataFrame) -> dict[str, float]:
        """Compare the latest 7-day window with the preceding 7-day window."""
        if df.empty:
            return {"current_distance": 0.0, "previous_distance": 0.0, "change_pct": 0.0}
        work = df.copy()
        work["date"] = pd.to_datetime(work["date"])
        end = work["date"].max()
        current_start = end - pd.Timedelta(days=6)
        previous_start = end - pd.Timedelta(days=13)
        previous_end = end - pd.Timedelta(days=7)
        current = work[(work["date"] >= current_start) & (work["date"] <= end)]["distance_km"].sum()
        previous = work[(work["date"] >= previous_start) & (work["date"] <= previous_end)]["distance_km"].sum()
        change = ((current - previous) / previous * 100) if previous else (100.0 if current else 0.0)
        return {"current_distance": float(current), "previous_distance": float(previous), "change_pct": float(change)}

    def create_activity_comparison_chart(self, df: pd.DataFrame) -> Path:
        comparison = self.activity_comparison(df)
        fig, ax = plt.subplots(figsize=(9, 5.2))
        if comparison.empty:
            ax.text(0.5, 0.5, "No activity data available", ha="center", va="center", transform=ax.transAxes)
            ax.set_axis_off()
        else:
            bars = ax.bar(comparison["activity_type"], comparison["distance_km"])
            ax.set_title("Distance by Activity Type")
            ax.set_xlabel("Activity Type")
            ax.set_ylabel("Distance (km)")
            ax.grid(axis="y", alpha=0.25)
            for bar, value in zip(bars, comparison["distance_km"]):
                ax.text(bar.get_x() + bar.get_width() / 2, value, f"{value:.1f}", ha="center", va="bottom")
        fig.tight_layout()
        path = self.report_dir / "activity_comparison.png"
        fig.savefig(path, dpi=160, bbox_inches="tight")
        plt.close(fig)
        return path

    def create_daily_trend_chart(self, df: pd.DataFrame) -> Path:
        trend = self.daily_trend(df)
        fig, ax = plt.subplots(figsize=(9, 5.2))
        if trend.empty:
            ax.text(0.5, 0.5, "No activity data available", ha="center", va="center", transform=ax.transAxes)
            ax.set_axis_off()
        else:
            ax.plot(trend["date"], trend["distance_km"], marker="o", linewidth=2)
            ax.set_title("Daily Distance Trend")
            ax.set_xlabel("Date")
            ax.set_ylabel("Distance (km)")
            ax.grid(alpha=0.25)
            fig.autofmt_xdate()
        fig.tight_layout()
        path = self.report_dir / "activity_trend.png"
        fig.savefig(path, dpi=160, bbox_inches="tight")
        plt.close(fig)
        return path
