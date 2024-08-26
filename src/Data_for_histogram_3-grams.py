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
                found_quotes.append((sentence1.strip(), idx1, sentence2.strip(), idx2))

    return found_quotes

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


def filter_sequences(decision, law):
    longest_sequences_decision = []
    longest_sequences_laws = []
    sequences_decision = []
    sequences_laws = []

    if len(decision) > 1:
        longest_sequences_decision = decision[0]
        longest_sequences_laws = law[0]
        for i in range(len(decision) - 1):
            if (((abs(decision[i + 1][0] - decision[i][-1]) <= 10) and
                 (decision[i][-1] < decision[i + 1][0])) and
                    ((abs(law[i][-1] - law[i + 1][0]) <= 10) and
                     (law[i][-1] < law[i + 1][0]))):
                longest_sequences_decision.extend(decision[i + 1])
                longest_sequences_laws.extend(law[i + 1])
            else:
                sequences_decision.append(longest_sequences_decision)
                sequences_laws.append(longest_sequences_laws)
                longest_sequences_decision = decision[i + 1]
                longest_sequences_laws = law[i + 1]


        if longest_sequences_decision or longest_sequences_laws:
            sequences_decision.append(longest_sequences_decision)
            sequences_laws.append(longest_sequences_laws)
    else:
        return 0

    # nested_arrays = sequences_laws
    # nested_lengths = [len(array) for array in nested_arrays]
    # #print(sequences_decision, sequences_laws)
    # pocet_citovanych_slov = sum(nested_lengths)
    return sequences_laws

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

import time

def find_best_citation():
    decisions_text, date_decisions = get_data()
    array_of_results = []
    array_time = []
    for i in range(len(decisions_text)):
        start_time = time.time()
        arr_zakony_text, search_text, arr_id, arr_version = get_laws_for_judge_decision(decisions_text, date_decisions, i)
        #print(remove_punctuation_and_make_3_grams(search_text))
        list_best_citations = []
        citations_text = []
        for zakon in arr_zakony_text:
            quotes = find_quotes(search_text, zakon)

            pole_indexov_rozhodnutia = []
            pole_indexov_zakony = []
            pole_indexov_zakony_text = []
            pole_indexov_rozhodnutia_text = []

            for quote in quotes:
                pole_indexov_rozhodnutia.append(quote[1])
                citations_text.append(quote[2])
                pole_indexov_zakony.append(quote[3])
            sequences_rozhodnutia, sequences_zakony = find_sequences(pole_indexov_rozhodnutia, pole_indexov_zakony)
            # print("Najdlhsia citacia v tomto zakone sa sklada z: ", filter_sequences(sequences_rozhodnutia, sequences_zakony), " viet")
            nested_arrays = filter_sequences(sequences_rozhodnutia, sequences_zakony)
            if nested_arrays != 0:
                nested_lengths = [len(array) for array in nested_arrays]
                pocet_citovanych_slov = max(nested_lengths)
            else:
                pocet_citovanych_slov = 0
            list_best_citations.append(pocet_citovanych_slov)

        print(list_best_citations)
        citations = filter_citations(list_best_citations, 7)
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
