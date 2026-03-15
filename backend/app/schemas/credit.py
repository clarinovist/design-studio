from pydantic import BaseModel, ConfigDict, UUID4
from datetime import datetime
from typing import List


from pydantic import Field

class CreditTransactionResponse(BaseModel):
    """
    Schema representing a single credit transaction (addition or deduction).
    """
    id: UUID4 = Field(..., description="Unique transaction ID")
    user_id: UUID4 = Field(..., description="User ID associated with the transaction")
    amount: int = Field(..., description="Amount of credits added (positive) or deducted (negative)", example=-10)
    balance_after: int = Field(..., description="Credit balance after this transaction", example=490)
    description: str = Field(..., description="Description of the transaction", example="Generated design")
    created_at: datetime = Field(..., description="Timestamp of the transaction")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "987e6543-e21b-12d3-a456-426614174000",
                "amount": -10,
                "balance_after": 490,
                "description": "Generated design",
                "created_at": "2023-01-01T12:00:00Z"
            }
        }
    )


class CreditHistoryResponse(BaseModel):
    """
    Schema for paginated credit history response.
    """
    transactions: List[CreditTransactionResponse] = Field(..., description="List of credit transactions")
    total_count: int = Field(..., description="Total number of transactions available", example=100)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "transactions": [],
                "total_count": 100
            }
        }
    )
