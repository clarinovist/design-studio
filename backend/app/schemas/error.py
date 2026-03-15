from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Any


class ErrorDetail(BaseModel):
    loc: List[str] = Field(description="Location of the error", example=["body", "name"])
    msg: str = Field(description="Error message", example="field required")
    type: str = Field(description="Error type", example="value_error.missing")


class ErrorResponse(BaseModel):
    """
    Standardized error response schema.
    """
    detail: str = Field(
        ...,
        description="A detailed error message intended for the developer/user.",
        example="The requested resource was not found."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "The requested resource was not found."
            }
        }
    )


class ValidationErrorResponse(BaseModel):
    """
    Validation error response schema, typically matching FastAPI's 422 Unprocessable Entity.
    """
    detail: List[ErrorDetail] = Field(
        ...,
        description="A list of validation errors."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": [
                    {
                        "loc": ["body", "email"],
                        "msg": "value is not a valid email address",
                        "type": "value_error.email"
                    }
                ]
            }
        }
    )


# Common error response dictionaries to be used in router `responses` parameter
ERROR_RESPONSES = {
    400: {"model": ErrorResponse, "description": "Bad Request"},
    401: {"model": ErrorResponse, "description": "Unauthorized - Authentication required"},
    403: {"model": ErrorResponse, "description": "Forbidden - Insufficient permissions"},
    404: {"model": ErrorResponse, "description": "Not Found - Resource does not exist"},
    409: {"model": ErrorResponse, "description": "Conflict - Resource already exists or conflict in state"},
    422: {"model": ValidationErrorResponse, "description": "Validation Error - Invalid input data"},
    500: {"model": ErrorResponse, "description": "Internal Server Error"},
}
