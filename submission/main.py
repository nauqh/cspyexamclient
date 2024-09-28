import ipywidgets as widgets
from IPython.display import display, clear_output, Markdown
import types
import inspect
import json
import requests


class Submission:
    __slots__ = ['questions', 'answers', 'email']

    def __init__(self, exam_url: str):
        response = requests.get(exam_url)
        self.questions = json.loads(response.content.decode('utf-8'))
        self.answers = [{'question': q['question'], 'answer': ''}
                        for q in self.questions]

    def register_student(self):
        def submit_email(btn):
            with output:
                clear_output()
                if (len(email_field.value) == 0) or ('@' not in email_field.value):
                    print("Please enter a valid email")
                    return
                self.email = email_field.value.strip().lower()

                btn.description = "Submitting..."
                btn.disabled = True

                print(f'Welcome {self.email.split("@")[0]}!')
                # first_submit = Submission.create(self.to_json())
                # if (getattr(first_submit, '_id', '')):
                #     if (getattr(first_submit, 'name', '')):
                #         print(f'Welcome {first_submit.name}!')
                #     else:
                #         print(f'Welcome {first_submit.email}')
                # else:
                #     self.email = ''

                btn.description = "Submit"
                btn.disabled = False

        text = widgets.HTML(value='''
            Please enter the email that you used to register for the course.<br />
            <i>Submit again will reset all of your answers and current score!<i>
        ''')

        button = widgets.Button(
            icon='fa-paper-plane', description="Submit", button_style='success', tooltip='Submit')
        email_field = widgets.Text(
            value='',
            placeholder='Email..',
            description='Your email',
            disabled=False
        )
        button.on_click(submit_email)
        output = widgets.Output()

        display(text)
        display(email_field)
        display(button, output)

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
        if not getattr(self, 'email', ''):
            print('Login required')
            print('Please submit your email')
            return

        if isinstance(answer, types.FunctionType):
            answer = inspect.getsource(answer)
        print(f'Your answer is:\n{answer}')

    def display_submission_summary(self):
        """
        Displays a summary of all questions and corresponding user answers in a table format.
        The table has two columns with fixed widths: 30% for the question number and 70% for the answer.
        Includes a 'Submit All' button for final submission.
        """
        output = widgets.Output()

        def submit_all(btn):
            with output:
                clear_output()
                # Check if all questions are answered
                # for idx, answer in enumerate(self.answers):
                #     if not answer['answer']:
                #         print(
                #             f"Please answer question {idx + 1} before submitting.")
                #         return

                # Submission logic placeholder
                print("\nAll answers submitted successfully!")
                btn.description = "Submit All"
                btn.disabled = False

        # Create HTML table with questions and answers, fixed column widths
        table_html = """
        <table style="width:80%; margin: 0 auto;; border-collapse: collapse;" border="1">
            <tr>
                <th style="padding: 8px; text-align: left; width: 20%;">Question</th>
                <th style="padding: 8px; text-align: left; width: 80%;">Your Answer</th>
            </tr>
        """

        for i, answer in enumerate(self.answers):
            question_number = f"Question {i+1}"
            user_answer = answer['answer'] or "No answer provided"
            table_html += f"""
            <tr>
                <td style="padding: 8px; width: 20%;">{question_number}</td>
                <td style="padding: 8px; width: 80%;">{user_answer}</td>
            </tr>
            """

        table_html += "</table>"

        display(widgets.HTML(table_html))

        btn_submit_all = widgets.Button(
            description="Submit All",
            button_style='success',
            tooltip='Submit All',
            layout=widgets.Layout(width='50%')
        )

        button_box = widgets.HBox([btn_submit_all], layout=widgets.Layout(
            justify_content='center',
        ))
        btn_submit_all.on_click(submit_all)

        display(button_box)
        display(output)
