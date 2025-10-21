# HDDel

回单线的筛除算法，fastapi做后端，n8n作编排可视化。

## 环境准备：

### Docker Windows本地部署n8n，参考n8n官方项目（https://github.com/n8n-io/n8n）

第一次安装桌面版docker，如果要提示安装WSL，powershell管理员运行以下代码。
```bash
wsl --update --web-download
```

设置Docker源，加速资源下载速度。鉴于很多公开docker镜像源已经失效，所以我为了省事，就花钱用了轩辕镜像，参考轩辕镜像（https://docker.xuanyuan.me/）
这是公开免费的，但是有限定额度。在Docker Engine里复制粘贴设置，不懂也可以去搜教程。
```bash
{
    "registry-mirrors": [
        "https://docker.xuanyuan.me"
    ]
}
```

docker desktop的右下角，打开终端，命令一键部署n8n项目。
```bash
docker volume create n8n_data
docker run -it --rm --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n n8nio/n8n
```

### 运行fastapi服务

git下载本项目源码，也可以直接网页端点击download zip下载。
```bash

```

本项目使用python解释器版本：3.13.7，使用uv安装依赖。
```bash
cd HDDel
uv pip install -r requirements.txt
```

启动FastAPI项目。如果端口被占用了，可以在main.py里面将8005改为其它的端口。
```bash
python main.py
```

### 使用n8n工作流








