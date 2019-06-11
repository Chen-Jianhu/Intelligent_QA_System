import elasticsearch
from elasticsearch import Elasticsearch
import json


class QASearch(object):
    def __init__(self, index):
        self.es = Elasticsearch()
        self.index = index
        self.mapping = {
            'properties': {
                'question': {
                    'type': 'text',
                    'analyzer': 'ik_max_word',
                    'search_analyzer': 'ik_max_word'
                }
            }
        }
        # self.es.indices.delete(index= self.index, ignore=[400, 404])
        # self.es.indices.create(index= self.index, ignore=400)
        self.es.indices.put_mapping(index=self.index, body=self.mapping)

    def insert_from_file(self, filepath):
        with open(filepath, 'r') as f:
            datas = json.load(f)
        for data in datas:
            self.es.index(index=self.index, body=data)

    def insert_one_data(self, data):
        self.es.index(index=self.index, body=data)

    def delete_one_data(self, id):
        self.es.delete(index=self.index, id=id)

    def update_one_date(self, new_data, id):
        self.es.update(index=self.index, body=new_data, id=id)

    def search_data(self, content):
        dsl = {'query': {'match': {'question': content}}}
        result = self.es.search(index=self.index, body=dsl)
        # print(result)
        # ans = json.dumps(result, indent=2, ensure_ascii=False)
        return result["hits"]["hits"][0]['_source']['answer'], result["hits"][
            "hits"][0]['_source']['link']

    def get_all_data(self):
        query_json = {"match": {"_index": "qa_pairs"}}
        # 遍历所有的查询条件
        queryData = self.es.search(index=self.index,
                                   scroll='5m',
                                   timeout='3s',
                                   size=100,
                                   body={"query": query_json})
        all_datas = queryData.get("hits").get("hits")
        scroll_id = queryData["_scroll_id"]
        total = queryData["hits"]["total"]["value"]
        # print(queryData)
        for i in range(int(total / 100)):
            # scroll参数必须指定否则会报错
            res = self.es.scroll(scroll_id=scroll_id, scroll='5m') 
            all_datas += res["hits"]["hits"]
        return all_datas

if __name__ == "__main__":
    es = QASearch(index="qa_pairs")
    # es.insert_from_file('./QA_pairs_compute.json')
    while True:
        try:
            question = input("输入问题:")
            result, url = es.search_data(question)
            print("答案为:\n", result)
            print("url:\n", url)
        except elasticsearch.exceptions.NotFoundError:
            print("Not Found!")
    # ds = es.get_all_data()
    # print(ds[0])
    # print(len(ds))
# es = Elasticsearch()
# mapping = {
#     'properties': {
#         'question': {
#             'type': 'text',
#             'analyzer': 'ik_max_word',
#             'search_analyzer': 'ik_max_word'
#         }
#     }
# }

# es.indices.delete(index='qa_pairs', ignore=[400, 404])
# es.indices.create(index='qa_pairs', ignore=400)
# es.indices.put_mapping(index='qa_pairs', body=mapping)

# with open('QA_pairs.json', 'r') as f:
#     datas = json.load(f)

# for data in datas:
#     es.index(index='qa_pairs', body=data)

# dsl = {
#     'query': {
#         'match': {
#             'question': '简介'
#         }
#     }
# }
# result = es.search(index='qa_pairs', body=dsl)
# print(json.dumps(result, indent=2, ensure_ascii=False))