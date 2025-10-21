#3rd party libraries
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

#1st party libraries
import logging


logger: logging.Logger = logging.getLogger(__name__)
router: APIRouter = APIRouter()

@router.get("/welcome", status_code=status.HTTP_200_OK)
async def welcome():
    return JSONResponse(status_code=200, content={"message": "FastAPI PoC! :)"})
