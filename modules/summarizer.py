import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv() # add you own credential to the env file

bedrock = boto3.client("bedrock-runtime", region_name="us-west-2")

def summarize_posts(posts):
    summaries = []

    for post in posts:
        if not post.strip():
            summaries.append("[Skipped: empty post]")
            continue

        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [
                {
                    "role": "user",
                    "content": f"Summarize the following Reddit post in 2 sentences:\n\n{post}"
                }
            ],
            "max_tokens": 300,
            "temperature": 0.5,
            "top_p": 1.0
        }

        try:
            response = bedrock.invoke_model(
                modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                contentType="application/json",
                accept="application/json",
                body=json.dumps(body)
            )

            result = json.loads(response["body"].read().decode("utf-8"))
            summaries.append(result["content"][0]["text"])
        except Exception as e:
            summaries.append(f"[ERROR] Claude failed: {e}")

    return summaries
