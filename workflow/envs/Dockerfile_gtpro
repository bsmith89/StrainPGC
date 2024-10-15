FROM --platform=linux/amd64 ubuntu:18.04
RUN \
    apt-get update \
    && apt-get install -y \
        git \
        make \
        g++ \
        libz-dev \
        libtbb2 \
        pigz \
    && rm -rf /var/lib/apt/lists/*
RUN \
    mkdir -p src && cd src \
    && git clone https://github.com/zjshi/gt-pro gt-pro && cd gt-pro \
    && make && ln -s $PWD/GT_Pro /usr/bin/ && ln -s $PWD/scripts/gtp_parse.py /usr/bin/
