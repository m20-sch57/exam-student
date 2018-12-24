"""
Contains all widgets for long question.
"""


from PyQt5 import Qt
from question_base import QuestionBase
import common


class QuestionLong(QuestionBase):
    """
    Returns widget for long question.
    """
    def __init__(self, parent, check_function, view_question_function):
        super().__init__(parent)
        answer = self.question_data['answer']
        if answer is False:
            answer = ''

        statement_label = Qt.QLabel(self.question_data['statement'])
        statement_label.setFont(Qt.QFont('Arial', 20))
        statement_label.setWordWrap(True)

        self.status_label = Qt.QLabel()
        self.status_label.setFont(Qt.QFont('Arial', 20))

        answer_input = Qt.QPlainTextEdit()
        answer_input.setFont(Qt.QFont('Arial', 20))
        answer_input.setPlainText(answer)
        answer_input.textChanged.connect(
            lambda: self.update_saved_status(answer, answer_input.toPlainText()))
        if self.question_data['answer'] is not False:
            self.update_saved_status(answer, answer_input.toPlainText())

        save_button = Qt.QPushButton('Сохранить')
        save_button.setFont(Qt.QFont('Arial', 20))
        save_button.clicked.connect(
            lambda: check_function(parent.exam, parent.question, answer_input.toPlainText()))

        next_button = Qt.QPushButton('Далее')
        next_button.setFont(Qt.QFont('Arial', 20))
        next_button.clicked.connect(
            lambda: view_question_function(parent.exam, parent.question + 1))

        save_layout = Qt.QHBoxLayout()
        save_layout.addWidget(save_button)
        save_layout.addSpacerItem(Qt.QSpacerItem(20, 0))
        save_layout.addWidget(self.status_label)
        save_layout.addStretch(1)
        if parent.question < len(parent.exam_data):
            save_layout.addSpacerItem(Qt.QSpacerItem(20, 0))
            save_layout.addWidget(next_button)

        self.layout.addWidget(statement_label)
        self.layout.addSpacerItem(Qt.QSpacerItem(0, 10))
        self.layout.addWidget(answer_input)
        self.layout.addSpacerItem(Qt.QSpacerItem(0, 10))
        self.layout.addLayout(save_layout)

    def update_saved_status(self, saved_answer, current_answer):
        """
        Call if current student's answer has changed.
        """
        if saved_answer == current_answer:
            self.status_label.setText('Изменения сохранены')
            self.status_label.setStyleSheet('color: ' + common.GREEN1)
        else:
            self.status_label.setText('Сохраните изменения')
            self.status_label.setStyleSheet('color: ' + common.RED1)


class QuestionLongDetails(QuestionBase):
    """
    Returns widget for details of long question.
    """
    def __init__(self, parent):
        super().__init__(parent)
        current_answer = self.question_data['answer']
        if current_answer is False:
            current_answer = ''
        current_score = self.question_data['score']
        if current_score is False:
            current_score = '0'
        if current_score == '-1':
            current_score = 'Неизв.'
        status = common.get_status(current_score, self.question_data['maxscore'])

        statement_label = Qt.QLabel(self.question_data['statement'])
        statement_label.setFont(Qt.QFont('Arial', 20))
        statement_label.setWordWrap(True)

        answer_input = Qt.QPlainTextEdit()
        answer_input.setFont(Qt.QFont('Arial', 20))
        answer_input.setPlainText(current_answer)
        answer_input.setDisabled(True)

        score_title = Qt.QLabel('Получено баллов:')
        score_title.setFont(Qt.QFont('Arial', 25))
        score_title.setFixedWidth(270)

        score_label = Qt.QLabel(current_score + ' (' + self.question_data['maxscore'] + ')')
        score_label.setFont(Qt.QFont('Arial', 20))
        score_label.setStyleSheet('color: ' + status['color'])

        score_layout = Qt.QHBoxLayout()
        score_layout.addWidget(score_title)
        score_layout.addSpacerItem(Qt.QSpacerItem(20, 0))
        score_layout.addWidget(score_label)
        score_layout.addStretch(1)

        self.layout.addWidget(statement_label)
        self.layout.addSpacerItem(Qt.QSpacerItem(0, 10))
        self.layout.addWidget(answer_input)
        self.layout.addSpacerItem(Qt.QSpacerItem(0, 10))
        self.layout.addLayout(score_layout)
