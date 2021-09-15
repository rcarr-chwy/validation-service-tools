FROM python:3.8.5-slim-buster

# Set the timezone.
ENV TZ=America/New_York
RUN echo "America/New_York" > /etc/timezone

# Set environment variables
# PYTHONDONTWRITEBYTECODE - Prevents Python from writing pyc files to disc (equivalent to python -B option)
# PYTHONUNBUFFERED - Prevents Python from buffering stdout and stderr (equivalent to python -u option)
#
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /requirements.txt

RUN pip install --upgrade pip \
&& pip install -r /requirements.txt \
&& rm -rf /requirements.txt

WORKDIR /app
