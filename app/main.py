from fastapi import FastAPI

from app.loader import load_data
from app.query import (get_open_tickets,get_critical_unresolved,get_average_rating,get_top_agent,execute_dynamic_query)
from app.anomaly_detector import detect_anomalies
from app.schemas import QueryRequest
from app.llm import parse_query

app = FastAPI(title="AI Ticket Analytics API")

# Load dataset once when application starts
df = load_data()

@app.get("/")
def root():
    return {"message": "AI Ticket Analytics API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/dashboard")
def dashboard():
    return {
        "total_tickets": len(df),
        "open_tickets": get_open_tickets(df),
        "critical_unresolved": get_critical_unresolved(df),
        "average_rating": get_average_rating(df),
        "top_agent": get_top_agent(df)
    }


@app.get("/anomalies")
def get_anomalies():

    anomalies = detect_anomalies(df)

    return {
        "message": f"Found {len(anomalies)} anomalies in the ticket dataset.",
        "total_anomalies": len(anomalies),
        "anomalies": anomalies[:20]
    }


@app.post("/query")
def process_query(request: QueryRequest):

    parsed_query = parse_query(request.query)

    result = execute_dynamic_query(
        parsed_query,
        df
    )

    # Count response
    if "count" in result:
        answer = f"There are {result['count']} matching records."

    # Average response
    elif "average" in result:
        answer = f"The average value is {result['average']}."

    # Top agent response
    elif "top_agent" in result:
        answer = (
            f"{result['top_agent']} resolved the most tickets "
            f"({result['ticket_count']} tickets)."
        )

    # List response
    elif isinstance(result, list):
        return {
            "answer": f"Found {len(result)} matching records.",
            "records": result
        }

    # Anomaly response
    elif "anomaly_count" in result:
        return {
            "answer": f"Found {result['anomaly_count']} anomalies.",
            "tickets": result["tickets"]
        }

    else:
        answer = result.get(
            "message",
            "No results found."
        )

    return {
        "answer": answer
    }