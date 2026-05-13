FROM python:3.13-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc libc-dev && \
    rm -rf /var/lin/apt/lists/*

WORKDIR app/

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir uwsgi

RUN apt-get purge --auto-remove gcc libc-dev

COPY . .

EXPOSE 8000 2525

ENV IP=0.0.0.0
ENV PORT=8000
ENV PROCESSES=2
ENV THREADS=2

CMD ["uwsgi", "--ini", "uwsgi.ini"]
