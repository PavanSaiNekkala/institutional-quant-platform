import os
import requests

from dotenv import load_dotenv

# =========================================================
# LOAD ENV
# =========================================================

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv(

    "TELEGRAM_BOT_TOKEN"
)

TELEGRAM_CHAT_ID = os.getenv(

    "TELEGRAM_CHAT_ID"
)

# =========================================================
# TELEGRAM ALERT
# =========================================================

def send_telegram_alert(

    message
):

    try:

        url = (

            f"https://api.telegram.org/bot"

            f"{TELEGRAM_BOT_TOKEN}"

            f"/sendMessage"
        )

        payload = {

            "chat_id":
                TELEGRAM_CHAT_ID,

            "text":
                message
        }

        response = requests.post(

            url,

            data=payload
        )

        return response.status_code == 200

    except Exception as e:

        print("TELEGRAM ERROR:", e)

        return False