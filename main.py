from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Kelly's USSD APP")


class USSDRequest(BaseModel):
    USERID: str = ""
    MSISDN: str = ""
    USERDATA: str = ""
    MSGTYPE: bool = True  # True = first dial, False = user replied
    NETWORK: str = ""
    SESSIONID: str = ""


# In-memory session store: SESSIONID -> {"step": ..., "feeling": ...}
# Use Redis or a database in production.
sessions: dict[str, dict] = {}

FEELING = {
    "1": "fine",
    "2": "sad",
    "3": "frisky",
}

WHY = {
    "1": "Relationship issues",
    "2": "Money problems",
    "3": "Family issues",
}

FIRST_PAGE = (
    "Good Day User, How are you feeling today?\n"
    "1. Feeling fine\n"
    "2. Feeling sad\n"
    "3. Feeling frisky"
)


def second_page(feeling: str) -> str:
    return (
        f"Why are you feeling {feeling}?\n"
        "1. Relationship issues\n"
        "2. Money problems\n"
        "3. Family issues"
    )


def reply(req: USSDRequest, msg: str, keep_open: bool) -> dict:
    # MSGTYPE in the response: True = keep the session open, False = end it
    return {
        "USERID": req.USERID,
        "MSISDN": req.MSISDN,
        "MSG": msg,
        "MSGTYPE": keep_open,
    }


@app.post("/ussd")
def handle_ussd(req: USSDRequest):
    # Page 1: user just dialled the code
    if req.MSGTYPE:
        sessions[req.SESSIONID] = {"step": 1}
        return reply(req, FIRST_PAGE, True)

    session = sessions.get(req.SESSIONID)
    if session is None:
        return reply(req, "Session expired. Please dial again.", False)

    choice = req.USERDATA.strip()

    # Page 2: user answered "how are you feeling?"
    if session["step"] == 1:
        if choice not in FEELING:
            sessions.pop(req.SESSIONID, None)
            return reply(req, "Invalid. Please dial again and select 1, 2 or 3.", False)
        session["feeling"] = FEELING[choice]
        session["step"] = 2
        return reply(req, second_page(session["feeling"]), True)

    # Page 3: user answered "why?"
    if session["step"] == 2:
        sessions.pop(req.SESSIONID, None)
        if choice not in WHY:
            return reply(req, "Invalid. Please dial again and select 1, 2 or 3.", False)
        return reply(
            req,
            f"Thanks. You are feeling {session['feeling']} because of: {WHY[choice]}.",
            False,
        )

    sessions.pop(req.SESSIONID, None)
    return reply(req, "Something went wrong. Please dial again.", False)