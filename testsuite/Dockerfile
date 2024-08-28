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
RUN pip install pylint==1.7.4 pycodestyle==2.3.1 pep257==0.7.0

WORKDIR /src/
COPY /src/ /src/
COPY testsuite/code_style_checks.sh code_style_checks.sh
