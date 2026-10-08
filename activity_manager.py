from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd

COLUMNS = ["id", "date", "activity_type", "duration_minutes", "distance_km", "notes"]


class ActivityManager:
    """Persistent CRUD operations for fitness activities using CSV + Pandas."""

    def __init__(self, data_file: str | Path = "data/activities.csv") -> None:
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.data_file.exists():
            pd.DataFrame(columns=COLUMNS).to_csv(self.data_file, index=False)

    def load(self) -> pd.DataFrame:
        try:
            df = pd.read_csv(self.data_file)
        except (OSError, pd.errors.EmptyDataError) as exc:
            raise RuntimeError(f"Could not read activity data: {exc}") from exc

        for column in COLUMNS:
            if column not in df.columns:
                df[column] = ""
        df = df[COLUMNS].copy()
        if not df.empty:
            df["id"] = pd.to_numeric(df["id"], errors="coerce").fillna(0).astype(int)
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
            df["duration_minutes"] = pd.to_numeric(df["duration_minutes"], errors="coerce").fillna(0.0)
            df["distance_km"] = pd.to_numeric(df["distance_km"], errors="coerce").fillna(0.0)
            df["activity_type"] = df["activity_type"].astype(str).str.title()
            df["notes"] = df["notes"].fillna("").astype(str)
        return df

    def save(self, df: pd.DataFrame) -> None:
        df = df.reindex(columns=COLUMNS)
        try:
            df.to_csv(self.data_file, index=False)
        except OSError as exc:
            raise RuntimeError(f"Could not save activity data: {exc}") from exc

    def _next_id(self, df: pd.DataFrame) -> int:
        return int(df["id"].max()) + 1 if not df.empty else 1

    def add_activity(
        self,
        date: str,
        activity_type: str,
        duration_minutes: float,
        distance_km: float,
        notes: str = "",
    ) -> int:
        df = self.load()
        new_id = self._next_id(df)
        row = pd.DataFrame(
            [
                {
                    "id": new_id,
                    "date": date,
                    "activity_type": activity_type,
                    "duration_minutes": duration_minutes,
                    "distance_km": distance_km,
                    "notes": notes,
                }
            ]
        )
        self.save(pd.concat([df, row], ignore_index=True))
        return new_id

    def update_activity(
        self,
        activity_id: int,
        date: str,
        activity_type: str,
        duration_minutes: float,
        distance_km: float,
        notes: str = "",
    ) -> None:
        df = self.load()
        matches = df.index[df["id"] == activity_id].tolist()
        if not matches:
            raise KeyError(f"Activity ID {activity_id} not found")
        idx = matches[0]
        df.loc[idx, COLUMNS[1:]] = [date, activity_type, duration_minutes, distance_km, notes]
        self.save(df)

    def delete_activity(self, activity_id: int) -> None:
        df = self.load()
        new_df = df[df["id"] != activity_id].copy()
        if len(new_df) == len(df):
            raise KeyError(f"Activity ID {activity_id} not found")
        self.save(new_df)

    def search(
        self,
        query: str = "",
        activity_type: str = "All",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        df = self.load()
        if df.empty:
            return df

        result = df.copy()
        if query.strip():
            q = query.strip().lower()
            result = result[
                result["activity_type"].str.lower().str.contains(q, na=False)
                | result["notes"].str.lower().str.contains(q, na=False)
            ]
        if activity_type and activity_type != "All":
            result = result[result["activity_type"] == activity_type]
        if start_date:
            result = result[pd.to_datetime(result["date"]) >= pd.to_datetime(start_date)]
        if end_date:
            result = result[pd.to_datetime(result["date"]) <= pd.to_datetime(end_date)]
        return result.sort_values(["date", "id"], ascending=[False, False]).reset_index(drop=True)
