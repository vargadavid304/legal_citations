import json
import string
from nltk import ngrams
from nltk.tokenize import word_tokenize
from elasticsearch import Elasticsearch

es = Elasticsearch('http://localhost:9200')


def remove_punctuation(text):
    translator = str.maketrans('', '', string.punctuation)
    text_without_punct = text.translate(translator)
    return text_without_punct

def longest_common_subsequence(text1, text2):
    text1 = remove_punctuation(text1)
    text2 = remove_punctuation(text2)
    words1 = [word for word in text1.split() if len(word) >= 3]
    words2 = [word for word in text2.split() if len(word) >= 3]
    m = len(words1)
    n = len(words2)

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
    i, j = m, n
    while i > 0 and j > 0:
        if words1[i - 1] == words2[j - 1]:
            lcs.append(words1[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] > dp[i][j - 1]:
            i -= 1
        else:
            j -= 1

    # Перевертаємо список, оскільки відновлення починалося з кінця
    lcs.reverse()

    return lcs

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
                    "more_like_this": {
                        "fields": ["versions.text"],
                        "like": search_text,
                        "min_term_freq": 1,
                        "max_query_terms": 12000
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
"size": 100
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

# Приклад використання з вашими текстами
# text1 = "V odvolaní sa má popri všeobecných náležitostiach (§ 42 ods. 3) uviesť, proti ktorému rozhodnutiu smeruje, v akom rozsahu sa napáda, v čom sa toto rozhodnutie alebo postup súdu považuje za nesprávny a čoho sa odvolateľ domáha. Odvolanie proti rozsudku alebo uzneseniu, ktorým bolo rozhodnuté vo veci samej, možno odôvodniť len tým, že v konaní došlo k vadám uvedeným v § 221 ods. 1, konanie má inú vadu, ktorá mohla mať za následok nesprávne rozhodnutie vo veci, súd prvého stupňa neúplne zistil skutkový stav veci, pretože nevykonal navrhnuté dôkazy, potrebné na zistenie rozhodujúcich skutočností, súd prvého stupňa dospel na základe vykonaných dôkazov k nesprávnym skutkovým zisteniam, doteraz zistený skutkový stav neobstojí, pretože sú tu ďalšie skutočnosti alebo iné dôkazy, ktoré doteraz neboli uplatnené (§ 205a), rozhodnutie súdu prvého stupňa vychádza z nesprávneho právneho posúdenia veci. Rozsah, v akom sa rozhodnutie napáda a dôvody odvolania môže odvolateľ rozšíriť len do uplynutia lehoty na odvolanie."
# #text2 = "Súd: Okresný súd Námestovo Spisová značka: 5C/265/2015 Identifikačné číslo súdneho spisu: 5815205480 Dátum vydania rozhodnutia: 02. 06. 2016 Meno a priezvisko sudcu, VSÚ: JUDr. Gabriela Kyseľová ECLI: ECLI:SK:OSNO:2016:5815205480.3  ROZSUDOK V MENE SLOVENSKEJ REPUBLIKY  Okresný súd Námestovo, samosudkyňou JUDr. Gabrielou Kyseľovou v právnej veci navrhovateľa: E. G., nar. XX.XX.XXXX, bytom XXX XX Q., C. XX, proti odporcom: v rade 1/ Q. G., nar. XX.XX.XXXX, bytom XXX XX A., F. XXX, v rade 2/ J. G., nar. XX.XX.XXXX, bytom XXX XX A., Nová XXX, adresa na doručovanie: C. XX, XXX XX Q., v konaní o zrušenie vyživovacej povinnosti voči plnoletým deťom, takto  r o z h o d o l :  I. Súd   z r u š u j e   vyživovaciu povinnosť navrhovateľky E. G., nar. XX.XX.XXXX voči odporcovi 1/ Q. G., nar. XX.XX.XXXX a odporcovi 2/ J. G., nar. XX.XX.XXXX, určenú jej rozsudkom Okresného súdu Námestovo zo dňa 17.10.2011 č. k. 7C/169/2010-59, počnúc dňom 01.07.2015.  II. Navrhovateľke sa náhrada trov konania   n e p r i z n á v a .  o d ô v o d n e n i e :  Návrhom podaným súdu dňa 10.09.2015 navrhovateľka žiadala, aby súd zrušil jej vyživovaciu povinnosť voči odporcovi I/ Q. G. a odporcovi II/ J. G., ktorá jej bola naposledy určená rozsudkom Okresného súdu Námestovo č. k. 7C/169/2010-59 zo dňa 17.10.2011, ktorým bola schválená rodičovská dohoda, na základe ktorej sa zaviazala prispievať na výživu každého z odporcov vo výške 30 % zo sumy životného minima.  Odporca I/ - Q. G. ukončil 06/2015 štúdium na J. škole v F. a od 09/2015 je vedený ako nezamestnaný. Odporca II/ - J. G. ukončil školskú dochádzku 06/2015 na J. obchodu a služieb v C. P. a od 02.09.2015 pracuje vo firme L. SE, T..  Súd s poukazom na ustanovenie § 101 ods. 2 veta druhá O.s.p. konal a rozhodol v neprítomnosti odporcu II/, ktorý svoju neúčasť neospravedlnil a nežiadal o odročenie pojednávania. Súhlasil (zriekol) sa dávky výživného.  Navrhovateľka zotrvala na podanom návrhu, pretože odporcovia sú plnoletí a obaja si zarábajú sami na živobytie. Opatruje svojho otca, poberá len opatrovateľský príspevok a dávku v hmotnej núdzi 63,20 €. Syn Q. ukončil školu koncom mája 2015 a dohodla sa s ním, že mu prestane prispievať na výživu, keďže začal pracovať. Spočiatku pracoval ako brigádnik, v súčasnosti pracuje v pracovnom pomere. Syn J. pracuje v spoločnosti L. od 2.9.2015 doposiaľ a žije s ňou v domácnosti, žiaden z odporcov neštuduje. J. ukončil štúdium v 06/2015.  Odporca I/  vo výpovedi súhlasil so zrušením vyživovacej povinnosti, keďže od 05/2015 ukončil štúdium a začal pracovať najskôr formou brigád ako stavebný robotník a od 04/2016 na základe pracovnej zmluvy ako vodič nakladať vo firme V. H., má svoj príjem, žije v domácnosti s otcom, s matkou - navrhovateľkou sa stretáva sporadicky. Vie si zarobiť na živobytie a nie je odkázaný na výživu navrhovateľky.  Odporca II/ v písomnom vyjadrení súhlasil so zrušením vyživovacej povinnosti.    V rámci dokazovania sa súd oboznámil s obsahom listín tvoriacich súčasť spisu a to pripojeným spisom súdu 7C/169/2010, z neho najmä rozsudkom súdu zo dňa 17.10.2011 č. k. 7C/169/2010, ktorým bolo rozvedené manželstvo navrhovateľky a otca odporcov, s pracovnou zmluvou odporcu II/  uzavretou 31.08.2015, lustráciou Sociálnej poisťovne, správami Úradu práce, sociálnych vecí a rodiny Námestovo, oddelenie služieb pre občana, Námestovo, ohľadom evidencie účastníkov konania v nezamestnanosti a poberaní dávok v hmotnej núdzi, správou L. SE, T. a vyjadrením odporcu II/, základe čoho ustálil nasledovný skutkový stav:  Navrhovateľke bola určená vyživovacia povinnosť voči odporcom rozsudkom Okresného súdu Námestovo zo dňa 17.10.2011 č. k. 7C/169/2010-59, právoplatným 22.11.2011  tak, že počnúc právoplatnosťou rozsudku, ktorým bola schválená rodičovská dohoda sa zaviazala prispievať na výživu odporcu I/a II/ sumou 30 % so sumy životného minima na nezaopatrené dieťa podľa § 2 zákona č. 601/2003 Z. z. o životnom minime a o zmene a doplnení niektorých zákonov v znení neskorších predpisov aktuálnej pre daný mesiac, za ktorý podľa tohto rozsudku jej vznikla povinnosť platiť výživného, vždy do 15. dňa v mesiaci vopred k rukám otca vtedy ešte maloletých odporcov.  Odporca I/ dňa 31.05.2015 ukončil stredoškolské štúdium na J. škole, F., U. XXX (lustrácia SP - čl.10) a ďalším štúdiom sa nepripravuje na budúce povolanie. V súčasnosti je  zamestnaný na základe pracovnej zmluvy ako vodič nakladač vo firme V. H., z ktorej práce dostáva mzdu slúžiacu na pokrytie nevyhnutných výdavkov, teda nadobudol schopnosť sa živiť.  Odporca II/  ukončil stredoškolské štúdium na J. odbornej škole obchodu a služieb C. P. dňa 30.06.2015 a  od 02.09.2015 do 31.12.2015 pracoval v spoločnosti L. SE, T., T. (čl.26) a od 01.01.2016 pracuje v spoločnosti E. T. F., s.r.o., so sídlom F., nadobudol schopnosť sa sám živiť.  Podľa § 62 ods. 1 zákona č. 36/2005 Z. z. o rodine a o zmene a doplnení niektorých zákonov - ďalej len, plnenie  vyživovacej  povinnosti  rodičov  k  deťom je ich zákonná  povinnosť, ktorá  trvá do času, kým  deti nie sú schopné samé sa živiť.  Podľa § 78 ods. 2 ZoR ak dôjde k zrušeniu alebo zníženiu výživného pre maloleté dieťa za uplynulý čas, spotrebované výživné sa nevracia.  V súlade so zisteným skutkovým stavom a citovaným ustanovením zákona súd návrhu vyhovel. Mal za preukázané, že odporcovia sú plnoletí, ukončili stredoškolské štúdium a nepripravujú sa na budúce povolenie. V súčasnosti obaja pracujú v pracovnom pomere založenom na základe pracovnej zmluvy, za čo dostávajú mzdu. Získali schopnosť sami sa živiť a zarobiť si peňažné prostriedky na úhradu základných životných potrieb. Vyživovaciu povinnosť súd zrušil počnúc nadobudnutím schopnosti oboch odporcov sa živiť, t.j. dňom 01.07.2015, kedy už ani jeden z nich neštudoval.  O náhrade trov konania súd rozhodol podľa § 142 ods. 1 O.s.p. v spojení s ustanovením § 150 ods. 1 O.s.p. tak, že úspešnému  navrhovateľovi náhradu trov konania nepriznal, pretože si náhradu neuplatňoval a ani z obsahu spisu nevyplýva, že by mu nejaké trovy konania vznikli. Súd prihliadol aj na dôvody hodné osobitného zreteľa, ktoré vzhliadol v charaktere konania, ktorým je zrušenie vyživovacej povinnosti medzi otcom a plnoletým synom.  O súdnom poplatku súd nerozhodoval, keďže konanie je vecné oslobodené od poplatku s poukazom na ustanovenie § 4 ods. 1 písm. g) zákona č. 71/1992 Z. z. o súdnych poplatkoch a poplatku za výpis z registra trestov.  Poučenie:  Proti tomuto rozsudku možno podať odvolanie  do 15 dní odo dňa jeho doručenia cestou tunajšieho súdu ku Krajskému súdu v Žiline.  Podľa § 205 OSP ods. 1, 2 v  odvolaní sa  má popri  všeobecných náležitostiach (§ 42 ods. 3) uviesť, proti ktorému rozhodnutiu smeruje, v akom rozsahu sa napáda, v čom sa toto rozhodnutie alebo postup súdu považuje za nesprávny a čoho sa odvolateľ domáha. Odvolanie možno odôvodniť len tým, že konanie prvého stupňa má inú vadu, ktorá mohla mať za následok nesprávne rozhodnutie vo veci alebo že rozsudok vychádza z nesprávneho právneho posúdenia veci.  Proti tomuto rozsudku možno podať do 15 dní odo dňa doručenia odvolanie u Okresného súdu v Námestove.  V Námestove dňa 2. júna 2016 JUDr. Gabriela Kyseľová samosudkyňa"
#
# text3 = "O povinnosti nahradiť trovy konania rozhoduje súd na návrh spravidla v rozhodnutí, ktorým sa konanie končí. Účastník, ktorému sa prisudzuje náhrada trov konania, je povinný trovy konania vyčísliť najneskôr do troch pracovných dní od vyhlásenia tohto rozhodnutia. Ak účastník v lehote podľa odseku 1 trovy nevyčísli, súd mu prizná náhradu trov konania vyplývajúcich zo spisu ku dňu vyhlásenia rozhodnutia s výnimkou trov právneho zastúpenia; ak takému účastníkovi okrem trov právneho zastúpenia iné trovy zo spisu nevyplývajú, súd mu náhradu trov konania neprizná a v takom prípade súd nie je viazaný rozhodnutím o prisúdení náhrady trov konania tomuto účastníkovi v rozhodnutí, ktorým sa konanie končí. V zložitých prípadoch, najmä z dôvodu väčšieho počtu účastníkov konania alebo väčšieho počtu nárokov uplatňovaných v konaní súd môže rozhodnúť, že o trovách konania rozhodne do 30 dní po právoplatnosti rozhodnutia vo veci samej; ustanovenie § 166 sa nepoužije. Ustanovenia odsekov 1 a 2 platia primerane s tým, že lehota troch pracovných dní plynie od právoplatnosti rozhodnutia vo veci samej. Ak sa rozhodnutie, ktorým sa konanie končí, nevyhlasuje a bol podaný návrh na rozhodnutie o trovách, súd vyzve účastníka na vyčíslenie trov do troch pracovných dní od doručenia výzvy. Ustanovenia odsekov 1 a 2 platia primerane. Trovy konania určí súd podľa sadzobníkov a podľa zásad platných pre náhradu mzdy a hotových výdavkov. Určiť výšku trov môže predseda senátu alebo samosudca až v písomnom vyhotovení rozhodnutia. O trovách štátu súd rozhodne aj bez návrhu. Súd môže o náhrade trov konania rozhodnúť aj tak, že namiesto určenia výšky trov prizná účastníkovi náhradu trov konania vyjadrenú zlomkom alebo percentom. Po právoplatnosti tohto rozhodnutia rozhodne o výške náhrady trov konania súd samostatným uznesením. Vo výroku o náhrade trov konania súd vyjadrí osobitne trovy právneho zastúpenia a iné trovy konania, ktorých náhrada sa účastníkovi priznáva."
# text4 = "Verejné zasadnutie o návrhu na dohodu o vine a treste sa vykoná za stálej prítomnosti všetkých členov senátu, zapisovateľa, prokurátora, obvineného, a ak má obvinený obhajcu, aj za stálej prítomnosti obhajcu. Po otvorení verejného zasadnutia prokurátor prednesie návrh na dohodu o vine a treste. Po prednesení návrhu dohody o vine a treste predseda senátu zistí formou otázok, či obvinený rozumie podanému návrhu na dohodu o vine a treste, súhlasí, aby sa jeho trestná vec prejednala touto skrátenou formou, čím sa vzdáva práva na verejný súdny proces, rozumie, čo tvorí podstatu skutku, ktorý sa mu kladie za vinu, bol ako obvinený poučený o svojich právach, najmä o práve na obhajobu, či mu bola daná možnosť na slobodnú voľbu obhajcu a či sa s obhajcom mohol radiť o spôsobe obhajoby, rozumel podstate konania o návrhu na dohodu o vine a treste, rozumie právnej kvalifikácii skutku ako trestného činu, bol oboznámený s trestnými sadzbami, ktoré zákon ustanovuje za trestné činy jemu kladené za vinu, sa dobrovoľne priznal a uznal vinu za spáchaný skutok, ktorý sa v návrhu dohody o vine a treste kvalifikuje ako určitý trestný čin, súhlasí s navrhovaným trestom, trest prijíma a v stanovených lehotách sa podriadi výkonu trestu a ochrannému opatreniu a nahradí škodu v rozsahu dohody, si uvedomuje, že ak súd prijme návrh na dohodu o vine a treste a vynesie rozsudok, ktorý nadobudne právoplatnosť vyhlásením, nebude možné proti tomuto rozsudku podať odvolanie. Ak súd dohodu o vine a treste odmietne podľa § 331 ods. 4 a po podaní obžaloby sa koná hlavné pojednávanie, priznanie spáchania skutku obvineným v konaní o dohode o vine a treste nemožno na hlavnom pojednávaní použiť ako dôkaz. Ak mladistvý v čase konania nedovŕšil osemnásť rokov svojho veku, súd zistí, či jeho obhajca a zákonný zástupca súhlasia s dohodou o vine a treste. Po vyjadrení obvineného ku všetkým otázkam, ako aj po vyjadrení strán k otázkam, ktoré sa ich priamo týkajú, súd sa odoberie na záverečnú poradu."
# text5 = "Súd môže rozhodovať len o skutku, jeho právnej kvalifikácii, primeranosti trestu, ochrannom opatrení vo vzťahu k obvinenému, ako aj o výroku na náhradu škody v rozsahu uvedenom v návrhu na dohodu o vine a treste, ak obvinený odpovedal na všetky otázky „áno“. Ak súd dohodu o vine a treste, ktorá v navrhnutom znení nie je zrejme neprimeraná, ale ju nepovažuje za spravodlivú, oznámi svoje výhrady stranám, ktoré môžu navrhnúť nové znenie dohody o vine a treste. Na ten účel súd preruší verejné zasadnutie na potrebný čas. Ak sa strany dohodnú, postupuje sa primerane podľa odseku 4; ak s dohodou o vine a treste nesúhlasí poškodený, postupuje sa primerane podľa § 232 ods. 3 posledná veta. Ak sa strany nedohodnú, postupuje súd podľa odseku 3. Ak súd dohodu o vine a treste v navrhnutom rozsahu neschváli alebo obvinený odpovedal na niektorú otázku „nie”, uznesením vráti vec prokurátorovi do prípravného konania; ak je obvinený vo väzbe a súd zároveň nerozhodol o prepustení obvineného na slobodu, pokračuje väzba v prípravnom konaní, ktorá však nesmie spolu s väzbou už vykonanou v prípravnom konaní presiahnuť lehotu uvedenú v § 76 ods. 7. Ak súd dohodu o vine a treste schváli, potvrdí to rozsudkom, ktorý verejne vyhlási. Proti tomuto rozsudku nie je prípustné odvolanie ani dovolanie okrem dovolania podľa § 371 ods. 1 písm. c) a ods. 2. Rozsudok nadobudne právoplatnosť vyhlásením."

for i, zakon in enumerate(arr_zakony_text):
    text1_words = search_text
    text2_words = zakon

    lcs = longest_common_subsequence(text1_words, text2_words)
    print(i)
    print(" ".join(lcs))
