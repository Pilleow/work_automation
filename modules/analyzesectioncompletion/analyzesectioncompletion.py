import re
import os
import time
import json
from PIL import Image
from tqdm import tqdm

from modules.script import Script
from teachable.teachable import Teachable
from misc.terminalcolors import ANSITerminalColors as ANSI


class NameContainer:
    ANY = -1
    ONE = 1
    SEND_WARNING = 10000
    SEND_ERROR = 10001

    def __init__(self, regex: str, count: int, on_missing: int = SEND_ERROR, display_name: str | None = None):
        self.regex = regex
        self.count = count
        self.on_missing = on_missing
        self.strings_matched = 0
        self.display_name = display_name
        if display_name is None:
            self.display_name = self.regex

    def compare(self, s: str) -> bool:
        if re.fullmatch(self.regex.strip(), s.strip()):
            self.strings_matched += 1
            return True
        return False

    def found_all(self) -> bool:
        return self.strings_matched == self.count or (self.count is self.ANY and self.strings_matched > 0)

    def send_message(self):
        if self.found_all():
            AnalyzeSectionCompletion.send_msg(
                1,
                AnalyzeSectionCompletion.OKAY,
                f"'{self.display_name}' znaleziony ({self.strings_matched})."
            )
        elif self.strings_matched > 0:
            AnalyzeSectionCompletion.send_msg(
                1,
                AnalyzeSectionCompletion.ERROR if self.on_missing is self.SEND_ERROR else AnalyzeSectionCompletion.WARNING,
                f"'{self.display_name}' występuje nieprawidłową ilość razy ({self.strings_matched} znalezione, {self.count} powinno)."
            )
        else:
            AnalyzeSectionCompletion.send_msg(
                1,
                AnalyzeSectionCompletion.ERROR if self.on_missing is self.SEND_ERROR else AnalyzeSectionCompletion.WARNING,
                f"'{self.display_name}' nie znaleziony. REGEX: {self.regex}"
            )


class AnalyzeSectionCompletion(Script):
    RUNNING = f"{ANSI.OKBLUE}[⚙]{ANSI.ENDC}  "
    OKAY = f"{ANSI.OKGREEN}[✓]{ANSI.ENDC}  "
    WARNING = f"{ANSI.WARNING}[?]{ANSI.ENDC}  "
    ERROR = f"{ANSI.FAIL}[✗]{ANSI.ENDC}  "
    WARNINGPOINT = f"{ANSI.WARNING} > {ANSI.ENDC}  "
    RATE_LIMIT_DELAY_SLEEP = 0.2  # https://docs.teachable.com/docs/rate-limits-1

    def __init__(self, teachable_key_path: str, scopes=(), token_path=""):
        super().__init__(scopes, token_path, teachable_key_path)
        self._thumbnails = {}
        self.teachable = Teachable()
        self.teachable.authorize(teachable_key_path)
        self.indent = 0
        self.names = {}
        self.valid_order = []

    def reinit_valid_names(self):
        self.names = {
            "odp_do_zad_dom": NameContainer("Odpowiedzi do zadania domowego z modu\u0142u [0-9]+", NameContainer.ONE, NameContainer.SEND_WARNING, display_name="Odpowiedzi do zadania domowego"),
            "zeszyt_cw": NameContainer("Zeszyt ćwiczeń", NameContainer.ONE),
            "quiz_przed": NameContainer("Sprawdź siebie", NameContainer.ONE),
            "qna": NameContainer("[0-9]+\.[0-9]+ Q&A", NameContainer.ANY, NameContainer.SEND_WARNING, display_name="Q&A"),
            "nagranie": NameContainer("[0-9]+\.[0-9]+ .+", NameContainer.ANY, display_name="Nagrania kursu"),
            "quiz_po": NameContainer("Quiz po zajęciach", NameContainer.ONE),
            "zad_pyt": NameContainer("Zadaj pytanie", NameContainer.ONE),
            "zad_dom": NameContainer("Zadanie domowe", NameContainer.ONE)
        }
        self.valid_order = [
            "odp_do_zad_dom",
            "zeszyt_cw",
            "quiz_przed",
            "nagranie",
            "quiz_po",
            "qna",
            "zad_pyt",
            "zad_dom"
        ]

    def run(self, course_id: int, section_name: str):
        self.reinit_valid_names()
        self.indent = 0
        self._thumbnails.clear()
        response = self.teachable.get_course(course_id)
        os.system('cls' if os.name == 'nt' else 'clear')
        print(" ", flush=True)
        self.send_msg(0, self.RUNNING, f"Skrypt Analyze Section Completion uruchomiony.\n")
        self.send_msg(0, self.OKAY, f"Załadowano kurs: {response['course']['name']}")
        section = list(filter(
            lambda item: item["name"].strip() == section_name,
            response["course"]["lecture_sections"]
        ))
        if len(section) == 0:
            self.send_msg(0, self.ERROR, f"Nie znaleziono sekcji o nazwie: {section_name}.")
            return
        section = section[0]
        self.send_msg(0, self.OKAY, f"Załadowano sekcję: {section_name}")

        lecture_data = []
        print()
        t_start = 0
        t_end = 0
        for lecture in tqdm(section["lectures"], colour="white", ncols=90, desc="Pobieranie danych o sekcjach", total=len(section["lectures"])):
            time.sleep(max(0.0, self.RATE_LIMIT_DELAY_SLEEP - (t_end - t_start)))
            t_start = time.time()
            lecture_data.append(self.teachable.get_lecture(course_id, lecture["id"]))
            t_end = time.time()
        print()

        # ------------------ etap 1 ------------------------

        self.send_msg(0, self.RUNNING, "Start etapu 1 - konwencje nazwowe.")
        self.indent = 1
        lecture_parts, order = self.test_konwencje_nazwowe(lecture_data)
        self.indent = 0
        if lecture_parts is None or not self.is_valid_order(order):
            self.send_msg(0, self.ERROR, "Test nie przeszedł etapu 1 - konwencje nazwowe.\n")
            return
        else:
            self.send_msg(0, self.OKAY, "Test przeszedł etap 1 - konwencje nazwowe.\n")

        # ------------------ etap 2 ------------------------

        self.send_msg(0, self.RUNNING, "Start etapu 2 - walidacja zawartości lekcji.")
        self.indent = 1

        out = 0
        out += not self.test_answers_for_hw(lecture_parts["odp_do_zad_dom"])
        out += not self.test_workbook(lecture_parts["zeszyt_cw"])
        out += not self.test_quiz_before(lecture_parts["quiz_przed"])
        for vid in lecture_parts["nagranie"]:
            out += not self.test_video(vid, course_id, vid["id"])
        out += not self.test_quiz_after(lecture_parts["quiz_po"])
        for qna in lecture_parts["qna"]:
            out += not self.test_qna(qna, course_id, qna["id"])
        out += not self.test_zad_pyt(lecture_parts["zad_pyt"])
        out += not self.test_zad_dom(lecture_parts["zad_dom"])

        try:
            os.remove("_temp_thumb.png")
        except FileNotFoundError:
            pass

        if len(self._thumbnails) > 1:
            print()
            self.send_msg(1, self.WARNING, "Wykryto podejrzane thumbnail. Sprawdź nagrania:")
            max_length_list = list(self._thumbnails.keys())[0]
            for thumb_list in self._thumbnails:
                if len(self._thumbnails[thumb_list]) > len(self._thumbnails[max_length_list]):
                    max_length_list = thumb_list
            if len(self._thumbnails[max_length_list]) == 1:
                max_length_list = None
            for thumb_list in self._thumbnails:
                if thumb_list is max_length_list:
                    continue
                for name in self._thumbnails[thumb_list]:
                    self.send_msg(1, self.WARNINGPOINT, name)
            print()

        self.indent = 0
        if out > 0:
            self.send_msg(0, self.ERROR, "Test nie przeszedł etapu 2 - walidacja zawartości lekcji.\n")
            return
        else:
            self.send_msg(0, self.OKAY, "Test przeszedł etap 2 - walidacja zawartości lekcji.\n")

    # ---------------------- testing methods below ---------------------------------------------

    def test_konwencje_nazwowe(self, lectures) -> list | None:

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
        order = []
        errored = False
        names_keys = list(self.names.keys())

        # --------------------------------------------------------------------------------------------------------

        for lec in lectures:
            lec_name = lec["lecture"]["name"]
            for key in names_keys:
                if not self.names[key].compare(lec_name):
                    continue
                if type(out[key]) is list:
                    out[key].append(lec["lecture"])
                    order.append(key)
                else:
                    out[key] = lec["lecture"]
                    order.append(key)
                break
            else:
                self.send_msg(1, self.WARNING, f"`{lec_name}` istnieje jako dodatkowa lekcja.")
                out["inne"].append(lec["lecture"])

        print()

        for key in names_keys:
            if not self.names[key].found_all() and self.names[key].on_missing is NameContainer.SEND_ERROR:
                errored = True
            self.names[key].send_message()

        # --------------------------------------------------------------------------------------------------------

        if errored:
            return [None, None]
        return [out, order]

    def is_valid_order(self, raw_order: list) -> bool:
        msg = lambda m: self.send_msg(1, self.ERROR, m)
        order = []
        for lec in raw_order:
            if lec not in order:
                order.append(lec)
        valid_order = self.valid_order.copy()
        i = 0
        if valid_order[0] != order[0]:
            if valid_order[0] != "odp_do_zad_dom":
                msg(f"Nieprawidłowa kolejność: {order[0]}, {valid_order[0]}")
                return False
            else:
                valid_order.pop(0)

        while i < len(valid_order):
            try:
                if order[i] != valid_order[i]:
                    if valid_order[i] == "qna":
                        valid_order.pop(i)
                    else:
                        msg(f"Nieprawidłowa kolejność: {order[i]}, {valid_order[i]}")
                        return False
            except IndexError:
                msg(f"Błąd: {order[i - 1]}")
                return False
            i += 1

        return True

    def test_answers_for_hw(self, content: dict | None) -> bool:
        if content is None:
            return True
        for att in content["attachments"]:
            if self._check_for_pdf(att):
                self.send_msg(1, self.OKAY, "Odpowiedzi do zadania domowego - zawartość prawidłowa.")
                return True
        self.send_msg(1, self.ERROR, "Odpowiedzi do zadania domowego - brak PDF z odpowiedziami.")
        return False

    def test_workbook(self, content: dict) -> bool:
        if content is None:
            return True
        for att in content["attachments"]:
            if self._check_for_pdf(att):
                self.send_msg(1, self.OKAY, "Zeszyt ćwiczeń - zawartość prawidłowa.")
                return True
        self.send_msg(1, self.ERROR, "Zeszyt ćwiczeń - brak PDF.")
        return False

    def test_quiz_before(self, content: dict) -> bool:
        for att in content["attachments"]:
            if self._check_for_valid_quiz(att):
                self.send_msg(1, self.OKAY, "Quiz przed zajęciami - zawartość prawidłowa.")
                return True
        self.send_msg(1, self.ERROR, "Quiz przed zajęciami - brak poprawnie ustawionego quizu.")
        return False

    def test_video(self, content: dict, course_id: int, lecture_id: int) -> bool:
        for att in content["attachments"]:
            if self._check_for_valid_video(att, course_id, lecture_id, content["name"]):
                self.send_msg(1, self.OKAY, f"{content['name']} - zawartość prawidłowa.")
                return True
        self.send_msg(1, self.ERROR, f"{content['name']} - brak nagrania.")
        return False

    def test_quiz_after(self, content: dict) -> bool:
        for att in content["attachments"]:
            if self._check_for_valid_quiz(att):
                self.send_msg(1, self.OKAY, "Sprawdź siebie - zawartość prawidłowa.")
                return True
        self.send_msg(1, self.ERROR, "Sprawdź siebie - brak poprawnie ustawionego quizu.")
        return False

    def test_qna(self, content: dict, course_id: int, lecture_id: int) -> bool:
        for att in content["attachments"]:
            if self._check_for_valid_textandimages(att) or self._check_for_pdf(att) or self._check_for_valid_video(att, course_id, lecture_id, content["name"]):
                self.send_msg(1, self.OKAY, f"{content['name']} - zawartość prawidłowa.")
                return True
        self.send_msg(1, self.ERROR, f"{content['name']} - brak dodanego nagrania, tekstu lub PDF.")
        return False

    def test_zad_pyt(self, content: dict) -> bool:
        for att in content["attachments"]:
            if self._check_for_valid_gform_cc(att):
                self.send_msg(1, self.OKAY, "Zadaj pytanie - zawartość prawidłowa.")
                return True
        self.send_msg(1, self.ERROR, "Zadaj pytanie - brak dodanego formularza Google Forms.")
        return False

    def test_zad_dom(self, content: dict) -> bool:
        for att in content["attachments"]:
            if self._check_for_valid_textandimages(att) and att["text"].find("https://docs.google.com/forms/d/e/") != -1:
                self.send_msg(1, self.OKAY, "Zadanie domowe - zawartość prawidłowa.")
                return True
        self.send_msg(1, self.ERROR, "Zadanie domowe - brak dodanego tekstu lub prawidłowego linku.")
        return False

    # ---------------------- testing methods above ---------------------------------------------

    def _check_for_valid_gform_cc(self, att: dict) -> bool:
        return att["kind"] == "code_embed" and att["text"].startswith('<iframe src="https://docs.google.com/forms/d/e/')

    def _check_for_valid_textandimages(self, att: dict) -> bool:
        return att["kind"] == "text" and len(att["text"]) > 0

    def _check_for_valid_video(self, att: dict, course_id: int, lecture_id: int, lecture_name: str) -> bool:
        # sprawdzenie thumbnail wymaga analizy obrazu!!! nie ma w API pola śledzącego, czy dodano customowy thumbnail
        if att["kind"] != "video":
            return False
        try:
            vid_data = self.teachable.get_video_data(course_id, lecture_id, att["id"])
        except Exception:
            self.send_msg(1, self.ERROR, f"Ładowanie danych nagrania '{lecture_name}' nie powiodło się. Być może jest nadal przetwarzany?")
            return False
        url = vid_data["video"]["url_thumbnail"]
        if url is None:
            return False
        data = self.teachable.get_static_url(url, "_temp_thumb.png")
        img = Image.open('_temp_thumb.png')
        img_width, img_height = img.size
        imgkey = ""
        imgkey += "".join([str(int(v/10) * 10) for v in img.getpixel((img_width // 6, img_height // 6))])  # top left
        imgkey += "".join([str(int(v/10) * 10) for v in img.getpixel((img_width // 6, img_height * 5 // 6))])  # bottom left
        imgkey += "".join([str(int(v/10) * 10) for v in img.getpixel((img_width * 5 // 6, img_height * 5 // 6))])  # bottom right
        if imgkey not in self._thumbnails:
            self._thumbnails[imgkey] = []
        self._thumbnails[imgkey].append(lecture_name)
        return True

    def _check_for_valid_quiz(self, att: dict) -> bool:
        return att["kind"] == "quiz" and len(att["quiz"]["questions"]) > 0

    def _check_for_pdf(self, att: dict) -> bool:
        return att["kind"] == "pdf_embed" and att["url"] is not None and att["file_extension"] == "pdf"

    @staticmethod
    def send_msg(indent: int, _type: str, msg: str) -> None:
        print(indent * "      ", _type, msg)


if __name__ == "__main__":
    asc = AnalyzeSectionCompletion("/home/igor/Documents/code/py/work_automation/credentials/teachable_key.json")
    asc.run(2153124, "MODUŁ 3")

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
