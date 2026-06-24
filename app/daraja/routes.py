from fastapi import APIRouter
from pydantic import BaseModel
from app.daraja.stk_push import initiate_stk_push
from app.daraja.utils import normalise_phone

router = APIRouter()

class PayRequest(BaseModel):
    merchant_id: str
    phone: str
    amount:int
    account_reference: str
    description: str = "Payment"

@router.post("/pay")
def pay(request: PayRequest):
    phone = normalise_phone(request.phone)
    print("NORMALISED PHONE", phone)
    result = initiate_stk_push(
        merchant_id=request.merchant_id,
        phone=request.phone,
        amount=request.amount,
        account_reference=request.account_reference,
        description=request.description,
    )
    return result
