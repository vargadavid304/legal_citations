mapping = {
    "settings": {
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
                    "version": {"type": "Integer"},
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
