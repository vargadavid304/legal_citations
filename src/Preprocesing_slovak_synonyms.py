import json

# Cesta k súboru JSON
file_path = 'D:\\downloads\\paragraf_texts\\paragraf_texts.json'

# Získanie dát zo súboru
with open(file_path, 'r', encoding='utf-8') as file:
    json_data = json.load(file)

# Vytvorenie nového zoznamu pre uchovávanie jednotlivých dokumentov
result_documents = []

# Cyklus pre spracovanie každého JSON objektu
for data in json_data:
    # Cyklus pre spracovanie každej "version" v poli "versions"
    for version in data["versions"]:
        # Vytvorenie samostatného dokumentu pre každú "version"
        document = {"_ident": data["_id"], "versions": [version]}
        result_documents.append(document)

# Výpis výsledku
for result_document in result_documents:
    #print(json.dumps(result_document, indent=2, ensure_ascii=False))
    print("\n")

from elasticsearch import Elasticsearch

# Функція для конвертації синонімів з формату SOLR в формат Elasticsearch
def convert_synonyms(input_file_path, output_file_path):
    with open(input_file_path, 'r', encoding='utf-8') as input_file:
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            for line in input_file:
                synonyms = line.strip().split(',')
                for synonym in synonyms[1:]:
                    output_file.write(f"{synonyms[0]} => {synonym}\n")

# Шляхи до файлів синонімів для введення та виведення
input_synonyms_file = 'slovak_synonyms.txt'
output_synonyms_file = 'output_synonyms.txt'

# Виклик функції для конвертації синонімів
convert_synonyms(input_synonyms_file, output_synonyms_file)

# Підключення до серверу Elasticsearch (змініть URL на свій)
es = Elasticsearch('http://localhost:9200')

# Зчитування списку зупинених слів
stopwords_file_path = "slovak_stopwords.txt"
with open(stopwords_file_path, "r", encoding="utf-8") as file:
    stopwords_list = [word.strip() for word in file.readlines()]

# Зчитування синонімів
synonyms_file_path = "slovak_synonyms.txt"
with open(synonyms_file_path, "r", encoding="utf-8") as file:
    synonyms_content = [word.strip() for word in file.readlines()]

# Налаштування аналізатора та фільтрів для Elasticsearch
mapping = {
    "settings": {
    "analysis": {
      "filter": {
        "sk_SK" : {
          "type" : "hunspell",
          "locale" : "sk_SK",
          "dedup" : True,
          "recursion_level" : 0
        },
        "synonym_filter": {
          "type": "synonym",
          "synonyms_path": "output_synonyms.txt",
          "ignore_case": True
        },
        "stopwords_SK": {
          "type": "stop",
          "stopwords_path": "stop-words/stop-words-slovak.txt",
          "ignore_case": True
        }
      },
      "analyzer": {
        "slovencina_synonym": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": [
            "stopwords_SK",
            "lowercase",
            "stopwords_SK",
            "synonym_filter",
            "asciifolding"
          ]
        },
        "slovencina": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": [
            "stopwords_SK",
            "lowercase",
            "stopwords_SK"
          ]
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
                            "title": {"type": "text", "analyzer": "slovencina_synonym"}
                        }
                    },
                    "text": {"type": "text", "analyzer": "slovencina_synonym"}
                }
            }
        }
    }
}

# Názov indexu, kde chcete ukladať dáta
index_name = 'prefinal_index_slovak_synonyms_5_shards'

# Vytvorenie indexu Elasticsearch, ak neexistuje
if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name, body=mapping)

identifikaator_es = 1
for result_document in result_documents:
    print(json.dumps(result_document, indent=2, ensure_ascii=False))
    identifikaator_es += 1
    es.index(index=index_name, body=result_document, id=identifikaator_es)

# Zmiany sa uloží
es.indices.refresh(index=index_name)
