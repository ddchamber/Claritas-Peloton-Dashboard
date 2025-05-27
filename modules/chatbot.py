import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv() # add you own credential to the env file

bedrock = boto3.client("bedrock-runtime", region_name="us-west-2")

def chat_with_claude(prompt, context=""):
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion:\n{prompt}"
            }
        ],
        "max_tokens": 400,
        "temperature": 0.7,
        "top_p": 1.0
    }

    try:
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body)
        )

        result = json.loads(response["body"].read().decode("utf-8"))
        return result["content"][0]["text"]
    except Exception as e:
        return f"[ERROR] Claude failed: {e}"


