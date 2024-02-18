from google.gforms import GForms
from google.gdocs import GDocs
from modules.script import Script


class FormsToDocsScript(Script):
    def __init__(self, scopes, token_path, client_secrets_path):
        super().__init__(scopes, token_path, client_secrets_path)
        self.gf = GForms(self.SCOPES)
        self.gd = GDocs(self.SCOPES)
        self.gf.authorize(self.token_path, self.client_secrets_path)
        self.gd.authorize(self.token_path, self.client_secrets_path)

    def run(self, form_id: str, docs_id: str, use_numeration: bool, numeration_start: int):
        try:
            assert (len(form_id) == 44)
            assert (len(docs_id) == 44)
        except AssertionError:
            raise ValueError(f"Invalid Forms ID or Docs ID:\nForms ID: \"{form_id}\"\nDocs ID: \"{docs_id}\" ")

        form = self.gf.get_form_data(form_id)
        form["items"].reverse()
        requests = []
        index = numeration_start - 1

        def add_as_insert_text(t):
            requests.append(
                {
                    'insertText': {
                        'location': {
                            'index': 1,
                        },
                        'text': t
                    }
                }
            )

        def make_bold(t):
            if len(t) == 0:
                return
            requests.append(
                {
                    'updateTextStyle': {
                        'range': {
                            'startIndex': 1,
                            'endIndex': 1 + len(t)
                        },
                        'textStyle': {
                            'bold': True,
                        },
                        'fields': 'bold'
                    }
                }
            )

        def make_unbold(t):
            if len(t) == 0:
                return
            requests.append(
                {
                    'updateTextStyle': {
                        'range': {
                            'startIndex': 1,
                            'endIndex': 1 + len(t)
                        },
                        'textStyle': {
                            'bold': False,
                        },
                        'fields': 'bold'
                    }
                }
            )

        # liczenie pytań z odpowiedziami
        for q in form["items"]:
            if ('questionItem' in q
                    and 'question' in q['questionItem']
                    and 'choiceQuestion' in q['questionItem']['question']):
                index += 1

        for q in form["items"]:
            answers = False

            # czy pytanie zawiera odpowiedzi?
            if ('questionItem' in q
                    and 'question' in q['questionItem']
                    and 'choiceQuestion' in q['questionItem']['question']):
                answers = True

            # odpowiedzi i prawidłowa odpowiedź
            text = ""
            cor_ans_txt = ""
            if answers:
                qa = q['questionItem']['question']['choiceQuestion']
                for j, a in enumerate(qa["options"]):
                    text += f"  {self.ALPHABET[j]}. {a['value']}\n"
                    try:
                        # this is stupid but it works
                        for ca in q['questionItem']['question']['grading']['correctAnswers']['answers']:
                            print(ca, a)
                            if ca == a:
                                cor_ans_txt += self.ALPHABET[j] + " "
                                break
                    except KeyError:
                        pass
                cor_ans_txt += "\n\n"
                add_as_insert_text(cor_ans_txt)
                make_bold(cor_ans_txt)
                text += "\nPrawidłowa odpowiedź: "
                add_as_insert_text(text)
                make_unbold(text)

            # tytuł pytania
            try:
                text = f"{q['title']}\n\n"
                add_as_insert_text(text)
                if answers:
                    make_bold(text)
                else:
                    make_unbold(text)
            except KeyError:
                pass

            # numer pytania
            if answers and use_numeration:
                text = f"{index}. "
                add_as_insert_text(text)
                make_bold(text)
                index -= 1
                make_bold(text)

        self.gd.insert_into_document(docs_id, requests)
