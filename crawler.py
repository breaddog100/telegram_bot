import requests
from bs4 import BeautifulSoup
from charset_normalizer import from_bytes

def get_search_results(query_url):
    """
    从指定的 SearxNG 服务获取搜索结果
    :param query_url: 搜索请求的 URL
    :return: 搜索结果的 JSON 数据
    """
    try:
        response = requests.get(query_url, timeout=5)  # 设置超时为 5 秒
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"获取搜索结果时出错: {e}")
        return None

def get_top_10_links(result):
    """
    根据相关性分数对搜索结果排序，提取前 10 个页面链接
    :param result: 搜索结果
    :return: 前 10 个页面链接列表
    """
    sorted_results = sorted(result['results'], key=lambda x: x.get('score', 0), reverse=True)
    links = [item['url'] for item in sorted_results[:10]]
    return links

def fetch_page_content(url):
    """
    获取指定页面的内容
    :param url: 页面链接
    :return: 页面内容的文本
    """
    try:
        response = requests.get(url, timeout=5)  # 设置超时为 5 秒
        response.raise_for_status()
        # 打印原始内容的前 200 字节
        print(f"原始内容: {response.content[:200]}")
        # 使用 charset-normalizer 检测编码
        detected = from_bytes(response.content).best()
        print(f"检测到的编码: {detected.encoding if detected else '未知'}")
        if detected:
            response.encoding = detected.encoding
        # 去除 BOM（如果存在）
        content = response.content
        if content.startswith(b'\xef\xbb\xbf'):
            content = content[3:]
        # 使用 lxml 解析器
        soup = BeautifulSoup(content, 'lxml')
        # 提取页面的文本内容
        text = soup.get_text()
        # 去掉空行
        text = "\n".join(line for line in text.splitlines() if line.strip())
        return text
    except requests.Timeout:
        print(f"请求 {url} 超时")
        return None
    except requests.RequestException as e:
        print(f"请求 {url} 时出错: {e}")
        return None
