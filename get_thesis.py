from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs
import os, time, json, requests
from PIL import Image


def check_vcode(driver):    # 检测并人工填写验证码
    try:   # 有的时候需要点击一下IP登录
        Button2 = driver.find_element_by_id("Button2")
        Button2.click()
        time.sleep(5)
        vcode = driver.find_element_by_id("vcode")   # 填写验证码
        vImg = driver.find_element_by_id("vImg")   # 验证码图片
        img_path = "./data/vImg.png"
        vImg.screenshot(img_path)
        img = Image.open(img_path)
        display(img)    # 展示图片
        input_string = input("请输入验证码：")
        vcode.send_keys(input_string + "\n")
        os.remove(img_path)
        time.sleep(5)
    except:
        pass
    

def get_content(thesis_url, driver, display_b):
    driver.get(thesis_url)
    check_vcode(driver)
    try:
        topTitle_d = driver.find_element_by_id("topTitle")
        topTitle = topTitle_d.get_attribute('textContent')
    except:
        # 如果进到这里，可能是因为操作太过频繁，需要重新登录
        try:
            driver.close()
            if display_b == 'n':
                # 下面这段代码是不让模拟浏览器显示出来的，测试完代码之后启动
                chrome_options = Options()
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--disable-gpu')
                driver = webdriver.Chrome(chrome_options = chrome_options)
            else:
                driver = webdriver.Chrome()
            driver.get(thesis_url)
            check_vcode(driver)
            topTitle = driver.find_element_by_id("topTitle").get_attribute('textContent')
        except:
            # 如果到了这一步，那没办法，只能跳过了
            return driver
        
    topTitle = '、'.join(topTitle.split('/'))
    content = driver.find_element_by_class_name("content").get_attribute('textContent')
    # content中包含大量无用信息，如需主要信息则需要进一步处理
    # 考虑到下一步是自然语言处理，故采用此方法
    with open("./thesis/{}.txt".format(topTitle.strip()), "wt", encoding = "utf-8") as fo:
        fo.write(content)
    return driver


def get_literature(url, driver, name, display_b):
    header = {
        "Host":"kns.cnki.net",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36",
        "cookie":r"""Ecp_ClientId=2200624201703446328; RsPerPage=20; cnkiUserKey=6188a170-8f76-0ba1-7507-4e186c73d168; Ecp_ClientIp=219.217.157.44; x-s3-sid=>/lE28b``ugjwv6w/M1o38300; Ecp_loginuserbk=DB0060; style=lt; Hm_lvt_ba7af201fc75865e9846f701ccb53e6b=1619489343,1621435412; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221798514efd191a-040d5f445af37b-2363163-1327104-1798514efd235a%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%7D%2C%22%24device_id%22%3A%221798514efd191a-040d5f445af37b-2363163-1327104-1798514efd235a%22%7D; UM_distinctid=17bfdc96f256bf-08aa53a9250a05-a7d173c-144000-17bfdc96f2641a; Hm_lvt_6e967eb120601ea41b9d312166416aa6=1632050471; ASP.NET_SessionId=slvsmlc1pzaagwjl3wxys3qw; SID_kns8=15123122; Ecp_session=1; SID_kns_new=kns123120; _pk_ref=%5B%22%22%2C%22%22%2C1632571144%2C%22https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3DVMp7DaDNu98VjlkMPcIqu_Pt69OCg-Ce2Y1cyzS5VK_%26ck%3D805.0.213.158.152.NaN.NaN.0NaN.NaN.0%26shh%3Dwww.baidu.com%26sht%3D50000021_hao_pg%26wd%3D%26eqid%3D99ede8bf0012a9f4000000045ef3444e%22%5D; CurrSortField=%e5%8f%91%e8%a1%a8%e6%97%b6%e9%97%b4%2f(%e5%8f%91%e8%a1%a8%e6%97%b6%e9%97%b4%2c%27TIME%27); CurrSortFieldType=desc; SID_kcms=124114; yeswholedownload=%3Bsxjg202105022; _pk_id=03f8ea77-e542-4922-b42d-4b34026aed98.1607761093.26.1632572878.1632571144.; c_m_expire=2021-09-25 21:18:17; c_m_LinID=LinID=WEEvREcwSlJHSldSdmVpa3VEOHV2V3dHOUYweGZWS2YrTHIzNm9DTXN3bz0=$9A4hF_YAuvQ5obgVAqNKPCYcEjKensW4IQMovwHtwkF4VYPoHbKxJw!!&ot=09/25/2021 21:18:17; LID=WEEvREcwSlJHSldSdmVpa3VEOHV2V3dHOUYweGZWS2YrTHIzNm9DTXN3bz0=$9A4hF_YAuvQ5obgVAqNKPCYcEjKensW4IQMovwHtwkF4VYPoHbKxJw!!; Ecp_LoginStuts={"IsAutoLogin":false,"UserName":"DB0060","ShowName":"%E5%A4%A7%E8%BF%9E%E7%90%86%E5%B7%A5%E5%A4%A7%E5%AD%A6%E5%9B%BE%E4%B9%A6%E9%A6%86","UserType":"bk","BUserName":"","BShowName":"","BUserType":"","r":"hHcCCA"}"""
    }
    r = requests.get(url, headers = header)
    r.encoding = r.apparent_encoding
    soup = bs(r.text, "html.parser")
    li = soup.find("li", {"class":"btn-html"})
    if li == None or li.find('a') == None:
        print("文献{}不支持HTML阅读".format(name.encode('utf-8').decode('unicode_escape')))
        return driver
    thesis_url = "https:" + li.find('a').attrs["href"]
    driver = get_content(thesis_url, driver, display_b)
    return driver


def main():
    start = time.time()
    url_form = """https://kns.cnki.net/kcms/detail/detail.aspx?dbcode={}&dbname={}\
        &filename={}&uniplatform=NZKPT"""   # 这个是网址的填写模板
    display_b = input("是否显示模拟浏览器？(y/n)")
    if display_b == 'n':
        # 下面这段代码是不让模拟浏览器显示出来的，测试完代码之后启动
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(chrome_options = chrome_options)
    else:
        driver = webdriver.Chrome()
        # driver放在这里是为了在后面少输入几次验证码，即只打开一次模拟浏览器
    with open("./data/info_ls.json", 'rt', encoding = 'utf-8') as fi:
        i = 0
        for thesis in fi:
            thesis = json.loads(thesis.strip())
            thesis_name = thesis['name'].encode('utf-8').decode('unicode_escape').strip()
            thesis_path = "./thesis/{}.txt".format('、'.join(thesis_name.split('/')))
            if os.path.exists(thesis_path):
                continue   # 如果要爬的文献已经下载了，就跳过
            url = thesis['url']
            if "RedirectScholar" not in url:
                for tiankong in url.split('/')[-1].split('&'):
                    if "DbCode" in tiankong:
                        dbcode = tiankong.split('=')[-1]
                    elif "DbName" in tiankong:
                        dbname = tiankong.split('=')[-1]
                    elif "FileName" in tiankong:
                        filename = tiankong.split('=')[-1]
                url = url_form.format(dbcode, dbname, filename)
            driver = get_literature(url, driver, thesis['name'], display_b)
            print("\r已完成{}篇".format(thesis['seq']), end = '')
    driver.close()
    print("\r文献下载完毕，耗时：{}s".format(time.time() - start))
    
    
main()
