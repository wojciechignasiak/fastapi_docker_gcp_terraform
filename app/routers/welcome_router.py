#3rd party libraries
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

#1st party libraries
import logging


logger: logging.Logger = logging.getLogger(__name__)
router: APIRouter = APIRouter()

@router.get("/welcome", status_code=status.HTTP_200_OK)
async def welcome():
    try:
        return JSONResponse(status_code=200, content={"message": "PoC for Finitec Sp. z o.o. Company! :)"})
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")