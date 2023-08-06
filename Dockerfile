# syntax=docker/dockerfile:1
FROM python:3.10


WORKDIR /app
COPY . .

RUN pip install pip -U -i https://mirrors.cloud.tencent.com/pypi/simple

RUN pip install -r requirements.txt  -i https://mirrors.cloud.tencent.com/pypi/simple
# RUN playwright install --with-deps chromium

# RUN pip install pdm -i https://mirrors.cloud.tencent.com/pypi/simple
# Run pdm config --global pypi.url https://mirrors.cloud.tencent.com/pypi/simple
# RUN pip install -U nb-cli nonebot2[fastapi,httpx,aiohttp,websockets] -i https://mirrors.cloud.tencent.com/pypi/simple
# Run pdm add nonebot2[fastapi,httpx,aiohttp,websockets] -v
# RUN pdm install
# RUN pdm update 


# 设置环境变量（如果需要）
ENV HOST=0.0.0.0

# 暴露容器的端口号（如果需要）
EXPOSE 8080

# 定义容器启动时要执行的命令
CMD ["nb","run"]