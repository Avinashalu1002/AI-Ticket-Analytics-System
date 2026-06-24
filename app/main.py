import logging
from fastapi import FastAPI, HTTPException

from app.loader import load_data
from app.query import (get_open_tickets, get_critical_unresolved, 
                       get_average_rating, get_top_agent, execute_dynamic_query)
from app.anomaly_detector import detect_anomalies
from app.schemas import QueryRequest
from app.llm import parse_query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Ticket Analytics API")

# Load dataset once when application starts
df = load_data()


@app.get("/")
def root():
    return {"message": "AI Ticket Analytics API is running"}


@app.get("/health")
def health():
    return {"status": "healthy", "total_tickets": len(df)}


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
def get_anomalies(limit: int = 20):
    anomalies = detect_anomalies(df)
    return {
        "message": f"Found {len(anomalies)} anomalies in the ticket dataset.",
        "total_anomalies": len(anomalies),
        "anomalies": anomalies[:limit]
    }


@app.post("/query")
def process_query(request: QueryRequest):

    try:
        parsed_query = parse_query(request.query)
        logger.info("Parsed Query: %s", parsed_query)
    except Exception as e:
        logger.error("LLM parsing failed: %s", e)
        raise HTTPException(status_code=503, detail="LLM service unavailable. Please try again.")

    try:
        result = execute_dynamic_query(parsed_query, df)
    except Exception as e:
        logger.error("Query execution failed: %s", e)
        raise HTTPException(status_code=500, detail="Failed to execute query against dataset.")

    # List result (from "list" operation)
    if isinstance(result, list):
        return {
            "answer": f"Found {len(result)} matching records.",
            "records": result
        }

    if "count" in result:
        answer = f"There are {result['count']} matching records."

    elif "average" in result:
        answer = f"The average value is {result['average']}."

    elif "top_agent" in result:
        answer = (
            f"{result['top_agent']} resolved the most tickets "
            f"({result['ticket_count']} tickets)."
        )

    elif "agent_id" in result:
        answer = (
            f"{result['agent_id']} has the lowest average "
            f"customer rating of {result['average_rating']}."
        )

    elif "average_rating" in result:
        answer = f"The average customer rating is {result['average_rating']}."

    elif "anomaly_count" in result:
        return {
            "answer": f"Found {result['anomaly_count']} anomalies.",
            "tickets": result["tickets"]
        }

    else:
        answer = result.get("message", "No results found.")

    return {"answer": answer}