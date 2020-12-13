FROM python:slim
LABEL git="https://github.com/Suwmlee/JAV-Scraper"

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
EXPOSE 12346

RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list \
    && sed -i 's/security.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pip -U \
    && pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt \
    && apt-get clean autoclean -y \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /media /jav-scraper/database \
    && chmod 777 /media /jav-scraper/database
RUN useradd -ms /bin/bash master
USER master
WORKDIR /jav-scraper
COPY . .
VOLUME /media
VOLUME /jav-scraper/database

CMD ["flask", "run", "--port=12346"]
