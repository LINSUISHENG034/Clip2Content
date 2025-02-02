FROM nvidia/cuda:11.7.1-base

RUN apt-get update && apt-get install -y ffmpeg python3.9

COPY requirements.txt .

RUN pip install -r requirements.txt

ENTRYPOINT ["celery", "-A", "main", "worker", "--loglevel=info"]