FROM python:3.10-alpine

WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY . /code/

# expose port 8000 (add -p8000:8000 to "docker run" command to carry through to host
EXPOSE 8000

# run as non-root
RUN addgroup -g 1000 api && adduser -D -H -G api -u 1000 api
USER api

# start API server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
