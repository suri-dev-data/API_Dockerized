FROM python:latest

WORKDIR /app

COPY requirements.txt ./

RUN pip install fastapi uvicorn motor pydantic

COPY . .

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]