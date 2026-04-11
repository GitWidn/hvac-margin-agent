import anthropic
import pandas as pd

client = anthropic.Anthropic(api_key="YOUR_API_KEY")

df = pd.read_csv('project_summary.csv')
top_projects = df.nsmallest(10, 'actual_labor_cost').to_string()  # worst margin first

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1000,
    messages=[{
        "role": "user",
        "content": f"""You are an AI agent analyzing HVAC project margins for a CFO.
        
Here are the 10 most at-risk projects by labor cost:
{top_projects}

For each project:
1. State the severity (CRITICAL / WARNING / OK)
2. Explain the root cause of margin erosion
3. Give 2-3 specific dollar-quantified recovery actions

Be specific. No generic advice."""
    }]
)

print(response.content[0].text)
