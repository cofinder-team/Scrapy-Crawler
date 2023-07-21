# Base image (Amazon Linux 2 with Python 3.8)
FROM amazonlinux:2



# Install Python and required packages

# Install dependencies, CloudWatch Agent, and configure
RUN yum update -y && \
    yum install -y amazon-cloudwatch-agent python3 python-pip postgresql-devel

COPY amazon-cloudwatch-agent.json /etc/cloudwatch/

# 작업 디렉토리를 설정합니다.
WORKDIR /app


# Scrapyd의 설정 파일을 복사합니다.
COPY scrapyd.conf /etc/scrapyd/

# Scrapy의 설정 파일을 복사합니다.
COPY scrapy.cfg /app/

# Scrapyd의 프로젝트 디렉토리를 복사합니다.
COPY ./scrapy_crawler /app/scrapy_crawler
COPY ./requirements.txt /app/scrapy_crawler

# 필요한 종속성을 설치합니다.
RUN python3 -m pip install -r /app/scrapy_crawler/requirements.txt

# Scrapyd 서버의 포트를 노출합니다.
EXPOSE 6800

# Scrapyd 서버를 실행합니다.
CMD ["scrapyd"]
