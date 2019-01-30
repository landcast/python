import requests
import jsonpath
import json
import time


class LaGou(object):

    def __init__(self, work):
        self.url = 'https://www.lagou.com/jobs/positionAjax.json?city=%E5%8C%97%E4%BA%AC&needAddtionalResult=false'
        # self.url = 'https://www.baidu.com'
        self.headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36', 'Referer': 'https://www.lagou.com/jobs/list_%E7%88%AC%E8%99%AB?city=%E5%8C%97%E4%BA%AC&cl=false&fromSearch=true&labelWords=&suginput=' }
        # self.proxies = { 'http': 'http://qtmp005:Aa123456@10.0.60.80:8080' }
        self.work = work
        self.file = open('work.json', 'w', encoding='utf-8')

    def get_data(self, url, count):
        session = requests.session()
        data = { 'first': 'true', 'pn': str(count), 'kd': self.work }
        r = session.post(url, headers=self.headers, data=data)
        print(r.status_code)
        return r.content

    def parse_data(self, data):
        data_dict = json.loads(data.decode())
        result = jsonpath.jsonpath(data_dict, '$..positionResult.result')
        details_url = []
        print('result', result)
        for res in result:
            for content in res:
                temp = dict()
                temp['company'] = content['companyFullName']
                temp['work'] = content['positionName']
                temp['education'] = content['education']
                temp['salary'] = content['salary']
                temp['CreateTime'] = content['formatCreateTime']
                temp['details_url'] = 'https://www.lagou.com/jobs/' + str(content['positionId']) + '.html'
                details_url.append(temp)
                return details_url

    def save_data(self, work):
        data = json.dumps(work, ensure_ascii=False) + ',\r'
        self.file.write(data)

    def __del__(self):
        self.file.close()

    def run(self):
        url = self.url
        count = 0
        while True:
            count += 1
            time.sleep(4)
            data = self.get_data(url, count)
            work_list = self.parse_data(data)
            print('正在保存第{}页数据!'.format(count))
            for work in work_list:
                self.save_data(work)
                print('保存完毕')
            print('--------------------------------')


if __name__ == '__main__':
    lagou = LaGou('爬虫')
    lagou.run()
