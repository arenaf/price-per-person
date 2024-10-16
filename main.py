from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


app = FastAPI()


class Price(BaseModel):
    price: float = Field(ge=0)
    people: int = Field(ge=1)
    tip: float = Field(ge=0)


@app.get("/")
def home():
    return JSONResponse(
        content=jsonable_encoder(
            {"message": "Calculate the total amount to be paid per person on the route: /price"}
        )
    )


# Error handler: incorrect data entered by the user
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):

    message = []

    for all_errors in exc.errors():
        type, loc = all_errors["type"], all_errors["loc"][1]
        if exc.errors()[0]["type"] == "json_invalid":
            msg = all_errors["ctx"]["error"]
        else:
            msg = all_errors["msg"]
        message.append({"type": type, "loc": loc, "msg": msg})

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            {
                "Error": "Incorrect data entry. All fields must be filled in and in numerical format.",
                "detail": message,
            }
        ),
    )


@app.post("/price")
def price_to_pay(price: Price):
    total_tip = (price.tip * price.price) / 100
    total_price = (total_tip + price.price) / price.people
    result = round(total_price, 2)
    return JSONResponse(
        content=jsonable_encoder(
            {"result": f"Total price per person: {result}"}
        )
    )
