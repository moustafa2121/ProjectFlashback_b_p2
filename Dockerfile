FROM python:3.12-alpine
ENV PYTHONUNBUFFERED=1
ENV OPENAI_API_KEY="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"
WORKDIR /django2
COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
COPY . .