import json

from elasticsearch import Elasticsearch

# Načítanie knižnice JSON
import json

# Cesta k súboru JSON
file_path = 'D:\\downloads\\paragraf_texts\\paragraf_texts.json'

# Získanie dát zo súboru
with open(file_path, 'r', encoding='utf-8') as file:
    json_data = json.load(file)

# Vytvorenie nového zoznamu na uchovávanie jednotlivých dokumentov
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

# Import knižnice Elasticsearch
from elasticsearch import Elasticsearch

# Adresa servera Elasticsearch (zmeňte URL podľa svojich potrieb)
es = Elasticsearch('http://localhost:9200')

# Nastavenie mapovania pre index Elasticsearch
mapping = {
    "settings": {
        "number_of_shards": 8,
        "analysis": {
            "analyzer": {
                "my_standard_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "asciifolding"]
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
                            "title": {"type": "text", "analyzer": "my_standard_analyzer"}
                        }
                    },
                    "text": {"type": "text", "analyzer": "my_standard_analyzer"}
                }
            }
        }
    }
}

# Názov indexu, kde chcete ukladať dáta
index_name = 'prefinal_index_standard_8_shards'

# Vytvorenie indexu Elasticsearch, ak neexistuje
if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name, body=mapping)

# Uloženie zmien
es.indices.refresh(index=index_name)
