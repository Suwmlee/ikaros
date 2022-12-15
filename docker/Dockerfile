FROM python:3.9-slim
LABEL git="https://github.com/Suwmlee/ikaros"

ENV S6_KEEP_ENV 1
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV TZ=Asia/Shanghai
ENV PUID=0
ENV PGID=0

EXPOSE 12346

RUN apt-get update && \
    apt-get install -y wget ca-certificates procps xz-utils

# update TZ
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone

# set version for s6 overlay
ARG S6_OVERLAY_VERSION="3.1.2.1"
ARG S6_OVERLAY_ARCH="x86_64"

# add s6 overlay
RUN wget https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz -P /tmp && \
    tar -C / -Jxpf /tmp/s6-overlay-noarch.tar.xz
RUN wget https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-${S6_OVERLAY_ARCH}.tar.xz -P /tmp && \
    tar -C / -Jxpf /tmp/s6-overlay-${S6_OVERLAY_ARCH}.tar.xz

# add s6 optional symlinks
RUN wget https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-symlinks-noarch.tar.xz -P /tmp && \
    tar -C / -Jxpf /tmp/s6-overlay-symlinks-noarch.tar.xz
RUN wget https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-symlinks-arch.tar.xz -P /tmp && \
    tar -C / -Jxpf /tmp/s6-overlay-symlinks-arch.tar.xz

# fetch ikaros web
RUN wget https://github.com/Suwmlee/ikaros-web/archive/release.tar.gz -P /tmp && \
    tar -C /tmp -xzf /tmp/release.tar.gz

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /app
COPY . .

# setup ikaros web
RUN mv /tmp/ikaros-web-release/index.html /app/web/templates/ && \ 
    mv /tmp/ikaros-web-release/* /app/web/static/

# clean
RUN rm -rf /tmp/*

RUN echo "**** create tomoki user and make folders ****" && \
    groupmod -g 1000 users && \
    useradd -u 911 -U -d /config -s /bin/false tomoki && \
    usermod -G users tomoki && \
    mkdir /config

VOLUME /media
VOLUME /app/data

#Copy s6-overlay 3.x services
#Uses a system-d like definition that can't be use in 2.x
COPY docker/s6/s6-rc.d/ /etc/s6-overlay/s6-rc.d/

ENTRYPOINT ["/init"]
