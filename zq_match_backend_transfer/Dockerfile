# 第一阶段：安装依赖和构建应用  
FROM python:3.11-slim AS build
  
# 使用国内的镜像源  
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        vim \
        build-essential \
        default-libmysqlclient-dev \
        pkg-config \
        libpq-dev \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*  
  
WORKDIR /app  
  
# 复制应用代码  
COPY . /app/  
  
# 使用国内的 PyPI 镜像源安装 Poetry  
RUN pip install poetry -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com && \
    poetry config virtualenvs.create false && \
    poetry export --output requirements.txt --without-urls && \
    pip install --upgrade pip -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com && \
    pip install -r requirements.txt -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com  
  
# 第二阶段：创建最小化的运行环境  
FROM python:3.11-slim
  
# 从第一阶段复制所需的文件和库  
COPY --from=build /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/  
COPY --from=build /app /app  
  
WORKDIR /app  
  
# 暴露端口并设置默认命令  
EXPOSE 8000  
CMD ["python3", "./manage.py", "runserver", "0.0.0.0:8000"]