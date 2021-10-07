from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs
import os, time, json, requests
from PIL import Image


def get_string(a_string):
    a_string = ''.join((''.join(a_string.split("<sub>"))).split("</sub>"))   # 删去sub标签
    a = ''.join((''.join(a_string.split("<sup>"))).split("</sup>"))   # 删去sup标签
    return a.split('<')[-2].split('>')[-1].strip()


def check_vericode(driver, j):    # 检验是否需要验证码，需要的话显示验证码图片，并人工输入验证码
    # j 是布尔值，用于判断是否需要改变验证码
    vericode = driver.find_element_by_id('vericode')   # 这个是验证码输入框
    changeVercode = driver.find_element_by_id('changeVercode')    # 这个是验证码图片
    if j:   # 如果 j 是 True，就点击验证码图片，换一个验证码
        changeVercode.click()
    img_path = "./data/vericode.png"
    changeVercode.screenshot(img_path)
    img = Image.open(img_path)
    display(img)    # 展示图片
    input_string = input("请输入验证码：")
    vericode.send_keys(input_string + "\n")
    os.remove(img_path)   # 删掉验证码图片
    time.sleep(10)


def get_page(input_string):   # 获取每一页的源代码
    display = input("是否显示模拟浏览器？(y/n)")   # 默认为yes
    print("开始获取网页源代码步骤")
    html_ls = []   # 获取的HTML源代码全部放在这里
    if display == 'n':
        # 下面这段代码是不让模拟浏览器显示出来的，测试完代码之后启动
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(chrome_options = chrome_options)
    else:
        driver = webdriver.Chrome()
    url = "https://kns.cnki.net/kns8/defaultresult/index"
    driver.get(url)
    txt_search = driver.find_element_by_id('txt_search')
    txt_search.send_keys(input_string + "\n")    # 这个 '\n' 可以直接当回车用，就不用点击了
    time.sleep(10)   # 等一会儿，不然有些信息加载不出来
    html = driver.page_source   # 获取网页源代码
    html_ls.append(html)
    soup = bs(html, "html.parser")
    div = soup.find("div", {"class":"all-box"})
    em = div.find("em")
    print("共 {} 篇文献".format(em.string))   # em.string 包含的是获取的文献总数
    num = (int(em.string) - 1)//20   # 每页有20篇文献，-1是为了20的倍数时别多翻页
    print("\r已完成 {}/{} 页".format(1, num + 1), end = '')
    if num > 0:
        for i in range(num):
            try:
                PageNext = driver.find_element_by_id("PageNext")
                PageNext.click()
                time.sleep(7)
                
                j = False
                while True:   # 这个循环是用于检测验证码的
                    try:
                        vericode = driver.find_element_by_id('vericode')
                    except:
                        break
                    else:
                        check_vericode(driver, j)
                        j = True
                
                html_ls.append(driver.page_source)
                print("\r已完成 {}/{}".format(i + 2, num + 1), end = '')
            except:
                print("\n进展到第 {} 页时出了问题。".format(i+2))

        print("\r获取网页源代码步骤完毕")
    driver.close()
    return html_ls


def get_infos(html):   # 获取所有文献的基本信息，包括文献url, 标题，作者等，尽可能多得获取信息
    soup = bs(html, "html.parser")
    tbody = soup.find("tbody")
    tr_ls = tbody.find_all("tr")
    for j, tr in enumerate(tr_ls):
        tr_dic = {}
        tr_dic["seq"] = get_string(str(tr.find("td", {"class":"seq"})))  # 文献的序号，好像没啥意义，加上再说
        name = tr.find("td", {"class":"name"}).find('a')
        tr_dic["url"] = "https://kns.cnki.net" + name.attrs["href"]   # 文献的url
        try:
            tr_dic["name"] = name.string.strip()   # 文献的名称
        except:
            tr_dic["name"] = get_string(str(name))
        authors = tr.find("td", {"class":"author"}).find_all('a')
        tr_dic["author"] = [a.string for a in authors]     # 作者信息
        source = tr.find("td", {"class":"source"})
        if source.find('a') == None:
            source = source.string.strip()
        else:
            source = source.find('a').string.strip()
        tr_dic["source"] = source   # 文献的来源
        tr_dic["date"] = tr.find("td", {"class":"date"}).string.strip()   # 文献的发表日期
        tr_dic["data"] = tr.find("td", {"class":"data"}).string.strip()   # 文献的来源数据库
        a = tr.find("td", {"class":"quote"}).find('a')
        if a == None:
            num = 0
        else:
            num = int(a.string)
        tr_dic["quote"] = num   # 文献的被引用次数
        with open("./data/info_ls.json", "at", encoding = 'utf-8') as fo:
            fo.write(json.dumps(tr_dic))   # 把数据以json格式备份
            fo.write('\n')
        print("\r已完成 {} 篇".format(tr_dic["seq"]), end = '')
        
        
def main():
    input_string = input("请输入想搜索的关键词：")   # 索引关键词
    start_1 = time.time()
    if not os.path.exists("./data/html_ls.txt"):
        html_ls = get_page(input_string)
        with open("./data/html_ls.txt", "wt", encoding = 'utf-8') as fo:
            fo.write(json.dumps(html_ls))   # 备份数据
    else:
        print("网页信息已存在，直接分析数据")
        with open("./data/html_ls.txt", "rt", encoding = 'utf-8') as fi:
            html_ls = json.loads(fi.read())
    start_2 = time.time()
    print("耗时 {} s".format(start_2 - start_1))
    
    print("开始获取文献基本信息步骤")
    for html in html_ls:
        get_infos(html)
    print("\r获取文献基本信息步骤完毕")
    start_3 = time.time()
    print("耗时 {} s".format(start_3 - start_2))
    print("该阶段完成")

    
main()
