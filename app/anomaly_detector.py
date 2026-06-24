import pandas as pd
from datetime import datetime


def detect_anomalies(df):

    anomalies = []
    now = datetime.now()

    for _, row in df.iterrows():

        resolution_time = row["resolution_time_hrs"]

        # Long resolution time (> 48 hours)
        if pd.notna(resolution_time) and resolution_time > 48:
            anomalies.append({
                "ticket_id": row["ticket_id"],
                "priority": row["priority"],
                "status": row["status"],
                "resolution_time_hrs": resolution_time,
                "reason": "Long Resolution Time (> 48 hrs)"
            })

        # Critical unresolved
        if row["priority"] == "Critical" and row["status"] != "Resolved":
            anomalies.append({
                "ticket_id": row["ticket_id"],
                "priority": row["priority"],
                "status": row["status"],
                "reason": "Critical Unresolved Ticket"
            })

        # High/Critical ticket older than 24 hours
        if row["status"] != "Resolved" and pd.notna(row["created_at"]):
            age_hours = (now - row["created_at"]).total_seconds() / 3600
            if row["priority"] in ["High", "Critical"] and age_hours > 24:
                anomalies.append({
                    "ticket_id": row["ticket_id"],
                    "priority": row["priority"],
                    "status": row["status"],
                    "age_hours": round(age_hours, 1),
                    "reason": "High Priority Ticket Older Than 24 Hours"
                })

    return anomalies