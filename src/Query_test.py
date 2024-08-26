import json
import string
from nltk import ngrams
from nltk.tokenize import word_tokenize
from elasticsearch import Elasticsearch

es = Elasticsearch('http://localhost:9200')

search_text = ""

file_path = "D:\\downloads\\rozhodnutia\\chunk_40.json"

with open(file_path, 'r', encoding='utf-8') as file:
    json_data = json.load(file)

result_documents = []

for data_element in json_data:
    result_documents.append(data_element['dokument_fulltext'])

i = 0
for result_document in result_documents:
    search_text = json.dumps(result_document, indent=2, ensure_ascii=False)
    i = i + 1
    if i == 86:
        break
print(search_text)

query = {
    "query": {
    "bool": {
      "filter": [
        {
          "nested": {
            "path": "versions",
            "query": {
              "range": {
                "versions.version": {
                  "lt": "20161006"
                }
              }
            }
          }
        }
      ],
      "must": [
        {
          "nested": {
            "path": "versions",
            "query": {
              "match": {
                "versions.text": search_text
              }
            }
          }
        }
      ]
    }
  },
  "collapse": {
    "field": "_ident",
    "inner_hits": {
      "name": "latest_version",
      "size": 1,
      "sort": [
        {
          "versions.version": {
            "order": "desc",
            "nested": {
              "path": "versions"
            }
          }
        }
      ]
    }
  }
}

result = es.search(index='prefinal_index', body=query)

arr_zakony = []
for hit in result['hits']['hits']:
    arr_zakony.append(hit)

arr_zakony_text = []
arr_id = []
arr_version = []

#text zakonov
for i in arr_zakony:
    print(i)
    for j in i['_source']['versions']:
        arr_zakony_text.append(j['text'])
        arr_id.append(i['_source']['_ident'])
        arr_version.append(j['version'])

print(arr_id)
print(arr_version)