import re
import time
import json
from tqdm import tqdm

from modules.script import Script
from teachable.teachable import Teachable
from misc.terminalcolors import ANSITerminalColors as ANSI


class AnalyzeSectionCompletion(Script):
    RUNNING = f"  {ANSI.OKBLUE}[⚙]{ANSI.ENDC}  "
    OKAY = f"  {ANSI.OKGREEN}[✓]{ANSI.ENDC}  "
    WARNING = f"  {ANSI.WARNING}[?]{ANSI.ENDC}  "
    ERROR = f"  {ANSI.FAIL}[✗]{ANSI.ENDC}  "
    RATE_LIMIT_DELAY_SLEEP = 0.2  # https://docs.teachable.com/docs/rate-limits-1

    def __init__(self, teachable_key_path: str, scopes=(), token_path=""):
        super().__init__(scopes, token_path, teachable_key_path)
        self.teachable = Teachable()
        self.teachable.authorize(teachable_key_path)
        self.indent = 0

    def run(self, course_id: int, section_name: str):
        self.indent = 0
        # todo ogarnij to zeby bylo na prawde
        lecture_data = [
            {
                "lecture": {
                    "id": 52270118,
                    "name": "Odpowiedzi do zadania domowego z modu\u0142u 2",
                    "position": 1,
                    "is_published": False,
                    "lecture_section_id": 10144789,
                    "attachments": [
                        {
                            "id": 96365139,
                            "name": None,
                            "kind": "text",
                            "url": None,
                            "text": "<p>Poni\u017cej znajdziesz dokument z odpowiedziami z zadania domowego z poprzedniego modu\u0142u. <strong>Pami\u0119taj, \u017ce komentarz do zada\u0144 dost\u0119pny jest tylko dla os\u00f3b, kt\u00f3re wykonaj\u0105 zadanie w ci\u0105gu 7 dni od jego udost\u0119pnienia - prowadz\u0105cy sprawdza wtedy prace domowe i odsy\u0142a je z indywidualnym komentarzem. </strong></p>",
                            "position": 1
                        },
                        {
                            "id": 96365140,
                            "name": "Zadanie domowe - Modu\u0142 2.pdf",
                            "kind": "pdf_embed",
                            "url": "https://cdn.fs.teachablecdn.com/Uf9u0sBASR2KYEahfCAX",
                            "text": None,
                            "position": 2,
                            "file_size": 0,
                            "file_extension": "pdf"
                        }
                    ]
                }
            },
            {
                "lecture": {
                    "id": 52270119,
                    "name": "Zeszyt ćwiczeń",
                    "position": 2,
                    "is_published": False,
                    "lecture_section_id": 10144789,
                    "attachments": [
                        {
                            "id": 96365141,
                            "name": "Modu\u0142 3 - Zwierze\u0328ta Egzotyczne.pdf",
                            "kind": "pdf_embed",
                            "url": "https://cdn.fs.teachablecdn.com/0YopeJmgQyiDtyWl2Dzj",
                            "text": None,
                            "position": 1,
                            "file_size": 0,
                            "file_extension": "pdf"
                        }
                    ]
                }
            },
            {
                "lecture": {
                    "id": 52270120,
                    "name": "Sprawdź siebie",
                    "position": 3,
                    "is_published": False,
                    "lecture_section_id": 10144789,
                    "attachments": [
                        {
                            "id": 96365142,
                            "name": None,
                            "kind": "text",
                            "url": None,
                            "text": "<p>Przygotowali\u015bmy dla Ciebie quiz, kt\u00f3ry pomo\u017ce Ci sprawdzi\u0107 Twoj\u0105 wiedz\u0119 z omawianego tematu przed obejrzeniem nagra\u0144. Powodzenia!</p>",
                            "position": 1
                        },
                        {
                            "id": 96365143,
                            "name": None,
                            "kind": "quiz",
                            "url": None,
                            "text": None,
                            "position": 2,
                            "quiz": {
                                "id": 2193686,
                                "type": "Quiz",
                                "questions": [
                                    {
                                        "question": "W badaniu klinicznym w\u0119\u017ca dla naszego bezpiecze\u0144stwa przyjmujemy, \u017ce na ka\u017cde \u2026..  zwierz\u0119cia potrzebna jest jedna osoba do asekuracji.",
                                        "question_type": "single",
                                        "answers": [
                                            "3m",
                                            "2m",
                                            "1,5m",
                                            "1m"
                                        ],
                                        "correct_answers": [
                                            "1,5m"
                                        ],
                                        "graded": True
                                    },
                                    {
                                        "question": "Czym jest autotomia?",
                                        "question_type": "single",
                                        "answers": [
                                            "Zespo\u0142em odruch\u00f3w u zwierz\u0105t wyst\u0119puj\u0105cych przy b\u00f3lu",
                                            "Wolicjalnym odrzuceniem ogona przez jaszczurk\u0119",
                                            "Pora\u017ceniem nerw\u00f3w ruchowych",
                                            "Zatrzymanie pasa\u017cu tre\u015bci jelitowej"
                                        ],
                                        "correct_answers": [
                                            "Wolicjalnym odrzuceniem ogona przez jaszczurk\u0119"
                                        ],
                                        "graded": True
                                    },
                                    {
                                        "question": "Deformacja skorupy u \u017c\u00f3\u0142wia, utrata jej twardo\u015bci, oraz zaburzenie proporcji wielko\u015bci tarczek mo\u017ce \u015bwiadczy\u0107 o:",
                                        "question_type": "single",
                                        "answers": [
                                            "Nieprawid\u0142owej wilgotno\u015bci w zbiorniku hodowlanym",
                                            "Metabolicznej chorobie ko\u015bci",
                                            "Zbyt niskiej temperaturze chowu",
                                            "Herpeswirozie"
                                        ],
                                        "correct_answers": [
                                            "Metabolicznej chorobie ko\u015bci"
                                        ],
                                        "graded": True
                                    },
                                    {
                                        "question": "Naturalnie op\u00f3\u017aniony odruch posturalny (naprawczy) wyst\u0119puje u",
                                        "question_type": "single",
                                        "answers": [
                                            "Pyton\u00f3w kr\u00f3lewskich",
                                            "Agam brodatych ",
                                            "Boa dusiciel",
                                            "Op\u00f3\u017aniony odruch naprawczy zawsze stanowi nieprawid\u0142owo\u015b\u0107 "
                                        ],
                                        "correct_answers": [
                                            "Pyton\u00f3w kr\u00f3lewskich"
                                        ],
                                        "graded": True
                                    },
                                    {
                                        "question": "Zwiotczenie fragmentu cia\u0142a u w\u0119\u017ca b\u0119dzie nasuwa\u0142o podejrzenie",
                                        "question_type": "single",
                                        "answers": [
                                            "Urazu kr\u0119gos\u0142upa",
                                            "IBD",
                                            "Niedobor\u00f3w tiaminy",
                                            "MBD"
                                        ],
                                        "correct_answers": [
                                            "Urazu kr\u0119gos\u0142upa"
                                        ],
                                        "graded": True
                                    }
                                ]
                            }
                        }
                    ]
                }
            },
            {
                "lecture": {
                    "id": 52270121,
                    "name": "3.1 Badanie kliniczne gad\u00f3w",
                    "position": 4,
                    "is_published": False,
                    "lecture_section_id": 10144789,
                    "attachments": [
                        {
                            "id": 96365144,
                            "name": "badanie kliniczne gadow cz1.mp4",
                            "kind": "video",
                            "url": None,
                            "text": None,
                            "position": 1,
                            "file_size": 0,
                            "file_extension": "mp4"
                        }
                    ]
                }
            },
            {
                "lecture": {
                    "id": 52270122,
                    "name": "3.2 Badanie kliniczne gad\u00f3w cz. 2",
                    "position": 5,
                    "is_published": False,
                    "lecture_section_id": 10144789,
                    "attachments": [
                        {
                            "id": 96365145,
                            "name": "32badanie gadow 2.mp4",
                            "kind": "video",
                            "url": None,
                            "text": None,
                            "position": 1,
                            "file_size": 0,
                            "file_extension": "mp4"
                        }
                    ]
                }
            },
            {
                "lecture": {
                    "id": 52270123,
                    "name": "Quiz po zaj\u0119ciach",
                    "position": 6,
                    "is_published": False,
                    "lecture_section_id": 10144789,
                    "attachments": [
                        {
                            "id": 96365146,
                            "name": None,
                            "kind": "text",
                            "url": None,
                            "text": "<p>Poni\u017cszy test ma na celu sprawdzenie Twojej wiedzy po ogl\u0105dni\u0119ciu nagra\u0144 (test jest tylko dla Twojej wiadomo\u015bci). Dzi\u0119ki temu b\u0119dziesz wiedzie\u0107, kt\u00f3re tematy musisz jeszcze doczyta\u0107 lub ponownie obejrze\u0107 :)</p>",
                            "position": 1
                        },
                        {
                            "id": 96365147,
                            "name": None,
                            "kind": "quiz",
                            "url": None,
                            "text": None,
                            "position": 2,
                            "quiz": {
                                "id": 2193687,
                                "type": "Quiz",
                                "questions": [
                                    {
                                        "question": "Za\u017c\u00f3\u0142cone b\u0142ony \u015bluzowe u gad\u00f3w",
                                        "question_type": "single",
                                        "answers": [
                                            "\u015awiadcz\u0105 zawsze o patologiach w\u0105troby",
                                            "Mog\u0105 wyst\u0119powa\u0107 np. Podczas tworzenia jaj i jest to zjawisko fizjologiczne",
                                            "Stanowi\u0105 patognomiczny objaw st\u0142uszczenia w\u0105troby",
                                            "U \u017c\u00f3\u0142wi zawsze przybieraj\u0105 tak\u0105 barw\u0119"
                                        ],
                                        "correct_answers": [
                                            "Mog\u0105 wyst\u0119powa\u0107 np. Podczas tworzenia jaj i jest to zjawisko fizjologiczne"
                                        ],
                                        "graded": True
                                    },
                                    {
                                        "question": "Badanie kliniczne gad\u00f3w najlepiej wykonywa\u0107",
                                        "question_type": "single",
                                        "answers": [
                                            "W obni\u017conej temperaturze gdy\u017c zwierz\u0119 jest wtedy spokojniejsze",
                                            "W temperaturze wy\u017csza ni\u017c pokojowa gdy\u017c gad b\u0119dzie wtedy zachowywa\u0142 si\u0119 wzgl\u0119dnie normalnie",
                                            "Temperatura nie ma znaczenia, istotne jest do\u015bwietlanie podczas badania UVB",
                                            "Temperatura w momencie badania nie ma znaczenia gdy\u017c i tak bazujemy g\u0142\u00f3wnie na wynikach bada\u0144 dodatkowych"
                                        ],
                                        "correct_answers": [
                                            "W temperaturze wy\u017csza ni\u017c pokojowa gdy\u017c gad b\u0119dzie wtedy zachowywa\u0142 si\u0119 wzgl\u0119dnie normalnie"
                                        ],
                                        "graded": True
                                    },
                                    {
                                        "question": "Ciemna broda u agamy brodatej podczas badania oznacza",
                                        "question_type": "single",
                                        "answers": [
                                            "Chorob\u0119 bakteryjn\u0105",
                                            "Pocz\u0105tkowy objaw adenowirozy",
                                            "Nie jest objawem specyficznym, mo\u017ce wynika\u0107 cho\u0107by z rozdra\u017cnienia zwierz\u0119cia",
                                            "Jest objawem hipotermii"
                                        ],
                                        "correct_answers": [
                                            "Nie jest objawem specyficznym, mo\u017ce wynika\u0107 cho\u0107by z rozdra\u017cnienia zwierz\u0119cia"
                                        ],
                                        "graded": True
                                    },
                                    {
                                        "question": "Zapadni\u0119te oczy, widoczne wyrostki poprzeczne kr\u0119g\u00f3w ogonowych, apatia mog\u0105 \u015bwiadczy\u0107 o",
                                        "question_type": "single",
                                        "answers": [
                                            "Odwodnieniu",
                                            "Metabolicznej chorobie ko\u015bci",
                                            "S\u0105 objawami wychudzenia",
                                            "S\u0105 oznakami fazy dekompensacyjnej wstrz\u0105su"
                                        ],
                                        "correct_answers": [
                                            "S\u0105 objawami wychudzenia"
                                        ],
                                        "graded": True
                                    },
                                    {
                                        "question": "W podstawowym badaniu klinicznym du\u017cych jaszczurek nie nale\u017cy obawia\u0107 si\u0119",
                                        "question_type": "single",
                                        "answers": [
                                            "Z\u0119b\u00f3w",
                                            "Pazur\u00f3w",
                                            "Jadu",
                                            "Uderzenia ogonem"
                                        ],
                                        "correct_answers": [
                                            "Jadu"
                                        ],
                                        "graded": True
                                    }
                                ]
                            }
                        }
                    ]
                }
            },
            {
                "lecture": {
                    "id": 52270128,
                    "name": "3.1 Q&A",
                    "position": 11,
                    "is_published": False,
                    "lecture_section_id": 10144789,
                    "attachments": [
                        {
                            "id": 96365151,
                            "name": "QA Modu\u0142 3 ciekawostka.mp4",
                            "kind": "video",
                            "url": None,
                            "text": None,
                            "position": 1,
                            "file_size": 0,
                            "file_extension": "mp4"
                        }
                    ]
                }
            },
            {
                "lecture": {
                    "id": 52270124,
                    "name": "Zadaj pytanie",
                    "position": 7,
                    "is_published": False,
                    "lecture_section_id": 10144789,
                    "attachments": [
                        {
                            "id": 96365148,
                            "name": None,
                            "kind": "text",
                            "url": None,
                            "text": "<p>Mamy \u015bwiadomo\u015b\u0107, \u017ce mo\u017cesz mie\u0107 du\u017co pyta\u0144, dlatego przygotowali\u015bmy anonimow\u0105 ankiet\u0119, w kt\u00f3rej mo\u017cesz zadawa\u0107 swoje pytania do danego modu\u0142u, a my na nie odpowiemy.</p><p>Dajemy Ci 7 dni od momentu pojawienia si\u0119 modu\u0142u na platformie na zadanie pyta\u0144. Po tym czasie mo\u017cliwo\u015b\u0107 zadawania pyta\u0144 w ankiecie zostanie wy\u0142\u0105czona.</p>",
                            "position": 1
                        },
                        {
                            "id": 96365149,
                            "name": None,
                            "kind": "code_embed",
                            "url": None,
                            "text": "<iframe src=\"https://docs.google.com/forms/d/e/1FAIpQLScDNWZsP478GGHJJCAlcyd5UgVRPUliTfja2upgyuu8FMRMaA/viewform?embedded=True\" width=\"640\" height=\"567\" frameborder=\"0\" marginheight=\"0\" marginwidth=\"0\">Loading\u2026</iframe>",
                            "position": 2
                        }
                    ]
                }
            },
            {
                "lecture": {
                    "id": 52270125,
                    "name": "Zadanie domowe",
                    "position": 8,
                    "is_published": False,
                    "lecture_section_id": 10144789,
                    "attachments": [
                        {
                            "id": 96365150,
                            "name": None,
                            "kind": "text",
                            "url": None,
                            "text": "<p>Nadszed\u0142 czas na wykonanie kolejnej pracy domowej - cho\u0107 pami\u0119taj, nie jest ona obowi\u0105zkowa.<br class=\"softbreak\"><br class=\"softbreak\">Upewnij si\u0119 dwa razy, \u017ce podajesz sw\u00f3j poprawny adres e-mail by odpowiedzi na pewno do Ciebie trafi\u0142y.</p><hr><p><br></p><p class=\"ql-align-center\"><strong style=\"color: rgb(130, 13, 13);\">ABY OTWORZY\u0106 ARKUSZ PRACY DOMOWEJ </strong></p><p class=\"ql-align-center\"><a href=\"https://docs.google.com/forms/d/e/1FAIpQLSdKGR2-z1OAvlFnzDYd8Q2zJh-MwM6z7vOEpgL_V0FzUCQeaw/viewform?usp=sf_link\" rel=\"noopener noreferrer\" target=\"_blank\"><strong>KLIKNIJ TUTAJ</strong></a></p>",
                            "position": 1
                        }
                    ]
                }
            },
            {
                "lecture": {
                    "id": 52270126,
                    "name": "Materia\u0142y dodatkowe w j\u0119zyku polskim",
                    "position": 9,
                    "is_published": False,
                    "lecture_section_id": 10144789,
                    "attachments": []
                }
            },
            {
                "lecture": {
                    "id": 52270127,
                    "name": "Materia\u0142y dodatkowe po angielsku",
                    "position": 10,
                    "is_published": False,
                    "lecture_section_id": 10144789,
                    "attachments": []
                }
            }
        ]
        response = self.teachable.get_course(course_id)
        section = list(filter(
            lambda item: item["name"] == section_name,
            response["course"]["lecture_sections"]
        ))[0]
        lecture_data = []
        for lecture in tqdm(section["lectures"], colour="#47b1fc", ncols=100, desc="Pobieranie danych o sekcjach", total=len(section["lectures"])):
            time.sleep(self.RATE_LIMIT_DELAY_SLEEP)
            lecture_data.append(self.teachable.get_lecture(course_id, lecture["id"]))

        # ------------------ etap 1 ------------------------

        self._send_msg(self.RUNNING, "Start etapu 1 - konwencje nazwowe.")
        self.indent = 1
        lecture_parts = self.test_konwencje_nazwowe(lecture_data)
        self.indent = 0
        if lecture_parts is None:
            self._send_msg(self.ERROR, "Test nie przeszedł etapu 1 - konwencje nazwowe.\n")
            return
        else:
            self._send_msg(self.OKAY, "Test przeszedł etap 1 - konwencje nazwowe.\n")

        # ------------------ etap 2 ------------------------

        self._send_msg(self.RUNNING, "Start etapu 2 - walidacja zawartości lekcji.")
        self.indent = 1

        out = 0
        out += not self.test_answers_for_hw(lecture_parts["odp_do_zad_dom"])
        out += not self.test_workbook(lecture_parts["zeszyt_cw"])
        out += not self.test_quiz_before(lecture_parts["quiz_przed"])
        for vid in lecture_parts["nagranie"]:
            out += not self.test_video(vid, course_id, vid["id"])
            time.sleep(self.RATE_LIMIT_DELAY_SLEEP)
        out += not self.test_quiz_after(lecture_parts["quiz_po"])
        for qna in lecture_parts["qna"]:
            out += not self.test_qna(qna, course_id, qna["id"])
        out += not self.test_zad_pyt(lecture_parts["zad_pyt"])
        out += not self.test_zad_dom(lecture_parts["zad_dom"])

        self.indent = 0
        if out > 0:
            self._send_msg(self.ERROR, "Test nie przeszedł etapu 2 - walidacja zawartości lekcji.\n")
            return
        else:
            self._send_msg(self.OKAY, "Test przeszedł etap 2 - walidacja zawartości lekcji.\n")

    # ---------------------- testing methods below ---------------------------------------------

    def test_konwencje_nazwowe(self, lectures) -> dict | None:
        out = {
            "odp_do_zad_dom": None,
            "zeszyt_cw": None,
            "quiz_przed": None,
            "nagranie": [],
            "quiz_po": None,
            "qna": [],
            "zad_pyt": None,
            "zad_dom": None,
            "inne": []
        }
        names = {
            "odp_do_zad_dom": "Odpowiedzi do zadania domowego z modu\u0142u [0-9]+",
            "zeszyt_cw": "Zeszyt ćwiczeń",
            "quiz_przed": "Sprawdź siebie",
            "nagranie": "[0-9]+\.[0-9]+ .+",
            "quiz_po": "Quiz po zajęciach",
            "qna": "[0-9]+\.[0-9]+ Q&A",
            "zad_pyt": "Zadaj pytanie",
            "zad_dom": "Zadanie domowe"
        }
        names_keys = list(names.keys())

        start_i = 0
        while (
                not re.match(names["odp_do_zad_dom"], lectures[start_i]["lecture"]["name"])
                and not re.match(names["zeszyt_cw"], lectures[start_i]["lecture"]["name"])
        ):
            self._send_msg(self.WARNING,
                           f"Nieznana lekcja na pozycji {start_i}: {lectures[start_i]['lecture']['name']}")
            start_i += 1

        # ODPOWIEDZI DO POPRZEDNIEGO MODUŁU
        name_index = 1
        if re.match(names["odp_do_zad_dom"], lectures[start_i]["lecture"]["name"]):
            self._send_msg(self.OKAY, f"\"{lectures[start_i]['lecture']['name']}\" istnieje.")
            out["odp_do_zad_dom"] = lectures[start_i]["lecture"]
        else:
            self._send_msg(self.WARNING, f"Brak odpowiedzi do zadania domowego z poprzedniego modułu.")

        # PRZED NAGRANIAMI
        while names_keys[name_index] != "nagranie":
            if not re.match(names[names_keys[name_index]], lectures[start_i + name_index]["lecture"]["name"]):
                self._send_msg(self.ERROR,
                               f"Brak odpowiedniej lekcji (regex: \"{names[names_keys[name_index]]}\") - błąd w {lectures[start_i + name_index]['lecture']['name']} ")
                return None
            self._send_msg(self.OKAY, f"\"{lectures[start_i + name_index]['lecture']['name']}\" istnieje.")
            out[names_keys[name_index]] = lectures[start_i + name_index]["lecture"]
            name_index += 1

        # NAGRANIA (nie QNA)
        video_exists = False
        while True:
            if not re.match(names[names_keys[name_index]], lectures[start_i + name_index]["lecture"]["name"]):
                if not re.match(names[names_keys[name_index + 1]],
                                lectures[start_i + name_index]["lecture"]["name"]) or not video_exists:
                    self._send_msg(self.ERROR,
                                   f"Brak odpowiedniej lekcji (regex: \"{names[names_keys[name_index]]}\") - błąd w {lectures[start_i + name_index]['lecture']['name']} ")
                    return None
                else:
                    name_index += 1
                    start_i -= 1
                    break
            self._send_msg(self.OKAY, f"\"{lectures[start_i + name_index]['lecture']['name']}\" istnieje.")
            out[names_keys[name_index]].append(lectures[start_i + name_index]["lecture"])
            video_exists = True
            start_i += 1

        # QUIZ PO
        if not re.match(names[names_keys[name_index]], lectures[start_i + name_index]["lecture"]["name"]):
            self._send_msg(self.ERROR,
                           f"Brak odpowiedniej lekcji (regex: \"{names[names_keys[name_index]]}\") - błąd w {lectures[start_i + name_index]['lecture']['name']} ")
            return None
        self._send_msg(self.OKAY, f"\"{lectures[start_i + name_index]['lecture']['name']}\" istnieje.")
        out[names_keys[name_index]] = lectures[start_i + name_index]["lecture"]
        name_index += 1

        # NAGRANIA QNA
        while True:
            if not re.match(names[names_keys[name_index]], lectures[start_i + name_index]["lecture"]["name"]):
                if not re.match(names[names_keys[name_index + 1]], lectures[start_i + name_index]["lecture"]["name"]):
                    self._send_msg(self.ERROR,
                                   f"Brak odpowiedniej lekcji (regex: \"{names[names_keys[name_index]]}\") - błąd w {lectures[start_i + name_index]['lecture']['name']} ")
                    return None
                else:
                    name_index += 1
                    start_i -= 1
                    break
            self._send_msg(self.OKAY, f"\"{lectures[start_i + name_index]['lecture']['name']}\" istnieje.")
            out[names_keys[name_index]].append(lectures[start_i + name_index]["lecture"])
            start_i += 1

        # CAŁA RESZTA
        while name_index < len(names_keys):
            if not re.match(names[names_keys[name_index]], lectures[start_i + name_index]["lecture"]["name"]):
                self._send_msg(self.ERROR,
                               f"Brak odpowiedniej lekcji (regex: \"{names[names_keys[name_index]]}\") - błąd w {lectures[start_i + name_index]['lecture']['name']} ")
                return None
            self._send_msg(self.OKAY, f"\"{lectures[start_i + name_index]['lecture']['name']}\" istnieje.")
            out[names_keys[name_index]] = lectures[start_i + name_index]["lecture"]
            name_index += 1

        # WSZYSTKO DODATKOWE
        while start_i + name_index < len(lectures):
            self._send_msg(self.WARNING,
                           f"\"{lectures[start_i + name_index]['lecture']['name']}\" istnieje jako dodatkowa lekcja.")
            out["inne"].append(lectures[start_i + name_index]["lecture"])
            name_index += 1
        return out

    def test_answers_for_hw(self, content: dict | None) -> bool:
        if content is None:
            return True
        for att in content["attachments"]:
            if self._check_for_pdf(att):
                self._send_msg(self.OKAY, "Odpowiedzi do zadania domowego - zawartość prawidłowa.")
                return True
        self._send_msg(self.ERROR, "Odpowiedzi do zadania domowego - brak PDF z odpowiedziami.")
        return False

    def test_workbook(self, content: dict) -> bool:
        if content is None:
            return True
        for att in content["attachments"]:
            if self._check_for_pdf(att):
                self._send_msg(self.OKAY, "Odpowiedzi do zadania domowego - zawartość prawidłowa.")
                return True
        self._send_msg(self.ERROR, "Odpowiedzi do zadania domowego - brak PDF z odpowiedziami.")
        return False

    def test_quiz_before(self, content: dict) -> bool:
        for att in content["attachments"]:
            if self._check_for_valid_quiz(att):
                self._send_msg(self.OKAY, "Quiz przed zajęciami - zawartość prawidłowa.")
                return True
        self._send_msg(self.ERROR, "Quiz przed zajęciami - brak poprawnie ustawionego quizu.")
        return False

    def test_video(self, content: dict, course_id: int, lecture_id: int) -> bool:
        for att in content["attachments"]:
            if self._check_for_valid_video(att, course_id, lecture_id):
                self._send_msg(self.OKAY, f"{content['name']} - zawartość prawidłowa.")
                return True
        self._send_msg(self.ERROR, f"{content['name']} - brak nagrania lub thumbnail.")
        return False

    def test_quiz_after(self, content: dict) -> bool:
        for att in content["attachments"]:
            if self._check_for_valid_quiz(att):
                self._send_msg(self.OKAY, "Sprawdź siebie - zawartość prawidłowa.")
                return True
        self._send_msg(self.ERROR, "Sprawdź siebie - brak poprawnie ustawionego quizu.")
        return False

    def test_qna(self, content: dict, course_id: int, lecture_id: int) -> bool:
        for att in content["attachments"]:
            if self._check_for_valid_video(att, course_id, lecture_id) or self._check_for_valid_textandimages(att) or self._check_for_pdf(att):
                self._send_msg(self.OKAY, f"{content['name']} - zawartość prawidłowa.")
                return True
        self._send_msg(self.ERROR, f"{content['name']} - brak dodanego nagrania, tekstu lub PDF.")
        return False

    def test_zad_pyt(self, content: dict) -> bool:
        for att in content["attachments"]:
            if self._check_for_valid_gform_cc(att):
                self._send_msg(self.OKAY, "Zadaj pytanie - zawartość prawidłowa.")
                return True
        self._send_msg(self.ERROR, "Zadaj pytanie - brak dodanego formularza Google Forms.")
        return False

    def test_zad_dom(self, content: dict) -> bool:
        for att in content["attachments"]:
            if self._check_for_valid_textandimages(att) and att["text"].find("https://docs.google.com/forms/d/e/") != -1:
                self._send_msg(self.OKAY, "Zadanie domowe - zawartość prawidłowa.")
                return True
        self._send_msg(self.ERROR, "Zadanie domowe - brak dodanego tekstu lub prawidłowego linku.")
        return False

    # ---------------------- testing methods above ---------------------------------------------

    def _check_for_valid_gform_cc(self, att: dict) -> bool:
        return att["kind"] == "code_embed" and att["text"].startswith('<iframe src="https://docs.google.com/forms/d/e/')

    def _check_for_valid_textandimages(self, att: dict) -> bool:
        return att["kind"] == "text" and len(att["text"]) > 0

    def _check_for_valid_video(self, att: dict, course_id: int, lecture_id: int) -> bool:
        if att["kind"] != "video":
            return False
        vid_data = self.teachable.get_video_data(course_id, lecture_id, att["id"])
        with open(f"{att['name']}.json", "w+") as f:
            json.dump(vid_data, f, indent=2)
        return vid_data["video"]["url_thumbnail"] is not None

    def _check_for_valid_quiz(self, att: dict) -> bool:
        return att["kind"] == "quiz" and len(att["quiz"]["questions"]) > 0

    def _check_for_pdf(self, att: dict) -> bool:
        return att["kind"] == "pdf_embed" and att["url"] is not None and att["file_extension"] == "pdf"

    def _send_msg(self, _type: str, msg: str) -> None:
        assert (_type in (self.RUNNING, self.ERROR, self.WARNING, self.OKAY))
        print(self.indent * "      ", _type, msg)


if __name__ == "__main__":
    asc = AnalyzeSectionCompletion("/home/igor/Documents/code/py/work_automation/credentials/teachable_key.json")
    asc.run(2362042, "Moduł 7 - Neurologiczne stany nagłe")

"""

Wszystko ma być skrupulatnie i szczegółowo wypisane w liście.
Ma być sprawdzone dla każdego modułu (sekcji):

    0. Konwencje nazwowe (REGULAR EXPRESSION)
        - istnieje co najwyżej jedno "Odpowiedzi do zadania domowego z modułu [0-9]+"
        - istnieje dokładnie jedno "Zeszyt ćwiczeń"
        - istnieje dokładnie jedno "Sprawdź siebie"
        - istnieje co najmniej jedno "[0-9]+\.[0-9]+ .+"
        - istnieje dokładnie jedno "Quiz po zajęciach"
        - istnieje dowolna ilość "[0-9]+\.[0-9]+ Q&A"
        - istnieje dokładnie jedno "Zadaj pytanie"
        - istnieje dokładnie jedno "Zadanie domowe"
        - istnieje dowolna ilość dodatkowych lekcji - wypisz
        - wszystkie lekcje są w podanej powyżej kolejności
        
    UWAGA:  Konwencje nazwowe muszą być spełnione przed 
            przystąpieniem do kolejnych kroków testu.
            Tester wie z jaką lekcją ma do czynienia 
            na podstawie nazwy.

    1. Odpowiedzi do zadania domowego z poprzedniego modułu
        - czy istnieje (nie istnieje tylko w module pierwszym)
        - czy ma dodany plik PDF
        
    2. Zeszyt ćwiczeń aktualnego modułu
        - czy istnieje
        - czy ma dodany plik PDF
        
    3. Quiz przed zajęciami
        - czy istnieje
        - czy ma dodany Quiz
        - czy Quiz ma dodane co najmniej jedno pytanie
        
    4. Nagrania wideo
        - czy istnieje conajmniej jedno
        - czy do każdego nagrania dodane jest co najmniej jedno Video
        - czy każde Video ma dodany thumbnail
        
    5. Quiz po zajęciach
        - czy istnieje
        - czy ma dodany Quiz
        - czy Quiz ma dodane co najmniej jedno pytanie

    6. Q&A (jeżeli istnieje)
        - czy ma dodane Video lub Text & Images lub PDF
    
    7. Zadaj pytanie
        - czy istnieje
        - czy ma dodany Custom Code
        - czy Custom Code ma dodany embed typu Google Forms
          (czy rozpoczyna się: <iframe src="https://docs.google.com/forms/d/e/)
        
    8. Zadanie domowe
        - czy istnieje
        - czy ma dodany Text & Images
        - czy Text & Images ma dodany link typu Google Forms 
          (czy zawiera: https://docs.google.com/forms/d/e/)
"""
