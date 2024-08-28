FROM alpine:3.6

RUN apk add --update \
    python \
    python-dev \
    py-pip \
    gcc \
    musl-dev \
    linux-headers \
    libffi-dev \
    openssl-dev

RUN pip install certifi==2017.7.27.1
RUN pip install python-openstackclient==3.12.0 python-cinderclient==3.2.0 python-heatclient==1.11.0

WORKDIR /src/

COPY /src/ /src/

ENTRYPOINT ["./importer.py"]
