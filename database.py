import sqlite3
def get_group_table_name(chat_id):
    """将群组 ID 转换为合法的表名"""
    return f"group_messages_{abs(chat_id)}"
def create_group_table_if_not_exists(chat_id):
    """动态创建群组聊天记录表"""
    conn = sqlite3.connect('chat_history.db')
    cursor = conn.cursor()
    table_name = get_group_table_name(chat_id)
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
def save_group_message(chat_id, user_id, username, role, content):
    """保存群组消息到数据库"""
    create_group_table_if_not_exists(chat_id)
    conn = sqlite3.connect('chat_history.db')
    cursor = conn.cursor()
    table_name = get_group_table_name(chat_id)
    cursor.execute(f'''
        INSERT INTO {table_name} (user_id, username, role, content)
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, role, content))
    conn.commit()
    conn.close()
def save_private_message(user_id, username, role, content):
    """保存个人消息到数据库"""
    conn = sqlite3.connect('chat_history.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO private_messages (user_id, username, role, content)
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, role, content))
    conn.commit()
    conn.close()
def load_private_messages(user_id, max_rounds):
    """从数据库加载个人对话历史"""
    conn = sqlite3.connect('chat_history.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT role, content FROM private_messages
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (user_id, max_rounds * 2))
    messages = cursor.fetchall()
    conn.close()
    return [{"role": role, "content": content} for role, content in messages]
def init_db():
    """初始化数据库，仅在表不存在时创建表"""
    conn = sqlite3.connect('chat_history.db')
    cursor = conn.cursor()
    # 检查 private_messages 表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='private_messages'")
    if not cursor.fetchone():
        # 创建 private_messages 表
        cursor.execute('''
            CREATE TABLE private_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                role TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        logger.info("private_messages 表已创建！")
    conn.commit()
    conn.close()
