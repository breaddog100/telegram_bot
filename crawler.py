import requests
from bs4 import BeautifulSoup
import chardet

def get_search_results(query_url):
    """
    从指定的 SearxNG 服务获取搜索结果
    :param query_url: 搜索请求的 URL
    :return: 搜索结果的 JSON 数据
    """
    try:
        response = requests.get(query_url)
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
        response = requests.get(url)
        response.raise_for_status()
        # 尝试从响应头中获取字符集
        content_type = response.headers.get('Content-Type')
        if content_type and 'charset=' in content_type:
            charset = content_type.split('charset=')[-1]
            response.encoding = charset
        else:
            # 若响应头中没有字符集信息，使用 chardet 检测
            detected = chardet.detect(response.content)
            response.encoding = detected['encoding']
        # 去除 BOM（如果存在）
        content = response.content
        if content.startswith(b'\xef\xbb\xbf'):
            content = content[3:]
        # 使用 response.content 并指定字符编码
        soup = BeautifulSoup(content, 'html.parser', from_encoding=response.encoding)
        # 提取页面的文本内容
        text = soup.get_text()
        return text
    except requests.RequestException as e:
        print(f"请求 {url} 时出错: {e}")
        return None

def main():
    query = "今天几号"
    query_url = f"http://198.135.50.173:56880/search?q={requests.utils.quote(query)}&format=json"
    # 获取搜索结果
    search_result = get_search_results(query_url)
    if search_result:
        # 获取前 10 个页面链接
        top_10_links = get_top_10_links(search_result)
        for link in top_10_links:
            print(f"正在获取 {link} 的内容...")
            content = fetch_page_content(link)
            if content:
                print(f"内容: {content[:200]}...")  # 打印前 200 个字符

if __name__ == "__main__":
    main()
