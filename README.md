```
telegram_bot/
│
├── bot.py                # 主程序入口
├── handlers.py           # 消息处理器
├── database.py           # 数据库相关操作
├── api_client.py         # Deepseek API 客户端
├── utils.py              # 工具函数（如日志、表名处理等）
├── config.py             # 配置文件（如环境变量加载）
└── models.py             # 数据模型（可选）

初始化

克隆代码库
git clone https://github.com/breaddog100/telegram_bot.git

更新系统
sudo apt update && sudo apt upgrade -y
sudo apt install build-essential

安装python3.10
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-dev -y
sudo apt install python-is-python3
python --version

安装SQLite3
sudo apt install sqlite3 -y

克隆代码
git clone https://github.com/breaddog100/telegram_bot.git
cd telegram_bot

创建虚拟环境：
python3.10 -m venv venv
source venv/bin/activate

安装Python依赖
pip install -r requirements.txt
cut -d= -f1 requirements.txt | xargs -n1 pip install --upgrade
pip freeze > requirements.txt
pip list

配置.env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
ARK_API_KEY=your_ark_api_key
...

启动bot
python bot.py

查询数据库
sqlite3 chat_history.db
查看表结构
.tables

```