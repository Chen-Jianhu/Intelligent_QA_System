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
        self.es.indices.create(index=self.index, ignore=400)
        # if self.es.indices.exists(index = self.index) is not True:
        #     self.es.indices.create(index = self.index, ignore = 400)
        self.es.indices.put_mapping(index=self.index, body=self.mapping)

    def insert_from_mem(self, datas):
        '''
        使用QA生成算法传过来的datas插入es
        :param datas: QA生成算法生成的数据
        :return: 插入是否成功
        '''
        try:
            for data in datas:
                self.es.index(index=self.index, body=data)
            return True
        except:
            return False

    def insert_from_file(self, file_path):
        with open(file_path, 'r') as f:
            datas = json.load(f)
        for data in datas:
            self.es.index(index=self.index, body=data)

    def insert_one_data(self, data):
        try:
            self.es.index(index=self.index, body=data)
            return True
        except:
            return False

    def delete_one_data(self, id):
        """
        根据 id 删除数据
        """
        try:
            self.es.delete(index=self.index, id = id)
            return True
        except:
            return False

    def update_one_date(self, new_data, id):
        """
        根据 id 和 new_data 更新数据
        """
        self.es.update(index=self.index, body=new_data, id = id)

    def search_data(self, content):
        """
        正确搜索到 返回 最佳答案 和 url
        没搜索到 返回 -1
        后续可改为根据 score 值选择返回答案还是-1
        """
        dsl = {'query': {'match': {'question': content}}}
        try:
            result = self.es.search(index=self.index, body=dsl)
            # print(result)
            # ans = json.dumps(result, indent=2, ensure_ascii=False)
            # print(ans)
            return result["hits"]["hits"][0]['_source']['answer'], result["hits"][
                "hits"][0]['_source']['link']
        except:
            print("ES Not Found!")
            return -1
    
    def search_datas_by_question(self, content):
        """
        正确搜索到 返回 hits
        没搜索到  返回 -1
        """
        dsl = {'query': {'match': {'question': content}}}
        try:
            result = self.es.search(index=self.index, body=dsl)
            # ans = json.dumps(result, indent=2, ensure_ascii=False)
            # print(result)
            return result["hits"]["hits"]
        except:
            return []
   
    def search_datas_by_answer(self, content):
        """
        正确搜索到 返回 hits
        没搜索到  返回 -1
        """
        dsl = {'query': {'match': {'answer': content}}}
        try:
            result = self.es.search(index=self.index, body=dsl)
            return result["hits"]["hits"]
        except:
            return []
        
    def get_all_data(self):
        query_json = {"match": {"_index": self.index}}
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


if __name__ == '__main__':
    Q = QASearch(index='qa_pairs')
    # Q.es.indices.delete(index=Q.index)
    Q.insert_from_file('./QA_pairs_compute.json')