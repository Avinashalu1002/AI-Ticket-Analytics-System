from datetime import datetime

def detect_anomalies(df):

    anomalies = []

    for _, row in df.iterrows():

        resolution_time = row.get("resolution_time_hrs")

        if (resolution_time is not None and resolution_time > 48):
            anomalies.append({"ticket_id": row["ticket_id"],
                "reason": "Long Resolution Time"})

        if (row["priority"] == "Critical" and row["status"] != "Resolved"):

            anomalies.append({"ticket_id": row["ticket_id"],
                "reason": "Critical Unresolved Ticket"})

        if row["status"] != "Resolved":

            age_hours = (datetime.now() - row["created_at"]).total_seconds() / 3600

            if (row["priority"] in ["High", "Critical"]
                and age_hours > 24):

                anomalies.append({"ticket_id": row["ticket_id"],
                    "reason": "High Priority Ticket Older Than 24 Hours"})

    return anomalies