import Levenshtein
import json
from elasticsearch import Elasticsearch
import time
import string
from nltk import ngrams
from nltk.tokenize import word_tokenize
import nltk

def remove_punctuation_and_short_words(text):
    translator = str.maketrans('', '', string.punctuation)
    text_without_punct = text.translate(translator)
    text_without_digits = ''.join(char for char in text_without_punct if not char.isdigit())

    words = text_without_digits.split()
    filtered_words = [word for word in words if len(word) >= 3]
    return ' '.join(filtered_words)


def longest_common_subsequence(text1, text2):
    text1 = remove_punctuation_and_short_words(text1)
    text2 = remove_punctuation_and_short_words(text2)
    words1 = text1.split()
    words2 = text2.split()
    m = len(words1)
    n = len(words2)


    dp = [[0] * (n + 1) for _ in range(m + 1)]


    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if words1[i - 1] == words2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])


    pole = []
    pole_rozhodnutia = []
    pole_zakony = []
    i, j = m, n
    counter = 0
    while i > 0 and j > 0:
        if words1[i - 1] == words2[j - 1]:
            pole.append((i, j))
            i -= 1
            j -= 1
            counter += 1
        elif dp[i - 1][j] > dp[i][j - 1]:
            i -= 1
        else:
            j -= 1

    pole.reverse()
    pole_rozhodnutia.reverse()
    pole_zakony.reverse()

    return pole

def is_sequence(arr):
    return all(arr[i] == arr[i-1] + 1 for i in range(1, len(arr)))

def find_sequences(array1, array2):
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
    return sequences_rozhodnutia, sequences_zakony


def filter_sequences(rozhodnutie, zakon):
    najdlhsie_podpostupnost_rozhodnutia = []
    najdlhsie_podpostupnost_zakony = []
    postupnosti_rozhodnutia = []
    postupnosti_zakony = []
    cleared = False

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
                postupnosti_rozhodnutia.append(najdlhsie_podpostupnost_rozhodnutia)
                postupnosti_zakony.append(najdlhsie_podpostupnost_zakony)
                najdlhsie_podpostupnost_rozhodnutia = rozhodnutie[i + 1]
                najdlhsie_podpostupnost_zakony = zakon[i + 1]
                cleared = True

        if not cleared or najdlhsie_podpostupnost_rozhodnutia:
            postupnosti_rozhodnutia.append(najdlhsie_podpostupnost_rozhodnutia)
            postupnosti_zakony.append(najdlhsie_podpostupnost_zakony)
    else:
        return 0

    return postupnosti_zakony

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

def filter_citations(arr, threshold):
    if not arr:
        return None

    indecies = []
    for i in range(len(arr)):
        if arr[i] > threshold:
            indecies.append(i)

    return indecies

def find_max_position(arr, threshold):
    if not arr:
        return None

    max_index = 0
    bolo = False
    for i in range(1, len(arr)):
        if arr[i] > arr[max_index] and arr[i] > threshold:
            max_index = i
            bolo = True
    if bolo is False and arr[max_index] == 0:
        return None

    return max_index


def get_data():
    file_path = "D:\\downloads\\rozhodnutia\\chunk_40.json"

    with open(file_path, 'r', encoding='utf-8') as file:
        json_data = json.load(file)

    decisions_text = []
    date_decisions = []

    for data_element in json_data:
        decisions_text.append(data_element['dokument_fulltext'])
        date_decisions.append(data_element['datum_vydania_rozhodnutia'])
    return decisions_text, date_decisions


def get_laws_for_judge_decision(decisions_text, date_decisions, i):
    search_text = ""
    date_decision = ""
    es = Elasticsearch('http://localhost:9200')


    search_text = json.dumps(decisions_text[i], indent=2, ensure_ascii=False)
    date_decision = date_decisions[i]


    date_decision = convert_to_integer(date_decision)

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
    decisions_text, date_decisions = get_data()
    array_of_results = []
    array_time = []
    for i in range(len(decisions_text)):
        start_time = time.time()
        arr_zakony_text, search_text, arr_id, arr_version = get_laws_for_judge_decision(decisions_text, date_decisions, i)
        print(arr_id)
        print(arr_version)
        list_best_citations = []
        for zakon in arr_zakony_text:
            quotes = longest_common_subsequence(search_text, zakon)
            zakon = remove_punctuation_and_short_words(zakon)
            dlzka_zakona = len(zakon)
            pole_indexov_rozhodnutia = []
            pole_indexov_zakony = []

            for quote in quotes:
                pole_indexov_rozhodnutia.append(quote[0])
                pole_indexov_zakony.append(quote[1])
            sequences_rozhodnutia, sequences_zakony = find_sequences(pole_indexov_rozhodnutia, pole_indexov_zakony)
            # print("Najdlhsia citacia v tomto zakone sa sklada z: ", filter_sequences(sequences_rozhodnutia, sequences_zakony), " viet")
            nested_arrays = filter_sequences(sequences_rozhodnutia, sequences_zakony)
            pocet_citovanych_slov = 0
            if nested_arrays != 0:
                nested_lengths = [len(array) for array in nested_arrays]
                for l in nested_lengths:
                    if l >= 5:
                        pocet_citovanych_slov += l
            else:
                pocet_citovanych_slov = 0

            if pocet_citovanych_slov != 0:
                percento_zo_zakona = (pocet_citovanych_slov / dlzka_zakona) * 100
            else:
                percento_zo_zakona = 0
            list_best_citations.append(percento_zo_zakona)

        print("Pole obsahujuce dlzku kazdej najdlhsej citaty pre kazdy paragraf zakona ", list_best_citations)
        citations = filter_citations(list_best_citations, 5)
        id = []
        version = []
        if len(citations) >= 1:
            for j in citations:
                id.append(arr_id[j])
                version.append(arr_version[j])
        else:
            id = None
            version = None
        array_of_results.append(id)
        print(("Pre toto: ", i, " rozhodnutie, bol najdeny citovany zakon s id: ", id, " a vo version: ", version, "."))
        end_time = time.time()
        elapsed_time = end_time - start_time
        array_time.append(elapsed_time)
        print("********************************************************************************************************")
    return array_of_results, array_time

a, b = find_best_citation()

print(a)
print(b)
