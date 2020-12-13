FROM python:slim
LABEL git="https://github.com/Suwmlee/JAV-Scraper"

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
EXPOSE 12346
ENV PUID=911 PGID=100

RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list \
    && sed -i 's/security.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pip -U \
    && pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN \
    if [ $(getent group ${PGID}) ]; then \
        adduser -D -u ${PUID} master; \
    else \
        addgroup -g ${PGID} master && \
        adduser -D -u ${PUID} -G master master; \
    fi
    
WORKDIR /jav-scraper
COPY . .
VOLUME /media
VOLUME /jav-scraper/database

CMD ["flask", "run", "--port=12346"]
