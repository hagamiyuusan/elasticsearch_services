from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import os
import glob
import tqdm
import json


class ElasticSearch():
    def __init__(self, host : str = "localhost", port : int = 9200) -> None:
        self.client = Elasticsearch([{'host': host, 'port': port, 'scheme': 'http'}])

    def add_ocr(self, data_path, index_name):
        if self.client.exists(index=index_name):
            pass
        else:
            self.client.indices.create(index=index_name)
        log_file = open('log.txt','w')
        ocr_file = sorted(glob.glob(os.path.join(data_path, '*.json')))
        id = 0
        for file in tqdm.tqdm(ocr_file):
            with open(file, 'r') as json_file:
                data = json.load(json_file)
            video_id = os.path.basename(file).split('.')[0]
            for frame_id, label in data.items():
                try:
                    ann = {
                        'id': id,
                        "frame": os.path.join(video_id,frame_id),
                        "ocr_text": label[0]['description']
                    }
                    self.client.index(index = index_name, id = id, document = ann)
                except:
                    log_file.write(f'{file}: {frame_id}\n')
                id+=1

    
    def search(self, index_name, query: str, topk: int) -> list:
        #'https://coralogix.com/blog/42-elasticsearch-query-examples-hands-on-tutorial/'
        #'Các chiến lược ở đây, nếu cần gì thì tìm thử'
        search_query = {
                "size": topk,  # Số lượng kết quả bạn muốn lấy
                "query": {
                    "match": {
                        "ocr_text": query  # Truy vấn tìm kiếm trong trường "ocr_text"
                    }
                }
            }
        search_results = self.client.search(index = index_name,body = search_query)
        hits = search_results['hits']['hits']
        results = [hit['frame'] for hit in hits]
        return results
    
    def delete_index(self, index_name):
        if self.client.indices.exists(index=index_name):
            self.client.indices.delete(index=index_name)



                    
                    




