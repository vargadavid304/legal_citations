import Levenshtein
import json
from elasticsearch import Elasticsearch
import time
import string
from nltk import ngrams
from nltk.tokenize import word_tokenize
import nltk

def remove_punctuation_and_make_3_grams(text1):
    #nltk.download('punkt')

    def remove_punctuation_and_short_words(text):
        translator = str.maketrans('', '', string.punctuation)
        text_without_punct = text.translate(translator)
        text_without_digits = ''.join(char for char in text_without_punct if not char.isdigit())

        words = text_without_digits.split()
        filtered_words = [word for word in words if len(word) >= 3]
        return ' '.join(filtered_words)

    def generate_word_ngrams(text, n):
        words = word_tokenize(text)
        word_3grams = list(ngrams(words, n))
        word_3grams_combined = [' '.join(gram) for gram in word_3grams]
        return word_3grams_combined

    cleaned_text = remove_punctuation_and_short_words(text1)

    word_3grams_combined = generate_word_ngrams(cleaned_text, 3)
    return word_3grams_combined



def find_quotes(text1, text2, threshold=0.9):
    sentences_text1 = remove_punctuation_and_make_3_grams(text1)
    sentences_text2 = remove_punctuation_and_make_3_grams(text2)
    found_quotes = []

    for idx1, sentence1 in enumerate(sentences_text1):
        for idx2, sentence2 in enumerate(sentences_text2):
            distance_ratio = Levenshtein.ratio(sentence1, sentence2)

            if distance_ratio > threshold:
                found_quotes.append((idx1, idx2))

    return found_quotes

def is_sequence(arr):
    return all(arr[i] == arr[i-1] + 1 for i in range(1, len(arr)))

def find_sequences(array1, array2):
    print("##############################################################")
    print(array1)
    print(array2)
    sequences_rozhodnutia = []
    current_sequence_rozhodnutia = []
    sequences_zakony = []
    current_sequence_zakony = []
    first = True
    for element1, element2 in zip(array1, array2):
        if first == True:
            current_sequence_rozhodnutia = [element1]
            current_sequence_zakony = [element2]
            first = False
        if ((not current_sequence_rozhodnutia or element1 == current_sequence_rozhodnutia[-1] + 1) or element1 == current_sequence_rozhodnutia[-1]) or ((not current_sequence_zakony or element1 == current_sequence_zakony[-1] + 1) or element1 == current_sequence_zakony[-1]):
            if element1 == current_sequence_rozhodnutia[-1] + 1 and element2 == current_sequence_zakony[-1] + 1:
                current_sequence_rozhodnutia.append(element1)
                current_sequence_zakony.append(element2)
            else:
                continue
        else:
            if (len(current_sequence_rozhodnutia) > 1 and is_sequence(current_sequence_rozhodnutia)) and (len(current_sequence_zakony) > 1 and is_sequence(current_sequence_zakony)):
                sequences_rozhodnutia.append(current_sequence_rozhodnutia)
                sequences_zakony.append(current_sequence_zakony)
            current_sequence_rozhodnutia = [element1]
            current_sequence_zakony = [element2]

    print(sequences_rozhodnutia)
    print(sequences_zakony)
    print("################################################################")
    return sequences_rozhodnutia, sequences_zakony


def filter_sequences(rozhodnutie, zakon):
    najdlhsie_podpostupnost_rozhodnutia = []
    najdlhsie_podpostupnost_zakony = []
    kalka_rozhodnutie = []
    kalka_zakony = []


    if len(rozhodnutie) > 1:
        najdlhsie_podpostupnost_rozhodnutia = rozhodnutie[0]
        najdlhsie_podpostupnost_zakony = zakon[0]
        for i in range(len(rozhodnutie) - 1):
            if (((abs(rozhodnutie[i + 1][0] - rozhodnutie[i][-1]) <= 10) and
                 (rozhodnutie[i][-1] < rozhodnutie[i + 1][0])) and
                    ((abs(zakon[i][-1] - zakon[i + 1][0]) <= 10) and
                     (zakon[i][-1] < zakon[i + 1][0]))):
                najdlhsie_podpostupnost_rozhodnutia.extend(rozhodnutie[i + 1])
                najdlhsie_podpostupnost_zakony.extend(zakon[i + 1])
            else:
                kalka_rozhodnutie.append(najdlhsie_podpostupnost_rozhodnutia)
                kalka_zakony.append(najdlhsie_podpostupnost_zakony)
                najdlhsie_podpostupnost_rozhodnutia = rozhodnutie[i + 1]
                najdlhsie_podpostupnost_zakony = zakon[i + 1]


        if najdlhsie_podpostupnost_rozhodnutia:
            kalka_rozhodnutie.append(najdlhsie_podpostupnost_rozhodnutia)
            kalka_zakony.append(najdlhsie_podpostupnost_zakony)
    else:
        return 0

    nested_arrays = kalka_rozhodnutie, kalka_zakony
    nested_lengths = [len(subarray) for array in nested_arrays for subarray in array]
    #print(kalka_rozhodnutie, kalka_zakony)
    if nested_lengths != []:
        max_length = max(nested_lengths)
    else:
        return None
    return max_length

def convert_to_integer(date_string):
    # Удаляем символы, которые не являются цифрами или буквами
    cleaned_string = ''.join(c for c in date_string if c.isdigit())

    # Извлекаем нужные нам цифры для даты (год, месяц, день)
    year = cleaned_string[:4]
    month = cleaned_string[4:6]
    day = cleaned_string[6:8]

    # Собираем строку и преобразуем её в целое число
    result = int(year + month + day)
    return result

def find_max_position(arr):
    if not arr:
        return None

    max_index = 0
    bolo = False
    for i in range(1, len(arr)):
        if arr[i] > arr[i-1]:
            max_index = i
            bolo = True
    if bolo is False and arr[max_index] == 0:
        return None

    return max_index

def get_laws_for_judge_decision(es = Elasticsearch('http://localhost:9200')):
    search_text = ""
    date_decision = ""

    file_path = "D:\\downloads\\rozhodnutia\\chunk_40.json"

    with open(file_path, 'r', encoding='utf-8') as file:
        json_data = json.load(file)

    decisions_text = []
    date_decisions = []

    for data_element in json_data:
        decisions_text.append(data_element['dokument_fulltext'])
        date_decisions.append(data_element['datum_vydania_rozhodnutia'])

    counter_text = 0
    for text in decisions_text:
        search_text = json.dumps(text, indent=2, ensure_ascii=False)
        if counter_text == 70:
            break
        counter_text = counter_text + 1



    counter_date = 0
    for j in date_decisions:
        date_decision = j
        if counter_date == 70:
            break
        counter_date = counter_date + 1


    date_decision = convert_to_integer(date_decision)

    print(search_text)
    print(date_decision)

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
                                        "lt": date_decision
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
        },
        "size": 30
    }

    result = es.search(index='prefinal_index', body=query)

    arr_zakony = []
    for hit in result['hits']['hits']:
        arr_zakony.append(hit)

    arr_zakony_text = []
    arr_id = []
    arr_version = []

    for i in arr_zakony:
        for j in i['_source']['versions']:
            arr_zakony_text.append(j['text'])
            arr_id.append(i['_source']['_ident'])
            arr_version.append(j['version'])
    return arr_zakony_text, search_text, arr_id, arr_version
def find_best_citation():
    arr_zakony_text, search_text, arr_id, arr_version = get_laws_for_judge_decision()
    print(remove_punctuation_and_make_3_grams(search_text))
    print(arr_id)
    print(arr_version)
    list_best_citations = []
    for zakon in arr_zakony_text:
        quotes = find_quotes(search_text, zakon)

        pole_indexov_rozhodnutia = []
        pole_indexov_zakony = []
        pole_indexov_zakony_text = []
        pole_indexov_rozhodnutia_text = []

        for quote in quotes:
            pole_indexov_rozhodnutia.append(quote[0])
            pole_indexov_zakony.append(quote[1])
        sequences_rozhodnutia, sequences_zakony = find_sequences(pole_indexov_rozhodnutia, pole_indexov_zakony)
        #print("Najdlhsia citacia v tomto zakone sa sklada z: ", filter_sequences(sequences_rozhodnutia, sequences_zakony), " viet")
        list_best_citations.append(filter_sequences(sequences_rozhodnutia, sequences_zakony))

    print(list_best_citations)
    max_pos = find_max_position(list_best_citations)
    if max_pos != None:
        id = arr_id[max_pos]
        version = arr_version[max_pos]
    else:
        id = None
        version = None

    return ("Pre toto rozhodnutie, bol najdeny citovany zakon s id: ", id, " a vo version: ", version, ".")

print(find_best_citation())

