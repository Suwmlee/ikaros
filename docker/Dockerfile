FROM python:3.9-slim
LABEL git="https://github.com/Suwmlee/ikaros"

ENV S6_KEEP_ENV 1
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV TZ=Asia/Shanghai

EXPOSE 12346

RUN apt-get update \
    && apt-get install -y wget ca-certificates procps xz-utils

# set version for s6 overlay
ARG S6_OVERLAY_VERSION="3.1.2.1"
ARG S6_OVERLAY_ARCH="x86_64"

# add s6 overlay
RUN wget https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz -P /tmp \
    && tar -C / -xvf /tmp/s6-overlay-noarch.tar.xz
RUN wget https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-${S6_OVERLAY_ARCH}.tar.xz -P /tmp \
    && tar -C / -xvf /tmp/s6-overlay-${S6_OVERLAY_ARCH}.tar.xz

# add s6 optional symlinks
RUN wget  https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-symlinks-noarch.tar.xz -P /tmp \
    && tar -C / -xvf /tmp/s6-overlay-symlinks-noarch.tar.xz
RUN wget  https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-symlinks-arch.tar.xz -P /tmp \
    && tar -C / -xvf /tmp/s6-overlay-symlinks-arch.tar.xz


WORKDIR /ikaros
COPY . .

RUN wget -O - https://github.com/Suwmlee/ikaros-web/archive/release.tar.gz | tar xvz \
    && mv ./ikaros-web-release/index.html /ikaros/web/templates/ \ 
    && mv ./ikaros-web-release/* /ikaros/web/static/
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone

RUN pip install --no-cache-dir -r requirements.txt

# clean
RUN apt-get clean autoclean -y \
    && apt-get purge -y wget \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

RUN echo "**** create abc user and make our folders ****" && \
    groupmod -g 1000 users && \
    useradd -u 911 -U -d /config -s /bin/false abc && \
    usermod -G users abc && \
    mkdir /config

VOLUME /media
VOLUME /ikaros/database

#Copy s6-overlay 3.x services
#Uses a system-d like definition that can't be use in 2.x
COPY ./docker/s6/s6-rc.d/ /etc/s6-overlay/s6-rc.d/
#Copy setup script as-is since no changes are needed between 2.x and 3.x
COPY ./docker/s6/cont-init.d/01-ikaros-setup /etc/s6-overlay/s6-rc.d/init/
#COPY /tools/build/docker/s6/fix-attrs.d/ /etc/fix-attrs.d/

# COPY docker/entrypoint.sh /ikaros/entrypoint.sh
# RUN chmod +x /ikaros/entrypoint.sh
# CMD [ "/ikaros/entrypoint.sh" ]
ENTRYPOINT ["/init"]
