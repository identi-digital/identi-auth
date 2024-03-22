FROM python:3.10.13-alpine

RUN apk add tzdata
ENV TZ="America/Lima"
WORKDIR /app
COPY . .

RUN pip install pip --upgrade

# Verify files
RUN ls -l


RUN pip install -r requirements.txt
EXPOSE 9000
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "9000", "authx:api"]
