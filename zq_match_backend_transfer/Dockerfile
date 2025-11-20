# ==========================================
# 第一阶段：构建与依赖安装
# ==========================================
# 使用 DaoCloud 镜像加速下载官方 Python 镜像
FROM docker.m.daocloud.io/library/python:3.11-slim AS build

# 1. 替换 Debian 12 (Bookworm) 的系统源为 USTC 镜像
# 2. 安装编译必须的系统依赖 (增加 libssl-dev libffi-dev 以防 poetry 安装失败)
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        default-libmysqlclient-dev \
        pkg-config \
        libpq-dev \
        libssl-dev \
        libffi-dev \
        && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 3. 复制项目文件
COPY . /app/

# 4. 先升级 pip (防止 pip 版本过低导致安装问题)
RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

# 5. 分步安装依赖，方便排查错误
# 安装 Poetry (增加超时设置)
RUN pip install poetry -i https://pypi.tuna.tsinghua.edu.cn/simple --default-timeout=100

# 导出 requirements.txt (如果这里报错，请检查本地是否有 pyproject.toml 和 poetry.lock)
# 注意：这里加了 || true，如果导出失败（比如lock文件问题），尝试直接使用项目中已有的 requirements.txt
RUN poetry config virtualenvs.create false && \
    poetry export --output requirements.txt --without-urls || echo "Poetry export failed, using existing requirements.txt"

# 安装项目依赖
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --default-timeout=100

# ==========================================
# 第二阶段：最小化运行环境
# ==========================================
FROM docker.m.daocloud.io/library/python:3.11-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 1. 安装运行时必须的系统库
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        default-libmysqlclient-dev \
        libpq-dev \
        busybox \
        && apt-get clean && rm -rf /var/lib/apt/lists/*

# 2. 从构建阶段复制 Python 依赖包
COPY --from=build /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=build /usr/local/bin/ /usr/local/bin/

# 3. 复制应用代码
COPY --from=build /app /app

EXPOSE 8000

# 启动命令
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]

