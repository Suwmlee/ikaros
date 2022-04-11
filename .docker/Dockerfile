FROM python:3.9-slim
LABEL git="https://github.com/Suwmlee/ikaros"

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
EXPOSE 12346
WORKDIR /ikaros
COPY . .

RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list \
    && sed -i 's/security.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list
RUN apt-get update \
    && apt-get install -y wget ca-certificates \
    && wget -O - https://github.com/Suwmlee/ikaros-web/archive/release.tar.gz | tar xvz \
    && mv ./ikaros-web-release/index.html /ikaros/web/templates/ \ 
    && mv ./ikaros-web-release/* /ikaros/web/static/

RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get clean autoclean -y \
    && apt-get purge -y wget \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

VOLUME /media
VOLUME /ikaros/database

RUN useradd -u 666 -U -d /ikaros -s /bin/bash abc \
    && usermod -G users abc
COPY .docker/entrypoint.sh /ikaros/entrypoint.sh
RUN chmod +x /ikaros/entrypoint.sh
CMD [ "/ikaros/entrypoint.sh" ]
