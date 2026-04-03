from pydantic import BaseModel

class CheckoutRequest(BaseModel):
    product_name: str
    amount: int       
    currency: str = "eur"
    success_url: str  
    cancel_url: str

    class Config:
        from_attributes = True
