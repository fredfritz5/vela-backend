import os
import base64
from datetime import datetime
import httpx
from dotenv import load_dotenv

from app.daraja.auth import get_access_token, BASE_URL
from app.db.supabase import supabase

load_dotenv()

SHORTCODE = os.getenv("DARAJA_SHORTCODE")
PASSKEY = os.getenv("DARAJA_PASSKEY")

def initiate_stk_push(merchant_id:str,phone: str, amount: int, account_reference: str, description: str = "Payment"):
    token = get_access_token()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    password_str = f"{SHORTCODE}{PASSKEY}{timestamp}"
    password = base64.b64encode(password_str.encode()).decode()

    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA":phone,
        "PartyB": SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": os.getenv("DARAJA_CALLBACK_URL"),
        "AccountReference": account_reference,
        "TransactionDesc": description,

    }

    supabase.table("daraja_logs").insert({
        "merchant_id": merchant_id,
        "direction": "request",
        "payload": payload,
    }).execute()


    response = httpx.post(
        f"{BASE_URL}/mpesa/stkpush/v1/processrequest",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        
    )

    response.raise_for_status()
    result = response.json()

    checkout_request_id = result.get("CheckoutRequestID")

    supabase.table("transactions").insert({
      "merchant_id": merchant_id,
      "checkout_request_id": checkout_request_id,
      "amount":amount,
      "phone": phone,
      "status": "pending",
    }).execute()

    return result


