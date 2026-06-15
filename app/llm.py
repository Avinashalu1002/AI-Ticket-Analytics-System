import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY"))

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
anomaly_check

Return JSON only.

Examples:

Question:
How many tickets are currently open?

Output:
{{"operation":"count",
  "filters": {{
      "status":"Open"
  }}}}

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
What is the average customer rating for Technical tickets?

Output:
{{
  "operation":"average",
  "field":"customer_rating",
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

Return ONLY valid JSON.

Question:
{user_query}
"""

    response = client.chat.completions.create(model="llama-3.3-70b-versatile",messages=[{"role": "user",
                    "content": prompt}])

    llm_response = response.choices[0].message.content.strip()

    try:
        return json.loads(llm_response)

    except json.JSONDecodeError:
        return {
            "operation": "unknown",
            "filters": {}
        }