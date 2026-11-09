from datetime import date
from typing import Annotated

import uvicorn
from fastapi import FastAPI, HTTPException, Path, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


# Define a Response Model for automatic schema generation
class WarrantyResponse(BaseModel):
    device_id: str = Field(..., example="PRINTER-1001", description="The normalized unique ID of the device")
    expires: date = Field(..., example="2028-12-31", description="The date the warranty expires")
    covered: bool = Field(..., example=True, description="Whether the device is currently under warranty")
    checked_on: date = Field(..., description="The date the check was performed")

app = FastAPI(
    title="Printer Warranty Provider API",
    description="This API allows users to verify the warranty status of printers and scanners based on their Device ID.",
    version="1.0.0",
    contact={
        "name": "Warranty Support Team",
        "email": "support@printerapi.com",
    }
)


# Define a clean Error Model for Swagger documentation
class ErrorDetail(BaseModel):
    message: str = Field(..., example="The device_id provided is invalid")
    field: str = Field(..., example="device_id")


# Custom Exception Handler to override the default Pydantic error
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Transforms the complex Pydantic error into a simple, flat list of errors.
    """
    errors = []
    for error in exc.errors():
        # Extract the field name (the last element in the 'loc' tuple)
        field_name = str(error.get("loc")[-1]) if error.get("loc") else "unknown"
        # Get the human-readable message
        message = error.get("msg")

        errors.append({
            "field": field_name,
            "message": message
        })

    return JSONResponse(
        status_code=422,
        content={"detail": errors},
    )

# Mock database
WARRANTIES = {
    "PRINTER-1001": "2028-12-31",
    "PRINTER-2001": "2024-06-15",
    "SCANNER-3001": "2027-09-30",
    "LAP-123": "2027-10-20",
}

@app.get(
    "/warranty/{device_id}",
    response_model=WarrantyResponse,               # Tells Swagger exactly what the output looks like
    summary="Check device warranty by device ID",  # Short summary in the UI
    description="Retrieve warranty expiration and coverage status for a specific device ID.", # Detailed description
    responses={
        404: {"description": "Device ID not found in the records"},
        422: {"model": list[ErrorDetail], "description": "Validation Error"},
        200: {"description": "Warranty details retrieved successfully"}
    },
    tags=["Warranty Management"]       # Groups endpoints in the UI
)
def get_warranty(
    device_id: Annotated[str, Path(
        description="The unique identifier of the printer or scanner",
        example="PRINTER-1001"
    )]
)->WarrantyResponse:
    """
    Retrieve warranty expiration and coverage status for a specific device ID.

    **Process:**
        1. Normalize the device ID to uppercase.
        2. Check if the ID exists in the database.
        3. Compare the expiry date against today's date.

    :param device_id: The unique identifier of the printer or scanner
    :return: Warranty details retrieved successfully
    :raises HTTPException(Not Found): If the warranty record is not found in the database
    """
    normalized_id = device_id.upper()
    expiry = WARRANTIES.get(normalized_id)

    if expiry is None:
        raise HTTPException(
            status_code=404,
            detail=f"No warranty record found for {normalized_id}"
        )

    today = date.today()
    expiration_date = date.fromisoformat(expiry)

    return WarrantyResponse(
        device_id=normalized_id,
        expires=expiration_date,
        covered=expiration_date >= today,
        checked_on=today,
    )



if __name__ == "__main__":
    """
    Check it and see it works on its swagger docs: http://127.0.0.1:8000/docs
    """
    uvicorn.run(app, host="127.0.0.1", port=8000)
