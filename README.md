# ckni_spider
知网爬虫
1. 该爬虫项目主要使用selenium模拟Chrome浏览器爬取文献，因为本人用Chrome进入知网页面会自动登录所在大学图书馆的机构账号，故给我省去了很多事情；
2. 涉及验证码的部分都是对验证码截图之后展示，然后由人工方式输入的（大神可考虑使用机器学习方式解决）；
3. 编辑代码及测试代码都是在 Jupyter notebook 中完成的，python版本为3.7；
4. 该项目代码运行非常耗时，尤其是最后的文献爬取步骤；
5. 爬取的文献中含有大量垃圾文本，因精力所限，暂未对垃圾文本剔除（有时间会做进一步处理）；
6. 原项目下一步为自然语言处理，故爬取文献是在HTML阅读界面进行的；
7. 如果要先运行python文件，运行 get_thesis_info.py，后为 get_thesis.py。
