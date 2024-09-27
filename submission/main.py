import ipywidgets as widgets
from IPython.display import display, clear_output, Markdown
import types
import inspect
import json


class Submission:
    def __init__(self):
        with open('https://raw.githubusercontent.com/nauqh/cspyexamclient/refs/heads/master/submission/questions.json', 'r') as file:
            self.questions = json.load(file)
        self.answers = [{'question': q['question'], 'answer': ''}
                        for q in self.questions]

    def generate_question(self, q_index: int):
        """Generates and displays a question form for the user to answer.

        Args:
            q_index (int): The index of the question to be displayed.

        Workflow:
        - Retrieve the question and answer using the provided index.
        - Create an output widget for feedback and define `submit_answer` and `reset_answer` functions.
        - Display the question content using Markdown.
        - Create the appropriate answer field widget and configure submit and reset buttons.
        - Attach functions to buttons and display the answer field, buttons, and output widget.
        """
        output = widgets.Output()
        question = self.questions[q_index]
        answer = self.answers[q_index]['answer']

        def submit_answer(btn):
            with output:
                clear_output()
                answer = answer_field.value

                if not answer:
                    print("Please enter your answer.")
                    return

                answer = answer.strip() if isinstance(
                    answer, str) else ','.join(answer)
                self.answers[q_index]['answer'] = answer
                self.validate_answer(answer)

                btn.description = "Submit"
                btn.disabled = False

        def reset_answer(btn):
            with output:
                clear_output()
            self.answers[q_index]['answer'] = ''
            if isinstance(answer_field, widgets.Textarea):
                answer_field.value = ''
            elif isinstance(answer_field, widgets.RadioButtons):
                answer_field.value = None
            elif isinstance(answer_field, widgets.SelectMultiple):
                answer_field.value = []

        # Answer field based on question type
        answer_field = self.create_answer_field(question, answer)

        # Buttons for submit and reset actions
        btn_submit = widgets.Button(
            description="Submit", button_style='success', tooltip='Submit'
        )
        btn_reset = widgets.Button(
            description="Reset answer", tooltip='Reset answer'
        )
        btn_submit.on_click(submit_answer)
        btn_reset.on_click(reset_answer)

        display(Markdown(question['question']))
        display(answer_field)
        display(widgets.HBox([btn_submit, btn_reset]))
        display(output)

    def create_answer_field(self, question: dict, answer: dict):
        """
        Create answer field based on question type.
        """
        result_type = question['resultType']
        choices = question.get('choices', [])

        if result_type in ['VALUE', 'SQL', 'EXPRESSION', 'FUNCTION']:
            return widgets.Textarea(
                value=answer if answer else '',
                placeholder='Enter your answer here...',
                layout=widgets.Layout(height='300px', width='600px')
            )
        elif result_type == 'MULTICHOICE_SINGLE':
            return widgets.RadioButtons(
                options=choices,
                value=answer if answer else None,
                description='Your answer:'
            )
        elif result_type == 'MULTICHOICE_MANY':
            return widgets.SelectMultiple(
                options=choices,
                value=answer.split(',') if answer else [],
                description='Your answer:'
            )

    def validate_answer(self, answer):
        if isinstance(answer, types.FunctionType):
            answer = inspect.getsource(answer)
        print(f'Your answer is:\n{answer}')


submission = Submission()
submission.generate_question(0)
