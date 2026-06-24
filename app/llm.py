import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


def get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set in environment")
    return Groq(api_key=api_key)


def parse_query(user_query):

    prompt = f"""
You are a ticket analytics query parser.

Dataset columns:

ticket_id
created_at
category
priority
status
response_time_hrs
resolution_time_hrs
agent_id
customer_rating
issue_summary

Allowed operations:

count
list
average
top_agent
lowest_rated_agent
anomaly_check

Return ONLY valid JSON. No markdown, no explanation.

Examples:

Question:
How many tickets are currently open?

Output:
{{
    "operation":"count",
    "filters": {{
        "status":"Open"
    }}
}}

Question:
How many Billing tickets are resolved?

Output:
{{
    "operation":"count",
    "filters": {{
        "category":"Billing",
        "status":"Resolved"
    }}
}}

Question:
What is the average customer rating for Technical category tickets?

Output:
{{
    "operation":"average",
    "column":"customer_rating",
    "filters": {{
        "category":"Technical"
    }}
}}

Question:
Which agent resolved the most tickets?

Output:
{{
    "operation":"top_agent",
    "filters": {{
        "status":"Resolved"
    }}
}}

Question:
Which agent has the lowest average customer rating?

Output:
{{
    "operation":"lowest_rated_agent"
}}

Question:
Show me all Critical tickets not resolved within 12 hours.

Output:
{{
    "operation":"list",
    "filters": {{
        "priority":"Critical"
    }},
    "conditions": {{
        "resolution_time_hrs": {{
            "gt": 12
        }}
    }}
}}

Question:
Are there any anomalies in resolution times?

Output:
{{
    "operation":"anomaly_check"
}}

Question:
{user_query}
"""

    client = get_client()

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    llm_response = response.choices[0].message.content.strip()

    # Strip markdown code fences if present
    llm_response = re.sub(r"```(?:json)?", "", llm_response).strip().strip("`").strip()

    try:
        return json.loads(llm_response)

    except Exception:
        return {
            "operation": "unknown",
            "filters": {}
        }