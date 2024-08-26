import json
import string
from nltk import word_tokenize, ngrams
import Levenshtein

def remove_punctuation_and_make_3_grams(text1):
    #nltk.download('punkt')

    def remove_punctuation_and_short_words(text):
        translator = str.maketrans('', '', string.punctuation)
        text_without_punct = text.translate(translator)

        # Удаление цифр из текста
        text_without_digits = ''.join(char for char in text_without_punct if not char.isdigit())

        words = text_without_digits.split()  # Разделить текст на отдельные слова
        filtered_words = [word for word in words if len(word) >= 3]  # Отфильтровать слова длиной >= 3
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
                found_quotes.append((sentence1.strip(), idx1, sentence2.strip(), idx2, distance_ratio))

    return found_quotes

def is_sequence(arr):
    return all(arr[i] == arr[i-1] + 1 for i in range(1, len(arr)))

def find_sequences(array1, array2):
    sequences_rozhodnutia = []
    current_sequence_rozhodnutia = []
    sequences_zakony = []
    current_sequence_zakony = []

    for element1, element2 in zip(array1, array2):
        if (not current_sequence_rozhodnutia or element1 == current_sequence_rozhodnutia[-1] + 1) and (not current_sequence_zakony or element2 == current_sequence_zakony[-1] + 1):
            current_sequence_rozhodnutia.append(element1)
            current_sequence_zakony.append(element2)
        else:
            if (len(current_sequence_rozhodnutia) > 1 and is_sequence(current_sequence_rozhodnutia)) and (len(current_sequence_zakony) > 1 and is_sequence(current_sequence_zakony)):
                sequences_rozhodnutia.append(current_sequence_rozhodnutia)
                sequences_zakony.append(current_sequence_zakony)
            current_sequence_rozhodnutia = [element1]
            current_sequence_zakony = [element2]

    if (len(current_sequence_rozhodnutia) > 1 and is_sequence(current_sequence_rozhodnutia)) and (len(current_sequence_zakony) > 1 and is_sequence(current_sequence_zakony)):
        sequences_rozhodnutia.append(current_sequence_rozhodnutia)
        sequences_zakony.append(current_sequence_zakony)
    return sequences_rozhodnutia, sequences_zakony


def filter_sequences(rozhodnutie, zakon):
    najdlhsie_podpostupnost_rozhodnutia = []
    najdlhsie_podpostupnost_zakony = []
    kalka_rozhodnutie = []
    kalka_zakony = []
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
                kalka_rozhodnutie.append(najdlhsie_podpostupnost_rozhodnutia)
                kalka_zakony.append(najdlhsie_podpostupnost_zakony)
                najdlhsie_podpostupnost_rozhodnutia = rozhodnutie[i + 1]
                najdlhsie_podpostupnost_zakony = zakon[i + 1]
                cleared = True

        if not cleared or najdlhsie_podpostupnost_rozhodnutia:
            kalka_rozhodnutie.append(najdlhsie_podpostupnost_rozhodnutia)
            kalka_zakony.append(najdlhsie_podpostupnost_zakony)
    else:
        return 0

    return kalka_rozhodnutie, kalka_zakony


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
    if i == 71:
        break
print(search_text)

text2 = "Exekútor, ktorému bol doručený návrh oprávneného na vykonanie exekúcie, predloží tento návrh spolu s exekučným titulom najneskôr do 15 dní od doručenia alebo odstránenia vád návrhu súdu (§ 45) a požiada ho o udelenie poverenia na vykonanie exekúcie. Súd preskúma žiadosť o udelenie poverenia na vykonanie exekúcie, návrh na vykonanie exekúcie a exekučný titul; ak ide o exekučné konanie vykonávané na podklade rozhodnutia vykonateľného podľa § 26 zákona č. 231/1999 Z. z. o štátnej pomoci v znení neskorších predpisov, exekučný titul sa nepreskúmava. Ak súd nezistí rozpor žiadosti o udelenie poverenia na vykonanie exekúcie alebo návrhu na vykonanie exekúcie alebo exekučného titulu so zákonom, do 15 dní od doručenia žiadosti písomne poverí exekútora, aby vykonal exekúciu, táto lehota neplatí, ak ide o exekučný titul podľa § 41 ods. 2 písm. c) a d). Ak súd zistí rozpor žiadosti alebo návrhu alebo exekučného titulu so zákonom, žiadosť o udelenie poverenia na vykonanie exekúcie uznesením zamietne. Proti tomuto uzneseniu je prípustné odvolanie. Ak je uznesenie, ktorým sa žiadosť zamietla, právoplatné, súd exekučné konanie aj bez návrhu zastaví. Proti tomuto rozhodnutiu nie je prípustné odvolanie. Odseky 1 až 3 sa nepoužijú v konaní o výkon rozhodnutia, pri ktorom vznikla poplatková povinnosť zaplatiť súdne poplatky, trovy trestného konania, pokuty, svedočné, znalečné a iné trovy súdneho konania. Ak sa navrhuje vykonanie exekúcie na podklade cudzieho rozhodnutia, súd doručí návrh na vykonanie exekúcie povinnému do vlastných rúk. Ak povinný do 15 dní od doručenia návrhu na vykonanie exekúcie nepodá návrh na samostatné uznanie cudzieho rozhodnutia, súd poverí exekútora, ak sú splnené podmienky podľa odseku 2, aby vykonal exekúciu. Poverenie na vykonanie exekúcie obsahuje označenie súdu, ktorý poveruje exekútora vykonaním exekúcie, exekútora, ktorý je poverený vykonaním exekúcie, exekučného titulu a orgánu, ktorý ho vydal, oprávneného a povinného, vymáhaného nároku, prípadne potvrdenie o vykonateľnosti cudzieho exekučného titulu. Ak ide o vykonanie exekúcie na vymoženie pohľadávky na výživnom, poverenie na vykonanie exekúcie obsahuje okrem náležitostí podľa odseku 6 aj výšku preddavku na odmenu a na náhradu hotových výdavkov podľa § 197 ods. 3. Oprávnený môže kedykoľvek v priebehu exekučného konania aj bez uvedenia dôvodu podať na príslušný okresný súd návrh na zmenu exekútora. Súd rozhodne o zmene exekútora do 30 dní od doručenia návrhu oprávneného na zmenu exekútora. Súd v rozhodnutí o zmene exekútora podľa odseku 8 zároveň vykonaním exekúcie poverí exekútora, ktorého navrhne oprávnený, a vec mu postúpi spolu s exekučným spisom súdneho exekútora, ktorý bol vykonaním exekúcie pôvodne poverený. Účinky pôvodného návrhu oprávneného na vykonanie exekúcie zostávajú zachované. Trovy exekúcie pôvodného exekútora sa vypočítajú tak, ako keby došlo k zastaveniu exekúcie."

quotes = find_quotes(search_text, text2)

pole_indexov_rozhodnutia = []
pole_indexov_zakony = []

for quote in quotes:
    pole_indexov_rozhodnutia.append(quote[1])
    pole_indexov_zakony.append(quote[3])

print(pole_indexov_rozhodnutia)
print(pole_indexov_zakony)

seq1, seq2 = find_sequences(pole_indexov_rozhodnutia, pole_indexov_zakony)

print(seq1)
print(seq2)

seq3, seq4 = filter_sequences(seq1, seq2)

print(seq3, seq4)

