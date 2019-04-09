"""
Page to display the results table of the exam.
"""


from PyQt5 import Qt
import common


def get_sums(results_table):
    """
    Returns results table sorted by sum.
    """
    sums = [0] * len(results_table)
    for i in range(len(results_table)):
        for j in range(len(results_table[i])):
            sums[i] += results_table[i][j]['score'] if results_table[i][j] else 0
    return sums


class ResultsPage(Qt.QWidget):
    """
    Page to display the results table of the exam.
    """
    def __init__(self, app, exam_id, users, questions_ids, results_table):
        super().__init__()
        sums = get_sums(results_table)
        order = sorted([i for i in range(len(users))], key=lambda i: sums[i], reverse=True)
        users = [users[i] for i in order]
        sums = [sums[i] for i in order]
        questions_ids = questions_ids
        results_table = [results_table[i] for i in order]

        back_button = Qt.QPushButton(Qt.QIcon(common.LEFT), '', self)
        back_button.setObjectName('Flat')
        back_button.setCursor(Qt.Qt.PointingHandCursor)
        back_button.setIconSize(Qt.QSize(35, 35))
        back_button.clicked.connect(lambda: app.display_exam(exam_id))

        results_title = Qt.QLabel('Таблица результатов', self)
        results_title.setFont(Qt.QFont('Arial', 30))

        update_button = Qt.QPushButton(Qt.QIcon(common.UPDATE), '', self)
        update_button.setObjectName('Flat')
        update_button.setCursor(Qt.Qt.PointingHandCursor)
        update_button.setIconSize(Qt.QSize(35, 35))
        update_button.clicked.connect(lambda: app.display_results_page(exam_id))

        scroll_area = Qt.QScrollArea()
        scroll_area.setFrameShape(Qt.QFrame.NoFrame)

        grid_layout = Qt.QGridLayout()
        grid_layout.setSpacing(0)

        user_column = Qt.QLabel('Участник', self)
        user_column.setFont(Qt.QFont('Arial', 20))
        user_column.setAlignment(Qt.Qt.AlignCenter)
        user_column.setStyleSheet('padding: 10px')
        grid_layout.addWidget(user_column, 0, 0)

        sum_column = Qt.QLabel('Сумма', self)
        sum_column.setFont(Qt.QFont('Arial', 20))
        sum_column.setAlignment(Qt.Qt.AlignCenter)
        sum_column.setStyleSheet('padding: 10px')
        grid_layout.addWidget(sum_column, 0, 1)

        for j in range(len(questions_ids)):
            question_column = Qt.QLabel(str(j + 1), self)
            question_column.setFont(Qt.QFont('Arial', 20))
            question_column.setAlignment(Qt.Qt.AlignCenter)
            question_column.setStyleSheet('padding: 10px')
            grid_layout.addWidget(question_column, 0, j + 2)

        for i in range(len(users)):
            user_row = Qt.QLabel(users[i]['name'], self)
            user_row.setFont(Qt.QFont('Arial', 20))
            user_row.setAlignment(Qt.Qt.AlignCenter)
            user_row.setStyleSheet('padding: 10px')
            grid_layout.addWidget(user_row, i + 1, 0)

            sum_cell = Qt.QLabel(str(sums[i]), self)
            sum_cell.setFont(Qt.QFont('Arial', 20))
            sum_cell.setAlignment(Qt.Qt.AlignCenter)
            sum_cell.setStyleSheet('padding: 10px')
            grid_layout.addWidget(sum_cell, i + 1, 1)

        for i in range(len(results_table)):
            for j in range(len(questions_ids)):
                question_details = common.get_question_details(results_table[i][j])
                question_style = common.main_question_style(results_table[i][j])

                cell = Qt.QPushButton(question_details['score'], self)
                cell.setObjectName('Flat')
                cell.setCursor(Qt.Qt.PointingHandCursor)
                cell.setFont(Qt.QFont('Arial', 15))
                cell.setStyleSheet('color: ' + question_style['main_color'])
                cell.clicked.connect(common.return_lambda(
                    app.display_student_answer_page, exam_id, questions_ids[j], users[i]['rowid']))
                grid_layout.addWidget(cell, i + 1, j + 2)

        scroll_widget = Qt.QWidget(self)
        scroll_widget.setLayout(grid_layout)
        scroll_area.setWidget(scroll_widget)

        upper_layout = Qt.QHBoxLayout()
        upper_layout.addWidget(back_button)
        upper_layout.addStretch(1)
        upper_layout.addWidget(results_title)
        upper_layout.addStretch(1)
        upper_layout.addWidget(update_button)

        layout = Qt.QVBoxLayout()
        layout.addLayout(upper_layout)
        layout.addSpacerItem(Qt.QSpacerItem(0, 40))
        layout.addWidget(scroll_area)
        self.setLayout(layout)
