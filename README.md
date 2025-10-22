# HDDel

回单线的筛除算法，fastapi做后端，n8n作编排可视化。

## 环境准备：

### n8n Docker Windows本地部署，参考n8n官方项目（https://github.com/n8n-io/n8n）

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
cd ..
python -m HDDel.main
```

### 使用n8n工作流

**localhost:5678** 打开网页进入n8n，将文件“算法筛除多余线.json”拖入workflow工作面板，点击“Execute workflow”按钮即可开始
![n8n工作流界面](https://github.com/jackhe183/HDDel/blob/main/assets/Snipaste_2025-10-22_09-37-56.png?raw=true)

### 以下是工作流调用算法测试的结果，我为了方便直接在调用算法main.py修改使用的算法py脚本了<br>
<textArea>
# from 最大裂谷算法 import find_slip_starts<br>
# from 簇过滤算法 import find_slip_starts<br>
# from .均衡分割算法 import find_slip_starts   # 新建文件夹 全对了  # 新建文件夹2的联数强制为2全部正确，设置联数=0全错<br>
# from .自适应分割算法 import find_slip_starts  # 新建文件夹 全对了  # 新建文件夹2的联数强制为2全部正确，设置联数=0全错<br>
# from .聚类拟合算法 import find_slip_starts  # 新建文件夹 全对了  # 新建文件夹2的联数强制为2全部正确，设置联数=0全错<br>
# from 高级分割算法 import find_slip_starts # 新建文件夹 全错了<br>
# from 智能决策算法 import find_slip_starts # 新建文件夹 自动大部分错，强制联数=2全部正确<br>
# from 稳健间距算法 import find_slip_starts # 新建文件夹 自动大部分错，强制联数=2全部正确<br>
# from 奥卡姆剃刀算法 import find_slip_starts # 新建文件夹 自动大部分错，强制联数=2全部正确<br>
from .结构匹配算法 import find_slip_starts  # 新建文件夹 全对了  # 新建文件夹2的联数强制为2全部正确，设置联数=0全错<br>
</textArea>
