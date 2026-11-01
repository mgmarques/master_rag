
from fastapi import FastAPI, HTTPException
from datetime import date
import uvicorn

app = FastAPI(title="Printer Warranty Provider API")

# Mock database
WARRANTIES = {
    "PRINTER-1001": "2028-12-31",
    "PRINTER-2001": "2024-06-15",
    "SCANNER-3001": "2027-09-30",
}

@app.get("/warranty/{device_id}")
def get_warranty(device_id: str):
    device_id = device_id.upper()

    expiry = WARRANTIES.get(device_id)

    if expiry is None:
        raise HTTPException(
            status_code=404,
            detail=f"No warranty record found for {device_id}"
        )

    today = date.today()
    expiration_date = date.fromisoformat(expiry)

    return {
        "device_id": device_id,
        "expires": expiry,
        "covered": expiration_date >= today,
        "checked_on": today.isoformat(),
    }


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
    )
