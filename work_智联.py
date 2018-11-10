"""
https://sou.zhaopin.com/?p=2&jl=719&sf=4001&st=6000&kw=python&kt=3
p:页数
jl:工作地点参数
sf:最低薪资     //可不要
st:最高薪资     //可不要
kw:搜索的关键字
kt:以职位名搜索
"""
import requests
import re
import pymysql
from threading import Thread


class RecruitSpider:
    def __init__(self, query, host, port, db, user, passwd, charset='utf8'):
        """初始化参数"""
        self.url_web = "https://m.zhaopin.com/zhengzhou-719/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Mobile Safari/537.36",

        }
        self.proxies = {
            "https": "https://202.112.237.102:3128"
        }
        self.params = {
            'keyword': query,
            'pageindex': 1
        }

        self.host = host
        self.port = port
        self.db = db
        self.user = user
        self.passwd = passwd
        self.charset = charset

    def parse_url(self, url, data=None, method='get'):
        """解析url，获取响应内容"""
        if method == 'get':
            resp = requests.get(url=url, params=self.params, headers=self.headers)
        else:
            resp = requests.post(url=url, data=data, headers=self.headers)

        return resp.content.decode('utf-8')

    # 连接数据库
    def connect(self):
        self.conn = pymysql.connect(host=self.host, port=self.port, db=self.db, user=self.user, passwd=self.passwd,
                                    charset=self.charset)
        self.cursor = self.conn.cursor()

    # 关闭数据库
    def close(self):
        self.cursor.close()
        self.conn.close()

    # 修改数据
    def __edit(self, sql, params):
        count = 0
        try:
            self.connect()
            count = self.cursor.execute(sql, params)
            self.conn.commit()
            self.close()
        except Exception as e:
            print(e)
        return count

    def run(self):
        """核心逻辑"""

        while True:

            content = self.parse_url(url=self.url_web)

            # 将网页源代码保存
            with open("./files/recruit.html", "w") as file:
                file.write(content)

            # 数据提取
            work_list = re.findall(r'<div class="job-name fl ">(.*?)</div>', content)
            salary_list = re.findall(r'<div class="fl">(.*?)</div>', content)
            company_list = re.findall(r'<div class="comp-name fl">(.*?)</div>', content)
            web_list = re.findall(r'<a class="boxsizing" data-link="(.*?)">', content)
            updatetime_list = re.findall(r'<div class="time fr">(.*?)</div>', content)

            for i in web_list:
                try:
                    # 获取本次数据的下标
                    index = web_list.index(i)
                    # 根据下标获取对应数据
                    if i.find('xiaoyuan') != -1:
                        print(i)
                        continue
                    else:
                        url_info = 'https://m.zhaopin.com/' + i

                    content_info = self.parse_url(url=url_info)

                    with open("./files/company.html", "w") as file:
                        file.write(content_info)

                    # 数据提取
                    address_list = re.findall(r'<div class="add"><i class="i_city"></i>(.*?)</div>', content_info)
                    job_list = re.findall(r'<div class="compaydetail-box">(.*?)</div>', content_info)
                    requirement_list = re.findall(r'<span class="exp">(.*?)<div class="time fr">', content_info, re.S)
                    createtime_list = re.findall(r'<span class="exp">.*?<div class="time fr">(.*?)</div>', content_info,
                                                 re.S)

                    # 获取要写入的数据
                    company = company_list[index]
                    print(company)
                    work = work_list[index]
                    requirement = requirement_list[0].replace('\n', '').replace(' ', '').replace('</span><span>',
                                                                                                 '  ').replace(
                        '<span>', '').replace('</span>', '').replace('</div>', '')
                    salary = salary_list[index]
                    job_main = job_list[0].replace('<br/>', '').replace('<p><p>', '<p>').replace('<p>', '')
                    address = address_list[0]
                    updatetime = updatetime_list[index]
                    createtime = createtime_list[0]

                    # 写入数据库
                    sql = 'insert into Worm(company,work,requirement,salary,address,job_main,updatetime,createtime) values(%s,%s,%s,%s,%s,%s,%s,%s)'
                    params = [company, work, requirement, salary, address, job_main, updatetime, createtime]
                    self.__edit(sql, params)
                except Exception as ex:
                    print(ex)

            # 判断是否到尾页
            next_page = re.findall(r'class="nextpage">></a>', content)

            if next_page:
                self.params['pageindex'] = self.params['pageindex'] + 1
                print(self.params['pageindex'])
            else:
                break


if __name__ == '__main__':
    # query = input('请输入职位：')
    query = '爬虫'

    recruit = RecruitSpider(query, 'localhost', 3306, 'Spider', 'root', '55555')
    thread_spiders = []
    for i in range(10):
        thread_spider = Thread(target=recruit.run)
        thread_spiders.append(thread_spider)
        thread_spider.start()

    for item in thread_spiders:
        item.join()


