
import json
import os
from datetime import datetime


LOG_FILE = "logs/chat_logs.json"


def save_chat_log(
    user_message: str,
    bot_response: str,
    intent: str,
    confidence: float
):

    # Create logs folder if it does not exist
    os.makedirs(
        os.path.dirname(LOG_FILE),
        exist_ok=True
    )


    # Read existing logs
    if os.path.exists(LOG_FILE):

        try:

            with open(
                LOG_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                logs = json.load(file)

        except (json.JSONDecodeError, OSError):

            logs = []

    else:

        logs = []


    # Create new log
    log = {

        "timestamp": datetime.now().isoformat(),

        "user_message": user_message,

        "intent": intent,

        "confidence": confidence,

        "bot_response": bot_response
    }


    # Add new log
    logs.append(log)


    # Save logs
    with open(
        LOG_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            logs,
            file,
            indent=4,
            ensure_ascii=False
        )
