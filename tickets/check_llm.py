import json
import os
from urllib.error import HTTPError
from urllib.request import Request, urlopen


api_key = os.environ["OPENAI_API_KEY"]

payload = {
    "model": "gpt-4.1-mini",
    "input": "Reply with one short sentence confirming you are ready.",
    "max_output_tokens": 50,
}

request = Request(
    "https://api.openai.com/v1/responses",
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    },
    method="POST",
)

try:
    with urlopen(request, timeout=20) as response:
        result = json.load(response)

    for item in result.get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                print(content["text"])
except HTTPError as error:
    details = json.loads(error.read().decode("utf-8"))
    print("HTTP status:", error.code)
    print("Error code:", details.get("error", {}).get("code"))