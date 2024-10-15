FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

WORKDIR /app

COPY . /app

RUN pip install poetry
RUN poetry install

EXPOSE 8000

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0"]
