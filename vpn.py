import requests
from lxml import etree


def my_ip():
    page = 1
    while page < 3:
        vpn_list = []
        info_word = []
        url = 'http://www.xicidaili.com/wt/{}'.format(page)
        url_test = 'https://blog.csdn.net/op0912036/article/details/83901336'

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
        }

        proxies = {
            "http": 'http://175.148.69.162:1133'
        }

        resp = requests.get(url=url, headers=headers,proxies=proxies)

        content = resp.content.decode('utf-8')

        html = etree.HTML(content)
        info_max = html.xpath('//tr/td/text()')

        for i in info_max:
            if i.find('\n'):
                info_word.append(i)

        info_list = [info_word[i:i + 6] for i in range(0, len(info_word), 6)]
        for info in info_list:
            if info[2] == '高匿':
                vpn = 'http://' + info[0] + ':' + info[1]

                try:
                    proxies = {
                        "http": vpn
                    }
                    requests.get(url=url_test, headers=headers, proxies=proxies, timeout=10)

                    vpn_list.append(vpn)

                    with open("./files/vpn.txt", "a") as file:
                        file.write(vpn + '\n')
                except Exception as ex:
                    print(ex)
        print(vpn_list)

        page = page + 1
        print(page)


if __name__ == '__main__':
    my_ip()
