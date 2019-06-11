#coding=utf-8

import json
from urllib import request as rqst
from urllib import parse

'''
错误代码：000 请求次数超过限制
'''


class ChatRobot(object):
    def __int__(self):
        pass

    def chat_with_qyk(self, question):
        '''
        与青云客智能聊天机器人对话
        :param question: 问题
        :return: 答案
        '''
        url = 'http://api.qingyunke.com/api.php?key=free&appid=0&msg='
        url = url + parse.quote(question)
        response = rqst.urlopen(url).read()  # json format
        response_dict = json.loads(response.decode())
        if response_dict['result'] == 0:
            answer = response_dict['content']
        else:
            answer = "对不起，小科出现了一点问题QAQ，请联系管理员解决！【错误代码】000"
        return answer

    def chat_with_tulin(self, uid, question):
        '''
        调用图灵机器人聊天
        :param uid: 用户的唯一识别串，可以是名字
        :param question: 用户提的问题
        :return: 答案
        '''
        answer = ''
        data = {
            "perception": {
                "inputText": {
                    "text": question,
                },
                "selfInfo": {
                    "location": {
                        "city": "苏州",
                        "province": "江苏",
                        "street": "仁爱路"
                    }
                }
            },
            "userInfo": {
                "apiKey": "33d741c8fb844b6f8d17e524e7179663",
                # "apiKey": "588d7fd064554687b34f0568c107efae",
                "userId": uid,
            }
        }
        jsondata_as_bytes = json.dumps(data).encode('utf-8')
        url = "http://openapi.tuling123.com/openapi/api/v2"
        req = rqst.Request(url)
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        req.add_header('Content-Length', len(jsondata_as_bytes))
        response = rqst.urlopen(req, jsondata_as_bytes).read()  # json format
        response_dict = json.loads(response.decode())
        if 'results' not in response_dict.keys():
            results = [{
                "resultType": "text",
                "values": {
                    "text": "对不起，小科出现了一点问题QAQ，请联系管理员解决！"
                }
            }]
        else:
            results = response_dict['results']
        for result in results:
            if result['resultType'] == 'url':
                answer = answer + '链接：' + result['values']['url'] + '。'
            else:
                answer = answer + result['values']['text']

        if answer == '请求次数超限制!':
            answer = "Error"
        return answer


if __name__ == '__main__':
    R = ChatRobot()
    while True:
        q = input("请输入问题：")
        a = R.chat_with_qyk(q)
        print(a)