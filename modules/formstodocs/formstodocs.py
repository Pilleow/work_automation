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

    def run(self, form_id: str, docs_id: str):
        try:
            assert (len(form_id) == 44)
            assert (len(docs_id) == 44)
        except AssertionError:
            raise ValueError(f"Invalid Forms ID or Docs ID:\nForms ID: \"{form_id}\"\nDocs ID: \"{docs_id}\" ")

        form = self.gf.get_form_data(form_id)
        form["items"].reverse()
        requests = []
        index = 0

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
            correct_answers = {}

            # czy pytanie zawiera odpowiedzi?
            if ('questionItem' in q
                    and 'question' in q['questionItem']
                    and 'choiceQuestion' in q['questionItem']['question']):
                answers = True

            # tworzenie listy prawidłowych odpowiedzi
            if (answers
                    and 'questionItem' in q
                    and 'question' in q['questionItem']
                    and 'grading' in q['questionItem']['question']
                    and 'correctAnswers' in q['questionItem']['question']['grading']
                    and 'answers' in q['questionItem']['question']['grading']['correctAnswers']):
                for i, a in enumerate(q['questionItem']['question']['grading']['correctAnswers']['answers']):
                    correct_answers[a['value']] = self.ALPHABET[i]

            # odpowiedzi i prawidłowa odpowiedź
            text = ""
            cor_ans_txt = ""
            if answers:
                qa = q['questionItem']['question']['choiceQuestion']
                for j, a in enumerate(qa["options"]):
                    text += f"  {self.ALPHABET[j]}. {a['value']}\n"
                    if a['value'] in correct_answers:
                        cor_ans_txt += correct_answers[a['value']] + " "
                cor_ans_txt += "\n\n"
                add_as_insert_text(cor_ans_txt)
                make_bold(cor_ans_txt)
                text += "\nPrawidłowa odpowiedź: "
                add_as_insert_text(text)
                make_unbold(text)

            # tytuł pytania
            text = f"{q['title']}\n\n"
            add_as_insert_text(text)
            if answers:
                make_bold(text)
            else:
                make_unbold(text)

            # numer pytania
            if answers:
                text = f"{index}. "
                add_as_insert_text(text)
                make_bold(text)
                index -= 1
                make_bold(text)

        self.gd.insert_into_document(docs_id, requests)
