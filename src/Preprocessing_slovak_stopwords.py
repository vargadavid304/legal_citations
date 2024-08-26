import json

file_path = 'D:\\downloads\\paragraf_texts\\paragraf_texts.json'

# Зчитування даних з файлу
with open(file_path, 'r', encoding='utf-8') as file:
    json_data = json.load(file)

# Створіть новий список для зберігання окремих документів
result_documents = []

# Цикл для обробки кожного JSON-об'єкта
for data in json_data:
    # Цикл для обробки кожного "version" у полі "versions"
    for version in data["versions"]:
        # Створення окремого документу для кожного "version"
        document = {"_ident": data["_id"], "versions": [version]}
        result_documents.append(document)

# Вивести результат
for result_document in result_documents:
    #print(json.dumps(result_document, indent=2, ensure_ascii=False))
    print("\n")

from elasticsearch import Elasticsearch



# Підключення до серверу Elasticsearch (змініть URL на свій)
es = Elasticsearch('http://localhost:9200')

stopwords_file_path = "slovak_stopwords.txt"

with open(stopwords_file_path, "r", encoding="utf-8") as file:
    stopwords_list = [word.strip() for word in file.readlines()]

mapping = {
    "settings": {
        "analysis": {
            "filter": {
                "sk_stop": {
                    "type": "stop",
                    "stopwords": stopwords_list
                },
            },
            "analyzer": {
                "sk_SK": {
                    "tokenizer":  "standard",
                    "filter":   ["lowercase", "sk_stop"]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "_ident": {"type": "keyword"},
            "versions": {
                "type": "nested",
                "properties": {
                    "version": {"type": "integer"},
                    "headlines": {
                        "type": "nested",
                        "properties": {
                            "paragraf_id": {"type": "keyword"},
                            "title": {"type": "text", "analyzer": "sk_SK"}
                        }
                    },
                    "text": {"type": "text", "analyzer": "sk_SK"}
                }
            }
        }
    }
}



# The index where you want to store the data
index_name = 'prefinal_index_slovak_5_shards'

if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name, body=mapping)

identifikaator_es = 1
for result_document in result_documents:
    print(json.dumps(result_document, indent=2, ensure_ascii=False))
    identifikaator_es += 1
    es.index(index=index_name, body=result_document, id = identifikaator_es)

# Збереження змін
es.indices.refresh(index=index_name)