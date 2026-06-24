from fastapi import APIRouter, Request
from app.db.supabase import supabase

router = APIRouter()

@router.post("/callbacks/stk-result")
async def  stk_callback(request: Request):
    payload = await request.json()
    callback = payload["Body"]["stkCallback"]

    checkout_request_id = callback["CheckoutRequestID"]
    result_code = callback["ResultCode"]
    result_desc = callback["ResultDesc"]

    pending = (
        supabase.table("transactions")
        .select("id, merchant_id, status")
        .eq("checkout_request_id", checkout_request_id)
        .execute()
    )

    if not pending.data:
        supabase.table("daraja_logs").insert({
            "merchant_id": None,
            "direction": "callback_unmatched",
            "payload": payload,
        }).execute()
        return {"ResultCode": 0, "ResultDesc": "Accepted"}
    
    transaction = pending.data[0]
    merchant_id = transaction["merchant_id"]

    supabase.table("daraja_logs").insert({
        "merchant_id": merchant_id,
        "direction": "callback",
        "payload": payload,
    }).execute()

    if transaction["status"] == "paid":
        return {"ResultCode": 0, "ResultDesc": "Already processed"}
    
    if result_code != 0:
        supabase.table("transactions").update({
            "status": "failed",
            "failure_reason": result_desc,
        }).eq("checkout_request_id", checkout_request_id).execute()
        return {"ResultCode": 0, "ResultDesc": "Accepted"}
    
    items = callback["CallbackMetadata"]["Item"]
    metadata = {item["Name"]:item.get("Value") for item in items}

    supabase.table("transactions").update({
        "status": "paid",
        "mpesa_receipt": metadata.get("MpesaReceiptNumber"),
        "amount": metadata.get("Amount"),
    }).eq("checkout_request_id", checkout_request_id).execute()

    return {"ResultCode": 0, "ResultDesc": "Accepted"}
    

    
    
    