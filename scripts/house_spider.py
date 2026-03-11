#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
房产爬虫 - 禅城区保利同济府
使用 Selenium + Chrome 模拟浏览器访问
尝试绕过反爬虫机制
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time
import random


def create_driver(headless=False):
    """创建 Chrome 浏览器"""
    options = Options()

    if headless:
        options.add_argument("--headless")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # 更真实的浏览器特征
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # 去除 webdriver 特征
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    })

    return driver


def human_delay():
    """模拟人类延迟"""
    time.sleep(random.uniform(0.5, 1.5))


def try_lianjia_api(driver, community_name):
    """尝试通过链家API获取数据"""
    print("[尝试] 链家API...")

    # 尝试直接访问小区详情页
    # 佛山保利同济府的ID需要查找，这里先试试搜索
    url = f"https://fs.lianjia.com/xq/"

    driver.get(url)
    human_delay()

    # 尝试找到搜索框
    try:
        # 尝试多种搜索框选择器
        selectors = [
            "#searchInput",
            ".search-input",
            "input[placeholder*='找房']",
            "input[placeholder*='小区']",
            "input[class*='search']"
        ]

        for selector in selectors:
            try:
                search_box = driver.find_element(By.CSS_SELECTOR, selector)
                search_box.clear()
                search_box.send_keys(community_name)
                human_delay()
                search_box.submit()
                human_delay()
                print(f"[成功] 使用选择器: {selector}")
                return driver.page_source
            except:
                continue

    except Exception as e:
        print(f"[错误] 搜索失败: {e}")

    return None


def try_anjuke(driver, community_name):
    """尝试安居客"""
    print("[尝试] 安居客...")

    try:
        driver.get("https://m.foshan.anjuke.com/")
        human_delay()

        # 查找搜索框
        selectors = [
            "input.search-input",
            "input[placeholder='搜索小区/楼盘']",
            ".search-bar input"
        ]

        for selector in selectors:
            try:
                search_box = driver.find_element(By.CSS_SELECTOR, selector)
                search_box.clear()
                search_box.send_keys(community_name)
                human_delay()
                search_box.submit()
                human_delay()
                return driver.page_source
            except:
                continue

    except Exception as e:
        print(f"[错误] 安居客失败: {e}")

    return None


def try_wuba(driver, community_name):
    """尝试58同城"""
    print("[尝试] 58同城...")

    try:
        driver.get("https://foshan.58.com/xiaoqu/")
        human_delay()

        # 查找搜索框
        search_box = driver.find_element(By.CSS_SELECTOR, "#keyword")
        search_box.clear()
        search_box.send_keys(community_name)
        human_delay()

        # 点击搜索按钮
        search_btn = driver.find_element(By.CSS_SELECTOR, ".searchbtn")
        search_btn.click()
        human_delay()

        return driver.page_source

    except Exception as e:
        print(f"[错误] 58同城失败: {e}")

    return None


def try_direct_url(driver):
    """尝试直接访问可能的URL"""
    print("[尝试] 直接URL...")

    # 可能的URL模式
    urls = [
        "https://fs.lianjia.com/xq/511100.html",  # 假设ID
        "https://fs.lianjia.com/xq/511102.html",
        "https://foshan.anjuke.com/community/",
    ]

    for url in urls:
        try:
            driver.get(url)
            human_delay()
            if "登录" not in driver.page_source and "验证码" not in driver.page_source:
                print(f"[可能] 访问: {url}")
                return driver.page_source
        except:
            continue

    return None


def parse_results(html, source_name):
    """解析搜索结果"""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, 'html.parser')
    results = []

    print(f"[解析] {source_name}...")

    # 查找价格信息
    price_patterns = [
        '.price .num',
        '.unit-price',
        '[class*="price"]',
        '.avg-price',
        '.house-price'
    ]

    for pattern in price_patterns:
        elems = soup.select(pattern)
        for elem in elems:
            text = elem.get_text(strip=True)
            if text and ('元' in text or '万' in text or '/㎡' in text):
                results.append(f"价格: {text}")

    # 查找房源标题
    title_patterns = [
        '.title',
        '.house-title',
        '.item-title',
        'a[href*="/ershoufang/"]'
    ]

    for pattern in title_patterns:
        elems = soup.select(pattern)
        for elem in elems[:3]:
            text = elem.get_text(strip=True)
            if text and len(text) > 5:
                results.append(f"房源: {text}")

    return results


def main():
    community = "保利同济府"

    print("=" * 50)
    print(f"开始搜索: {community}")
    print("=" * 50)

    # 先试试无头模式
    print("\n[模式1] 无头模式...")
    driver = create_driver(headless=True)

    try:
        # 尝试各种数据源
        html = try_lianjia_api(driver, community)
        if html:
            results = parse_results(html, "链家")
            if results:
                print("\n[成功] 找到数据:")
                for r in results[:5]:
                    print(f"  - {r}")
                return

        # 尝试安居客
        html = try_anjuke(driver, community)
        if html:
            results = parse_results(html, "安居客")
            if results:
                print("\n[成功] 找到数据:")
                for r in results[:5]:
                    print(f"  - {r}")
                return

    finally:
        driver.quit()

    # 无头模式失败，试试有头模式
    print("\n[模式2] 有头模式（可见浏览器）...")

    # 这个需要用户手动操作，先跳过
    print("[跳过] 有头模式需要手动操作")

    print("\n[失败] 未能自动获取数据")
    print("\n建议:")
    print("1. 手动打开链家APP/网站")
    print("2. 搜索'保利同济府'")
    print("3. 截图发给我")


if __name__ == "__main__":
    main()
