"""Tiny terminal USSD simulator, so you can test without a real shortcode.

Run the server first:   uvicorn main:app --reload
Then in another shell:  python simulator.py
"""

import urllib.parse
import urllib.request
import uuid

URL = "http://127.0.0.1:8000/ussd"
PHONE = "+233200000000"
SERVICE_CODE = "*123#"


def send(session_id: str, text: str) -> str:
    data = urllib.parse.urlencode(
        {
            "sessionId": session_id,
            "serviceCode": SERVICE_CODE,
            "phoneNumber": PHONE,
            "text": text,
        }
    ).encode()
    with urllib.request.urlopen(urllib.request.Request(URL, data=data)) as resp:
        return resp.read().decode()


def main():
    session_id = str(uuid.uuid4())
    text = ""
    print(f"Dialling {SERVICE_CODE} ...\n")
    while True:
        reply = send(session_id, text)
        prefix, _, body = reply.partition(" ")
        print(f"--- USSD ---\n{body}\n------------")
        if prefix == "END":
            print("Session ended.")
            break
        answer = input("> ").strip()
        text = f"{text}*{answer}" if text else answer


if __name__ == "__main__":
    main()
