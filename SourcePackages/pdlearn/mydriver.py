from typing import List, Any

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions
from selenium.webdriver.chrome.options import Options
from pdlearn import user_agent
from bs4 import BeautifulSoup
import lxml
import os
import time
import requests
import random
from urllib.parse import quote
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class title_of_login:
    def __call__(self, driver):
        """ 用来结合webDriverWait判断出现的title """
        is_title1 = bool(EC.title_is(u'我的学习')(driver))
        is_title2 = bool(EC.title_is(u'系统维护中')(driver))
        if is_title1 or is_title2:
            return True
        else:
            return False


class Mydriver:

    def __init__(self, noimg=True, nohead=True):
        try:
            self.options = Options()
            if os.path.exists("./chrome/chrome.exe"):  # win
                self.options.binary_location = "./chrome/chrome.exe"
            elif os.path.exists("/opt/google/chrome/chrome"):  # linux
                self.options.binary_location = "/opt/google/chrome/chrome"
            if noimg:
                self.options.add_argument('blink-settings=imagesEnabled=true')  # 不加载图片, 提升速度，但无法显示二维码
            if nohead:
                self.options.add_argument('--headless')
                self.options.add_argument('--disable-extensions')
                self.options.add_argument('--disable-gpu')
                self.options.add_argument('--no-sandbox')
            self.options.add_argument('--mute-audio')  # 关闭声音
            self.options.add_argument('--window-size=400,500')
            # self.options.add_argument('--window-size=900,800')
            self.options.add_argument('--window-position=700,0')
            self.options.add_argument('--log-level=3')

            self.options.add_argument('--user-agent={}'.format(user_agent.getheaders()))
            self.options.add_experimental_option('excludeSwitches', ['enable-automation'])  # 绕过js检测
            self.webdriver = webdriver
            if os.path.exists("./chrome/chromedriver.exe"):  # win
                self.driver = self.webdriver.Chrome(executable_path="./chrome/chromedriver.exe",
                                                    chrome_options=self.options)
            elif os.path.exists("./chromedriver"):  # linux
                self.driver = self.webdriver.Chrome(executable_path="./chromedriver",
                                                    chrome_options=self.options)
            elif os.path.exists("/usr/lib64/chromium-browser/chromedriver"):  # linux 包安装chromedriver
                self.driver = self.webdriver.Chrome(executable_path="/usr/lib64/chromium-browser/chromedriver",
                                                    chrome_options=self.options)
            elif os.path.exists("/usr/local/bin/chromedriver"):  # linux 包安装chromedriver
                self.driver = self.webdriver.Chrome(executable_path="/usr/local/bin/chromedriver",
                                                    chrome_options=self.options)
            else:
                self.driver = self.webdriver.Chrome(chrome_options=self.options)
        except:
            print("=" * 120)
            print("Mydriver初始化失败")
            print("=" * 120)
            raise

    def login(self):
        print("正在打开二维码登陆界面,请稍后")
        self.driver.get("https://pc.xuexi.cn/points/login.html")
        try:
            remover = WebDriverWait(self.driver, 30, 0.2).until(
                lambda driver: driver.find_element_by_class_name("redflagbox"))
        except exceptions.TimeoutException:
            print("网络缓慢，请重试")
        else:
            self.driver.execute_script('arguments[0].remove()', remover)
        try:
            remover = WebDriverWait(self.driver, 30, 0.2).until(
                lambda driver: driver.find_element_by_class_name("layout-header"))
        except exceptions.TimeoutException:
            print("当前网络缓慢...")
        else:
            self.driver.execute_script('arguments[0].remove()', remover)
        try:
            remover = WebDriverWait(self.driver, 30, 0.2).until(
                lambda driver: driver.find_element_by_class_name("layout-footer"))
        except exceptions.TimeoutException:
            print("当前网络缓慢...")
        else:
            self.driver.execute_script('arguments[0].remove()', remover)
            self.driver.execute_script('window.scrollTo(document.body.scrollWidth/2 - 200 , 0)')
        try:
            # WebDriverWait(self.driver, 270).until(EC.title_is(u"我的学习"))
            WebDriverWait(self.driver, 270).until(title_of_login())
            cookies = self.get_cookies()
            return cookies
        except:
            print("扫描二维码超时")

    def dd_login(self, d_name, pwd):
        __login_status = False
        self.driver.get(
            "https://login.dingtalk.com/login/index.htm?"
            "goto=https%3A%2F%2Foapi.dingtalk.com%2Fconnect%2Foauth2%2Fsns_authorize"
            "%3Fappid%3Ddingoankubyrfkttorhpou%26response_type%3Dcode%26scope%3Dsnsapi"
            "_login%26redirect_uri%3Dhttps%3A%2F%2Fpc-api.xuexi.cn%2Fopen%2Fapi%2Fsns%2Fcallback"
        )
        self.driver.find_elements_by_id("mobilePlaceholder")[0].click()
        self.driver.find_element_by_id("mobile").send_keys(d_name)
        self.driver.find_elements_by_id("mobilePlaceholder")[1].click()
        self.driver.find_element_by_id("pwd").send_keys(pwd)
        self.driver.find_element_by_id("loginBtn").click()
        try:
            print("登陆中...")
            WebDriverWait(self.driver, 2, 0.1).until(lambda driver: driver.find_element_by_class_name("modal"))
            print(self.driver.find_element_by_class_name("modal").find_elements_by_tag_name("div")[0].text)
            self.driver.quit()
            __login_status = False
        except:
            __login_status = True
        return __login_status

    def get_cookies(self):
        cookies = self.driver.get_cookies()
        return cookies

    def set_cookies(self, cookies):
        for cookie in cookies:
            self.driver.add_cookie({k: cookie[k] for k in cookie.keys()})

    def get_url(self, url):
        self.driver.get(url)

    def go_js(self, js):
        self.driver.execute_script(js)

    def quit(self):
        self.driver.quit()

    def click_xpath(self, xpath):
        try:
            self.condition = EC.visibility_of_element_located(
                (By.XPATH, xpath))
            WebDriverWait(driver=self.driver, timeout=15, poll_frequency=1).until(self.condition)
        except Exception as e:
            print('一点小问题：', e)
        self.driver.find_element_by_xpath(xpath).click()

    def xpath_getText(self, xpath):
        self.condition = EC.visibility_of_element_located(
            (By.XPATH, xpath))
        WebDriverWait(driver=self.driver, timeout=15, poll_frequency=1).until(self.condition)
        return self.driver.find_element_by_xpath(xpath).text

    def check_delay(self):
        delay_time = random.randint(2, 15)
        print('等待 ', delay_time, ' 秒')
        time.sleep(delay_time)

    def _view_tips(self):
        # global answer
        content = ""
        try:
            # tips_open = self.driver.find_element_by_xpath('//*[@id="app"]/div/div[2]/div/div[4]/div[1]/div[3]/span')
            tips_open = self.driver.find_element_by_xpath(
                '//*[@id="app"]/div/div[*]/div/div[*]/div[*]/div[*]/span[contains(text(), "查看提示")]')
            tips_open.click()
            print("有可点击的【查看提示】按钮")
        except Exception as e:
            print("没有可点击的【查看提示】按钮")
            return ""
        time.sleep(2)
        try:
            # tips_open = self.driver.find_element_by_xpath('//*[@id="app"]/div/div[2]/div/div[4]/div[1]/div[3]/span')
            tips_open = self.driver.find_element_by_xpath(
                '//*[@id="app"]/div/div[*]/div/div[*]/div[*]/div[*]/span[contains(text(), "查看提示")]')
            tips_open.click()
        except Exception as e:
            print("关闭查看提示失败！")
            return ""
        try:
            html = self.driver.page_source
            soup1 = BeautifulSoup(html, 'lxml')
            content = soup1.find_all('font')  # tips.get_attribute("name") ,attrs={'color'}
            answer: List[str] = []
        except Exception as e:
            print('page_source failed')
            print(e)
        try:
            for i in content:
                answer.append(i.text)
                '''
            if len(answer) >= 2:
                answer=str.join(answer)
            if (',' or '.' or '，' or '。' or '、') in answer:
                answer=re.split(",|，|.|。|、",answer)
                '''
            print('获取提示：', answer)
        except Exception as e:
            print('无法查看提示内容')
            print(e)
            return ""
        time.sleep(2)

        try:
            tips_close = self.driver.find_element_by_xpath('//*[@id="app"]/div/div[2]/div/div[4]/div[1]/div[1]')
            tips_close.click()
        except Exception as e:
            print("没有可点击的【关闭提示】按钮")
        time.sleep(2)
        return answer

    def radio_get_options(self):
        html = self.driver.page_source
        soup1 = BeautifulSoup(html, 'lxml')
        content = soup1.find_all('div', attrs={'class': 'q-answer choosable'})
        options = []
        for i in content:
            options.append(i.text)
        print('获取选项：', options)
        return options

    def radio_check(self, check_options):
        for check_option in check_options:
            try:
                self.driver.find_element_by_xpath(
                    '//*[@id="app"]/div/div[*]/div/div[*]/div[*]/div[*]/div[contains(text(), "' + check_option + '")]').click()
            except Exception as e:
                print("点击", check_option, '失败！')
        self.check_delay()
        submit = WebDriverWait(self.driver, 15).until(lambda driver: driver.find_element_by_class_name("action-row").find_elements_by_xpath("button"))
        if len(submit) > 1:
            self.click_xpath('//*[@id="app"]/div/div[2]/div/div[6]/div[2]/button[2]')
            print("成功点击交卷！")
        else:
            self.click_xpath('//*[@id="app"]/div/div[*]/div/div[*]/div[*]/button')
            print("点击进入下一题")

    def blank_get(self):
        html = self.driver.page_source
        soup1 = BeautifulSoup(html, 'lxml')
        content = soup1.find_all('div', attrs={'class': 'q-body'})
        print('原始', content)
        content = soup1.find('div', attrs={'class': 'q-body'}).getText()
        print(content)
        # content1=content.text
        dest = re.findall(r'.{0,2}\s+.{0,2}', content)
        print('填空反馈')
        print(dest)

    def fill_in_blank(self, answer):
        for i in range(0, len(answer)):
            self.driver.find_element_by_xpath(
                '//*[@id="app"]/div/div[2]/div/div[4]/div[1]/div[2]/div/input[' + str(i + 1) + ']').send_keys(answer[i])
        self.check_delay()
        submit = WebDriverWait(self.driver, 15).until(
            lambda driver: driver.find_element_by_class_name("action-row").find_elements_by_xpath("button"))
        if len(submit) > 1:
            self.click_xpath('//*[@id="app"]/div/div[2]/div/div[6]/div[2]/button[2]')
            print("成功点击交卷！")
        else:
            self.click_xpath('//*[@id="app"]/div/div[*]/div/div[*]/div[*]/button')
            print("点击进入下一题")

    def zhuanxiang_fill_in_blank(self, answer):
        for i in range(0, len(answer)):
            self.driver.find_element_by_xpath(
                '//*[@id="app"]/div/div[2]/div/div[6]/div[1]/div[2]/div/input[' + str(i + 1) + ']').send_keys(answer[i])
        self.check_delay()
        submit = WebDriverWait(self.driver, 15).until(
            lambda driver: driver.find_element_by_class_name("action-row").find_elements_by_xpath("button"))
        if len(submit) > 1:
            self.click_xpath('//*[@id="app"]/div/div[2]/div/div[6]/div[2]/button[2]')
            print("成功点击交卷！")
        else:
            self.click_xpath('//*[@id="app"]/div/div[*]/div/div[*]/div[*]/button')
            print("点击进入下一题")

    def _search(self, content, options, exclude=''):
        # 职责 网上搜索
        print(f'搜索 {content} <exclude = {exclude}>')
        print(f"选项 {options}")
        content = re.sub(r'[\(（]出题单位.*', "", content)
        if options[-1].startswith("以上") and chr(len(options) + 64) not in exclude:
            print(f'根据经验: {chr(len(options) + 64)} 很可能是正确答案')
            return chr(len(options) + 64)
        # url = quote('https://www.baidu.com/s?wd=' + content, safe=string.printable)
        url = quote("https://www.sogou.com/web?query=" + content, safe=string.printable)
        response = requests.get(url, headers=self.headers).text
        counts = []
        for i, option in zip(['A', 'B', 'C', 'D', 'E', 'F'], options):
            count = response.count(option)
            counts.append((count, i))
            print(f'{i}. {option}: {count} 次')
        counts = sorted(counts, key=lambda x: x[0], reverse=True)
        counts = [x for x in counts if x[1] not in exclude]
        c, i = counts[0]
        if 0 == c:
            # 替换了百度引擎为搜狗引擎，结果全为零的机会应该会大幅降低       
            _, i = random.choice(counts)
            print(f'搜索结果全0，随机一个 {i}')
        print(f'根据搜索结果: {i} 很可能是正确答案')
        return i
