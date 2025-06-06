FROM python:3.12-alpine

ENV PORT 80
WORKDIR /app

RUN apk add --no-cache gcc musl-dev
RUN pip3 install pip --upgrade
RUN pip3 install jj==2.12.1
RUN pip3 install "jinja2>=3.0"
RUN apk del gcc musl-dev

EXPOSE 80

ENTRYPOINT ["python3", "-m", "jj"]

CMD []
