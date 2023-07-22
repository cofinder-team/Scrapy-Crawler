# 베이스 이미지를 선택합니다.
FROM python:3.10

# 작업 디렉토리를 설정합니다.
WORKDIR /app

# Scrapyd를 설치합니다.
RUN pip install scrapyd

# Scrapyd의 설정 파일을 복사합니다.
COPY scrapyd.conf /etc/scrapyd/

# Scrapy의 설정 파일을 복사합니다.
COPY scrapy.cfg /app/

# Scrapyd의 프로젝트 디렉토리를 복사합니다.
COPY ./scrapy_crawler /app/scrapy_crawler
COPY ./requirements.txt /app/scrapy_crawler

# CloudWatch Agent 설정 파일을 복사합니다.
COPY ./amazon-cloudwatch-agent.json /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json

# 필요한 종속성을 설치합니다.
RUN pip install -r /app/scrapy_crawler/requirements.txt
RUN pip install scrapy

# Scrapyd 서버의 포트를 노출합니다.
EXPOSE 6800

# Scrapyd 서버를 실행합니다.
CMD ["scrapyd"]