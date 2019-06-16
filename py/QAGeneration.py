# -*- coding: utf-8 -*-
import os
import json
from pyltp import *


LTP_DATA_DIR = '~/qa_data/ltp_data_v3.4.0'  # ltp模型目录的路径

par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')  # 依存句法分析模型路径，模型名称为`parser.model`
pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注模型路径，模型名称为`pos.model`
cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')  # 分词模型路径，模型名称为`cws.model`

ask_word = ["如何", "什么", "哪些", "吗", "怎", "？"] # 问题类
definition_word = ['简介','概述','功能']  # 定义类
step_word = ['步骤']   # 步骤类
list_word = ['条件','事项','场景','示例'] # 列表类

meaningless_title = ['概述','附录','修订记录','简介'] # 无意义的标题

class QAGeneration:

    def Analyze(self,title, kind = 3):
        """
        k = 1 时返回分词结果
        k = 2 时返回分词和词性标注的结果
        默认 k = 3 返回分词 词性标注 句法依存分析结果
        """
        # 分词
        segmentor = Segmentor()  # 初始化分词实例
        # segmentor.load(cws_model_path)  # 加载模型
        segmentor.load_with_lexicon(cws_model_path, 'ltp_data_v3.4.0/my_data.txt') # 加载模型，第二个参数是您的外部词典文件路径
        words = list(segmentor.segment(title))  # 分词
        # print(words)    # ['元芳', '你', '怎么', '看']
        segmentor.release()  # 释放模型

        if kind == 1:
            return words

        # 词性标注
        postagger = Postagger() # 初始化实例
        postagger.load(pos_model_path)  # 加载模型
        postags = list(postagger.postag(words))  # 词性标注
        # print(postags)  # ['nh', 'r', 'r', 'v']
        postagger.release()

        if kind == 2:
            return words, postagger

        # 依存句法分析
        parser = Parser() # 初始化实例
        parser.load(par_model_path)  # 加载模型
        arcs = parser.parse(words, postags)
        result = [(arc.head, arc.relation) for arc in arcs]
        parser.release()

        return words, postags, result

    def Ask_title(self, title, data):
        """
        针对title本身已是疑问句的，生成 QA 对
        title: 标题
        data: 包含标题等信息的字典
        return: QA_pair
        """
        QA_pair = []
        QA_flag = False

        question = title
        answer = ''
        content = data['title_content'].strip()
        # 如果有内容的话，答案就是内容
        if content:
            answer = content
            print("type1")
            QA_flag = True
        else:
            # 如果有副标题的话，用副标题作为答案
            if data["subtitle_nums"] > 0:
                # subtitle = self.Get_subtitles(data)
                for i in range(data["subtitle_nums"]):
                    answer += data["subcontent"][i]
                    print("type2")
                    QA_flag = True
            # 反之不能形成 QA 对
            else:
                print("type3")
                QA_flag = False

        if QA_flag:
            QA_pair.append(self.Save_qa(question, answer, data))



        return QA_pair

    def Normal_title(self, title, data):
        """
        针对title本身不是疑问句的，生成 QA 对
        """
        QA_pair = []
        VOB_flag = False # 动宾关系

        # 如果标题是前面列举的无意义词
        if len([i for i in meaningless_title if i in title])>0:

            question = data['subject'][0] + '的' + data['subject'][-2] + '是什么？'
            content = data['title_content'].strip()
            answer = ''
            # print(content)
            if content != "":
                answer = content
                print("type4")
                QA_pair.append(self.Save_qa(question, answer, data))
            else:
                if data["subtitle_nums"] > 0:
                    for i in range(data["subtitle_nums"]):
                        subtitle_list = self.Analyze(data["subtitle"][i], kind=1)
                        if len([i for i in subtitle_list if i in definition_word])>0:
                            answer += data["subcontent"][i]
                            print("type5")
                            QA_pair.append(self.Save_qa(question, answer, data))
                        elif len([i for i in subtitle_list if i in step_word])>0:
                            question = data['subject'][0] + '中如何' + data['subject'][-2] + '？'
                            answer += data["subcontent"][i]
                            print("type6")
                            QA_pair.append(self.Save_qa(question, answer, data))

                    # subtitle = self.Get_subtitles(data)
                    # for subt in subtitle.keys():
                    #    if data[subt.replace("title", "_content")] != "":
                    #       subtitle_list = self.Analyze(data[subt], kind=1)
                    #       # print(subtitle_list)
                    #       if len([i for i in subtitle_list if i in definition_word])>0:
                    #          answer = data[subt.replace("title", "_content")]
                    #          QA_pair.append(self.Save_qa(question, answer, data))
                    #       elif len([i for i in subtitle_list if i in step_word])>0:
                    #          question = data['subject'][0] + '中如何' + data['subject'][-2] + '？'
                    #          answer = data[subt.replace("title", "_content")]
                    #          QA_pair.append(self.Save_qa(question, answer, data))

        else:
            words, postags, result = self.Analyze(title)
            # print(words)
            # print(postags)
            # print(result)

            # 取主题词，并进行分词
            subject = data["subject"][0]
            subject_list = self.Analyze(subject, kind=1)
            # print(subject_list)

            # 检查是否存在动宾关系
            for arc in result:
                if arc[-1] == 'VOB':
                    VOB_flag = True
                    break

            # 如果 title 和 subject 存在共同词，则不需要拼接
            if len([i for i in subject_list  if i in words])>0:
                # print(words)
                # print(subject_list)
                # 如果有 VOB 在的话，采用如何提问
                if VOB_flag:
                    question = '如何'+title + '？'
                    content = data['title_content'].strip()
                    # 如果有内容的话，答案就是内容
                    if content != "":
                        answer = content
                        print("type7")
                        QA_pair.append(self.Save_qa(question, answer, data))
                    else:
                        # 如果有副标题的话，检查副标题
                        if data["subtitle_nums"] > 0:
                            for i in range(data["subtitle_nums"]):
                                subtitle_list = self.Analyze(data["subtitle"][i], kind=1)
                                if len([i for i in subtitle_list if i in step_word])>0:
                                    answer = data["subcontent"][i]
                                    print("type8")
                                    QA_pair.append(self.Save_qa(question, answer, data))
                                elif len([i for i in subtitle_list if i in definition_word])>0:
                                    question = title + '是什么？'
                                    answer = data["subcontent"][i]
                                    print("type9")
                                    QA_pair.append(self.Save_qa(question, answer, data))

                            # subtitle = self.Get_subtitles(data)
                            # for subt in subtitle.keys():
                            #    # 如果副标题内容不为空的话
                            #    if data[subt.replace("title", "_content")] != "":
                            #       subtitle_list = self.Analyze(data[subt], kind=1)
                            #       # 如果是表示操作的话，副标题下面的内容就是答案
                            #       if len([i for i in subtitle_list  if i in step_word])>0:
                            #          answer = data[subt.replace("title", "_content")]
                            #          QA_pair.append(self.Save_qa(question, answer, data))
                            #       # 如果是表示定义的词
                            #       elif len([i  for i in subtitle_list if i in definition_word])>0:
                            #          question = title + '是什么？'
                            #          answer = data[subt.replace("title", "_content")]
                            #          QA_pair.append(self.Save_qa(question, answer, data))

                # 如果没有 VOB 的话，名词型问句
                else:
                    question = title + '是什么？'
                    content = data['title_content'].strip()
                    if content != "":
                        answer = content
                        print("type10")
                        QA_pair.append(self.Save_qa(question, answer, data))

                    else:
                        if data["subtitle_nums"] > 0:
                            for i in range(data["subtitle_nums"]):
                                subtitle_list = self.Analyze(data["subtitle"][i], kind=1)
                                if len([i for i in subtitle_list if i in definition_word])>0:
                                    answer = data["subcontent"][i]
                                    print("type11")
                                    QA_pair.append(self.Save_qa(question, answer, data))
                                elif len([i for i in subtitle_list if i in step_word])>0:
                                    question = '如何' + title + '？'
                                    answer = data["subcontent"][i]
                                    print("type12")
                                    QA_pair.append(self.Save_qa(question, answer, data))

                        # subtitle = self.Get_subtitles(data)
                        # for subt in subtitle.keys():
                        #    if data[subt.replace("title", "_content")] != "":
                        #       subtitle_list = self.Analyze(data[subt], kind=1)
                        #       if len([i  for i in subtitle_list if i in definition_word])>0:
                        #          answer = data[subt.replace("title", "_content")]
                        #          QA_pair.append(self.Save_qa(question, answer, data))
                        #       elif len([i for i in subtitle_list if i in step_word ])>0:
                        #          question = '如何' + title + '？'
                        #          answer = data[subt.replace("title", "_content")]
                        #          QA_pair.append(self.Save_qa(question, answer, data))
            # 需要拼接
            else:
                # 如果有 VOB 在的话，采用如何提问
                # print(title)
                if VOB_flag:
                    question = subject + '中' + '如何' + title + '？'
                    # print(question)
                    content = data['title_content'].strip()
                    # 如果有内容的话，答案就是内容
                    if content != "":
                        answer = content
                        print("type13")
                        QA_pair.append(self.Save_qa(question, answer, data))
                    else:
                        # 如果有副标题的话，检查副标题
                        if data["subtitle_nums"] > 0:
                            for i in range(data["subtitle_nums"]):
                                subtitle_list = self.Analyze(data["subtitle"][i], kind=1)
                                if len([i for i in subtitle_list if i in step_word])>0:
                                    answer = data["subcontent"][i]
                                    print("type14")
                                    QA_pair.append(self.Save_qa(question, answer, data))
                                elif len([i for i in subtitle_list if i in definition_word])>0:
                                    question = subject + '的' + title + '是什么？'
                                    answer = data["subcontent"][i]
                                    print("type15")
                                    QA_pair.append(self.Save_qa(question, answer, data))

                        # if data["subtitle_numbers"] > 0:
                        #    subtitle = self.Get_subtitles(data)
                        #    for subt in subtitle.keys():
                        #       # 如果副标题内容不为空的话
                        #       if data[subt.replace("title", "_content")] != "":
                        #          subtitle_list = self.Analyze(data[subt], kind=1)
                        #          # 如果是表示操作的话，副标题下面的内容就是答案
                        #          if len([i for i in subtitle_list if i in step_word])>0:
                        #             answer = data[subt.replace("title", "_content")]
                        #             QA_pair.append(self.Save_qa(question, answer, data))
                        #          # 如果是表示定义的词
                        #          elif len([i for i in subtitle_list if i in definition_word ])>0:
                        #             question = subject + '的' + title + '是什么？'
                        #             answer = data[subt.replace("title", "_content")]
                        #             QA_pair.append(self.Save_qa(question, answer, data))

                # 如果没有 VOB 的话，名词型问句
                else:
                    question = subject + '的' + title + '是什么？'
                    content = data['title_content'].strip()
                    if content != "":
                        answer = content
                        print("type16")
                        QA_pair.append(self.Save_qa(question, answer, data))

                    else:
                        if data["subtitle_nums"] > 0:
                            for i in range(data["subtitle_nums"]):
                                subtitle_list = self.Analyze(data["subtitle"][i], kind=1)
                                if len([i for i in subtitle_list if i in definition_word])>0:
                                    answer = data["subcontent"][i]
                                    print("type17")
                                    QA_pair.append(self.Save_qa(question, answer, data))
                                elif len([i for i in subtitle_list if i in step_word])>0:
                                    question = subject + '中' + '如何' + title + '？'
                                    answer = data["subcontent"][i]
                                    print("type18")
                                    QA_pair.append(self.Save_qa(question, answer, data))

                        # if data["subtitle_numbers"] > 0:
                        #    subtitle = self.Get_subtitles(data)
                        #    for subt in subtitle.keys():
                        #       if data[subt.replace("title", "_content")] != "":
                        #          subtitle_list = self.Analyze(data[subt], kind=1)
                        #          if len([i for i in subtitle_list if i in definition_word ])>0:
                        #             answer = data[subt.replace("title", "_content")]
                        #             QA_pair.append(self.Save_qa(question, answer, data))
                        #          elif len([i  for i in subtitle_list if i in step_word])>0:
                        #             question = subject + '中' + '如何' + title + '？'
                        #             answer = data[subt.replace("title", "_content")]
                        #             QA_pair.append(self.Save_qa(question, answer, data))
        return QA_pair

    def Normal_subtitle(self, title, data):
        """
        针对 subtitle 来生成 QA 对
        """
        QA_pair = []

        title_list = self.Analyze(title, kind=1)
        subject = data["subject"][0]

        # 如果大标题是无意义的词
        if len([i for i in meaningless_title if i in title])>0:
            if data["subtitle_nums"] > 0:
                # subtitle = self.Get_subtitles(data)
                # for subt in subtitle.keys():
                for i in range(data["subtitle_nums"]):
                    VOB_flag = False # 动宾关系
                    # content = data[subt.replace("title", "_content")]
                    content = data["subcontent"][i]
                    subtitle = data["subtitle"][i]
                    if content != "":
                        # 小标题本身是问句的
                        if self.is_Ask_title(subtitle):
                            question = subtitle
                            answer = content
                            print("type19")
                            QA_pair.append(self.Save_qa(question, answer, data))

                        # 本身不是疑问句的话
                        else:
                            words, postags, result = self.Analyze(subtitle)
                            # 检查是否有动宾关系在其中
                            for arc in result:
                                if arc[-1] == 'VOB':
                                    VOB_flag = True
                                    break
                            # 动词型
                            if VOB_flag:
                                # 如果存在重复的话，不需要拼接
                                if len([i for i in title_list if i in words])>0:
                                    question =  subject + "中如何" + subtitle + "？"
                                    answer = content
                                    # 如果是列表词的话
                                    if len([i for i in words if i in list_word])>0:
                                        question = subject + "中有哪些" + subtitle + "？"
                                    print("type20")
                                    QA_pair.append(self.Save_qa(question, answer, data))
                                # 不存在重复，且标题为无意义词
                                else:
                                    question = subject + '中' + data['subject'][-2] + '如何' + subtitle + '？'
                                    answer = content
                                    if len([i for i in words if i in list_word])>0:
                                        question = subject + '中' + data['subject'][-2] + '有哪些' + subtitle + '？'
                                    print("type21")
                                    QA_pair.append(self.Save_qa(question, answer, data))
                            # 名词型
                            else:
                                if len([i for i in title_list if i in words])>0:
                                    question =  subject + "中" + subtitle + "是什么？"
                                    answer = content
                                    if len([i for i in words if i in list_word])>0:
                                        question = subject + "中有哪些" + subtitle+ "？"
                                    print("type22")
                                    QA_pair.append(self.Save_qa(question, answer, data))
                                else:
                                    question = subject + '中' + data['subject'][-2] + '的' + subtitle + '是什么？'
                                    answer = content
                                    if len([i for i in words if i in list_word])>0:
                                        question = subject + '中' + data['subject'][-2] + '有哪些' + subtitle + '？'
                                    print("type23")
                                    QA_pair.append(self.Save_qa(question, answer, data))

        # 大标题是有意义的
        else:
            if data["subtitle_nums"] > 0:
                # subtitle = self.Get_subtitles(data)
                # for subt in subtitle.keys():
                for i in range(data["subtitle_nums"]):
                    VOB_flag = False # 动宾关系
                    content = data["subcontent"][i]
                    subtitle = data["subtitle"][i]
                    if content != "":
                        if self.is_Ask_title(subtitle):
                            question = subtitle
                            answer = content
                            print("type24")
                            QA_pair.append(self.Save_qa(question, answer, data))
                        else:
                            words, postags, result = self.Analyze(subtitle)
                            # 检查是否有动宾关系在其中
                            for arc in result:
                                if arc[-1] == 'VOB':
                                    VOB_flag = True
                                    break
                            # 动词型
                            if VOB_flag:
                                if len([i for i in title_list if i in words])>0:
                                    question =  subject + "中如何" + subtitle + "？"
                                    answer = content
                                    # 如果是列表词的话
                                    if len([i for i in words if i in list_word])>0:
                                        question = subject + "中有哪些" + subtitle + "？"
                                    print("type25")
                                    QA_pair.append(self.Save_qa(question, answer, data))
                                else:
                                    question = subject + '的' + title + '中如何' + subtitle + '？'
                                    answer = content
                                    if len([i for i in words if i in list_word])>0:
                                        question = subject + '的' + title + '中有哪些' + subtitle + '？'
                                    print("type26")
                                    QA_pair.append(self.Save_qa(question, answer, data))
                            # 名词型
                            else:
                                if len([i for i in title_list if i in words])>0:
                                    question =  subject + "中" + subtitle + "是什么？"
                                    answer = content
                                    if len([i for i in words if i in list_word])>0:
                                        question = subject + "中有哪些" + subtitle+ "？"
                                    print("type27")
                                    QA_pair.append(self.Save_qa(question, answer, data))
                                else:
                                    question = subject + '的' + title + '中' + subtitle + '是什么？'
                                    answer = content
                                    if len([i for i in words if i in list_word])>0:
                                        question = subject + '的' + title + '有哪些' + subtitle + '？'

                                    print("type28")
                                    QA_pair.append(self.Save_qa(question, answer, data))
        return QA_pair

    def Save_qa(self,question, answer, data):
        """
        return : {'question':question,
                 'answer': answer,
                 'link': data['link'],
                 'subject': data['subject'][0]}
        """
        QA_data = {}

        QA_data['question'] = self.question_finetune(question)
        QA_data['answer'] = self.answer_finetune(answer)
        if 'link' in data.keys() and data['link'] != '':
            QA_data['link'] = data['link']
        else:
            QA_data['link'] = ''
        if 'subject' in data.keys() and (len(data['subject']) > 0):
            QA_data['subject'] = data['subject'][0]
        else:
            QA_data['subject'] = ''

        return QA_data


    def question_finetune(self,question):
        """
        为疑问句补上标点符号
        """
        question = question.strip()
        # 判断问句的最后一位的标点
        if question[-1] in ['，', '。', '；']:  # 说明句子的最后一位是有标点的，但不是问号
            question = question[:-1] + '？'
        elif question[-1] not in ['，', '。', '？', '；', '！']:  # 句子最后没有标点结尾的
            question = question + '?'
        print(question)
        return question


    def answer_finetune(self,answer):
        """
        为陈述句补上标点符号
        """
        answer = answer.strip()
        # 判断问句的最后一位的标点
        if answer[-1] in ['，', '？', '；']:  # 说明句子的最后一位是有标点的，但不是句号
            answer = answer[:-1] + '。'
        elif answer[-1] not in ['，', '。', '？', '；', '！']:  # 句子最后没有标点结尾的
            answer = answer + '。'
        return answer

        # def Get_subtitles(self, data):
    #    """
    #    return: {"subtitle1":subtitle}
    #    """
    #    subtitle = {}
    #    for i in range(data["subtitle_numbers"]):
    #       key = "subtitle{}".format(i+1)
    #       subtitle[key] = data[key]
    #    return subtitle

    def is_Ask_title(self, title):
        """
        判断是否是疑问句的标题
        """
        result = False
        for i in ask_word:
            if i in title:
                result = True
        return result

    def run(self, parse_data, save_path=None):
        '''
        QA对生成算法
        :param parse_data: 经过解析的数据
        :param save_path: 填写则保存数据
        :return: 生成好的QA对
        '''
        QA_pairs = []

        for data in parse_data:
            title = data["title"].strip()
            if title == "":
                # 如果没能获取到 title，选取主题词第一个作为 title
                title = data["subject"][0]

            # 如果title本身就是疑问句的话
            if self.is_Ask_title(title):
                QA_pairs.extend(self.Ask_title(title, data))
            # 如果本身不是疑问句的话,也就是正常的 title
            else:
                QA_pairs.extend(self.Normal_title(title, data))
                QA_pairs.extend(self.Normal_subtitle(title, data))
        # 保存
        if save_path:
            json_str = json.dumps(QA_pairs, ensure_ascii=False, indent=2)
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(json_str)
        return QA_pairs


if __name__ == "__main__":
    s = QAGeneration()
    s.run('../spider/cc_contents.json')



## 测试代码
#    data = {
#     "title": "与其他云服务的关系",
#     "title_content": "云解析服务支持将注册的域名托管到华为云的云解析服务，并为该域名提供域名解析服务。具体操作请参考《云解析服务帮助中心》。",
#     "url": "https://support.huaweicloud.com/productdesc-domain/zh-cn_topic_0122928885.html",
#     "subject": [
#       "域名注册",
#       "产品介绍",
#       "与其他云服务的关系"
#     ],
#     "subtitle_numbers": 0
#   }
#    t = "与其他云服务的关系"
#    print(s.Normal_title(t, data))

# with open("../spider/cc_contents.json", 'r') as f:
#          datas = json.load(f)

#       QA_pairs = []

#       for data in datas:
#          title = data["title"].strip()
#          if title == "":
#             # 如果没能获取到 title，选取主题词第一个作为 title
#             title = data["subject"][0]

#          # 如果title本身就是疑问句的话   
#          if self.is_Ask_title(title):
#             QA_pairs.extend(self.Ask_title(title, data))
#          # 如果本身不是疑问句的话,也就是正常的 title
#          else:
#             QA_pairs.extend(self.Normal_title(title, data))
#             QA_pairs.extend(self.Normal_subtitle(title, data))

#       with open("QA_pairs_compute.json", "w", encoding = "utf-8") as f:
#          f.write(json.dumps(QA_pairs, ensure_ascii=False, indent=2))