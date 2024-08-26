import json
import string
from nltk import ngrams
from nltk.tokenize import word_tokenize
from elasticsearch import Elasticsearch

es = Elasticsearch('http://localhost:9200')


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
    words1 = text1.split()  # Розділяємо перший текст на слова
    words2 = text2.split()  # Розділяємо другий текст на слова
    m = len(words1)  # Кількість слів у першому тексті
    n = len(words2)  # Кількість слів у другому тексті

    # Ініціалізуємо матрицю для зберігання проміжних результатів
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Заповнюємо матрицю за допомогою динамічного програмування
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if words1[i - 1] == words2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # Відновлюємо найбільшу спільну підпослідовність
    lcs = []
    pole_rozhodnutia = []
    pole_zakony = []
    i, j = m, n
    counter = 0
    while i > 0 and j > 0:
        if words1[i - 1] == words2[j - 1]:
            lcs.append(words1[i - 1])
            pole_zakony.append(i)
            pole_rozhodnutia.append(j)
            i -= 1
            j -= 1
            counter += 1
        elif dp[i - 1][j] > dp[i][j - 1]:
            i -= 1
        else:
            j -= 1

    # Перевертаємо список, оскільки відновлення починалося з кінця
    lcs.reverse()
    pole_rozhodnutia.reverse()
    pole_zakony.reverse()

    return lcs, pole_rozhodnutia, pole_zakony

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
    rozhodnutia = []
    zakony = []
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
                rozhodnutia.append(najdlhsie_podpostupnost_rozhodnutia)
                zakony.append(najdlhsie_podpostupnost_zakony)
                najdlhsie_podpostupnost_rozhodnutia = rozhodnutie[i + 1]
                najdlhsie_podpostupnost_zakony = zakon[i + 1]
                cleared = True

        if not cleared or najdlhsie_podpostupnost_rozhodnutia:
            rozhodnutia.append(najdlhsie_podpostupnost_rozhodnutia)
            zakony.append(najdlhsie_podpostupnost_zakony)
    else:
        return 0

    nested_arrays = rozhodnutia, zakony
    nested_lengths = [len(subarray) for array in nested_arrays for subarray in array]
    #print(rozhodnutia, zakony)
    # Нахождение самой большой длины
    if nested_lengths != []:
        max_length = max(nested_lengths)
    else:
        return None
    return max_length

def spajame_lcs(bet_lcs, pole_indexov_rozhodnutia, pole_indexov_zakony):
    spojene_lcs = []
    first = True
    for i in range(1, len(bet_lcs)):
        if (pole_indexov_rozhodnutia[i][0] - pole_indexov_rozhodnutia[i-1][len(pole_indexov_rozhodnutia[i-1]) - 1]) <= 10 and (pole_indexov_zakony[i][0] - pole_indexov_zakony[i-1][len(pole_indexov_zakony[i-1]) - 1]) <= 10:
            if first is True:
                spojene_lcs.extend(bet_lcs[i-1])
                spojene_lcs.extend(bet_lcs[i])
                first = False
            else:
                spojene_lcs.extend(bet_lcs[i])
    return spojene_lcs
def find_max_position(arr):
    if not arr:
        return None

    max_index = 0
    for i in range(1, len(arr)):
        if arr[i] > arr[max_index]:
            max_index = i

    return max_index

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
      "size": 30,
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
        "field": "_ident"
      }
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
    print(arr_id)
    print(arr_version)
    list_best_citations = []
    lcs, pole_indexov_rozhodnutia, pole_indexov_zakony = [], [], []
    for zakon in arr_zakony_text:
        lcs, pole_indexov_rozhodnutia, pole_indexov_zakony = longest_common_subsequence(search_text, zakon)
        sequences_rozhodnutia, sequences_zakony = find_sequences(pole_indexov_rozhodnutia, pole_indexov_zakony)
        print("Najdlhsia citacia v tomto zakone sa sklada z: ", filter_sequences(sequences_rozhodnutia, sequences_zakony), " viet")
        list_best_citations.append(filter_sequences(sequences_rozhodnutia, sequences_zakony))
        print(lcs)
    print(list_best_citations)
    max_pos = find_max_position(list_best_citations)
    id = arr_id[max_pos]
    version = arr_version[max_pos]
    print("Pre toto rozhodnutie, bol najdeny citovany zakon s id: ", id, " a vo version: ", version, ".")


print(find_best_citation())
