def get_open_tickets(df):
    return len(df[df["status"] == "Open"])


def get_critical_unresolved(df):
    return len(
        df[
            (df["priority"] == "Critical")
            & (df["status"] != "Resolved")
        ]
    )


def get_average_rating(df):
    return round(df["customer_rating"].mean(), 2)


def get_top_agent(df):
    resolved_tickets = df[df["status"] == "Resolved"]

    if resolved_tickets.empty:
        return "No Data"

    agent_stats = (
        resolved_tickets
        .groupby("agent_id")
        .size()
        .sort_values(ascending=False)
    )

    return agent_stats.index[0]


def execute_dynamic_query(parsed_query, df):

    operation = parsed_query.get("operation")
    filters = parsed_query.get("filters", {})
    conditions = parsed_query.get("conditions", {})

    filtered_df = df.copy()

    # Apply filters
    for column, value in filters.items():
        if column in filtered_df.columns:
            filtered_df = filtered_df[filtered_df[column] == value]

    # Apply conditions
    for column, rule in conditions.items():
        if column not in filtered_df.columns:
            continue
        if "gt" in rule:
            filtered_df = filtered_df[filtered_df[column] > rule["gt"]]
        if "lt" in rule:
            filtered_df = filtered_df[filtered_df[column] < rule["lt"]]

    # Count
    if operation == "count":
        return {"count": len(filtered_df)}

    # Average (generic — works for any column + any filter)
    elif operation == "average":
        column = parsed_query.get("column")  # consistent key name
        if not column or column not in filtered_df.columns:
            return {"message": "Invalid or missing column for average"}
        return {"average": round(filtered_df[column].mean(), 2)}

    # List records
    elif operation == "list":
        return filtered_df.head(20).to_dict(orient="records")

    # Top Agent
    elif operation == "top_agent":
        agent_stats = (
            filtered_df
            .groupby("agent_id")
            .size()
            .sort_values(ascending=False)
        )
        if agent_stats.empty:
            return {"message": "No matching records"}
        return {
            "top_agent": agent_stats.index[0],
            "ticket_count": int(agent_stats.iloc[0])
        }

    # Lowest Rated Agent
    elif operation == "lowest_rated_agent":
        ratings = (
            filtered_df
            .dropna(subset=["customer_rating"])
            .groupby("agent_id")["customer_rating"]
            .mean()
            .sort_values()
        )
        if ratings.empty:
            return {"message": "No ratings available"}
        return {
            "agent_id": ratings.index[0],
            "average_rating": round(float(ratings.iloc[0]), 2)
        }

    # Anomaly Check — delegates to detect_anomalies for consistency
    elif operation == "anomaly_check":
        from app.anomaly_detector import detect_anomalies
        anomalies = detect_anomalies(filtered_df)
        return {
            "anomaly_count": len(anomalies),
            "tickets": anomalies[:10]
        }

    # Max
    elif operation == "max":
        column = parsed_query.get("column")
        if not column or column not in filtered_df.columns:
            return {"message": "Invalid or missing column for max"}
        return {"max": float(filtered_df[column].max())}

    # Min
    elif operation == "min":
        column = parsed_query.get("column")
        if not column or column not in filtered_df.columns:
            return {"message": "Invalid or missing column for min"}
        return {"min": float(filtered_df[column].min())}

    return {"message": "Unsupported operation"}