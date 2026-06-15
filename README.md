# AI Ticket Analytics System

## Overview

AI-powered support ticket analytics system built using FastAPI, Pandas, and Groq LLM.

The system ingests support ticket data from a CSV file, supports natural language querying, detects anomalies, and exposes functionality through REST APIs.

---

## Features

- CSV Data Ingestion
- Natural Language Querying using Groq LLM
- Dynamic Query Parsing
- Ticket Analytics Dashboard
- Anomaly Detection
- FastAPI REST APIs
- Swagger Documentation

---

## Tech Stack

- Python
- FastAPI
- Pandas
- Groq (Llama 3.3 70B)
- Uvicorn

---

## Project Structure

AI_Ticket_System/
├── app/
├── data/
├── requirements.txt
├── README.md
└── .env

---

## Setup

Install dependencies:

pip install -r requirements.txt

Run the application:

uvicorn app.main:app --reload

---

## API Endpoints

### Health Check

GET /health

### Dashboard

GET /dashboard

### Anomalies

GET /anomalies

### Query

POST /query

Example:

{
  "query": "How many tickets are currently open?"
}

---

## Example Queries

- How many tickets are currently open?
- How many Billing tickets are resolved?
- What is the average customer rating for Technical tickets?
- Which agent resolved the most tickets?
- Show me all Critical tickets not resolved within 12 hours.
- Are there any anomalies in resolution times?
