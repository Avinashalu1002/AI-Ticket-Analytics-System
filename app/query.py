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

            filtered_df = filtered_df[
                filtered_df[column] == value
            ]

    # Apply conditions
    for column, rule in conditions.items():

        if column not in filtered_df.columns:
            continue

        if "gt" in rule:

            filtered_df = filtered_df[
                filtered_df[column] > rule["gt"]
            ]

        if "lt" in rule:

            filtered_df = filtered_df[
                filtered_df[column] < rule["lt"]
            ]

    # Count
    if operation == "count":

        return {
            "count": len(filtered_df)
        }

    # Average
    elif operation == "average":

        field = parsed_query.get("field")

        if field not in filtered_df.columns:

            return {
                "message": "Invalid field"
            }

        return {
            "average": round(
                filtered_df[field].mean(),
                2
            )
        }

    # List records
    elif operation == "list":

        return filtered_df.head(20).to_dict(
            orient="records"
        )

    # Top agent
    elif operation == "top_agent":

        agent_stats = (
            filtered_df
            .groupby("agent_id")
            .size()
            .sort_values(ascending=False)
        )

        if agent_stats.empty:

            return {
                "message": "No matching records"
            }

        return {
            "top_agent": agent_stats.index[0],
            "ticket_count": int(agent_stats.iloc[0])
        }

    # Anomaly check
    elif operation == "anomaly_check":

        anomalies = filtered_df[
            filtered_df["resolution_time_hrs"] > 48
        ]

        return {
            "anomaly_count": len(anomalies),
            "tickets": anomalies.head(10).to_dict(
                orient="records"
            )
        }

    return {
        "message": "Unsupported operation"
    }