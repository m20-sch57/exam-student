"""
Examiner project, student module.
"""


import sys
import os
import socket
import hashlib
import functools

from PyQt5 import Qt
from client import Client
from settings_page import SettingsPage
from login_page import LoginPage
from register_page import RegisterPage
from home_page import HomePage
from start_exam_page import StartExamPage
from error_widget import ErrorWidget
from exam_page import ExamPage
from exam_status import ExamRunning, ExamFinished
from question_short import QuestionShort, QuestionShortChecked, QuestionShortDetails
from question_long import QuestionLong, QuestionLongDetails


def safe(function):
    """
    Returns safe function.
    """
    @functools.wraps(function)
    def result(self, *args, **kwargs):
        try:
            return function(self, *args, **kwargs)
        except socket.error:
            self.display_settings_page()
            self.widget.set_failed_state()
    return result


class Application(Qt.QApplication):
    """
    Main application class.
    """
    def __init__(self):
        super().__init__(sys.argv)
        self.client = Client()
        self.window = Qt.QWidget()
        self.window.setStyleSheet(open(os.path.join('css', 'common_style.css')).read())
        self.window.setWindowTitle('Школьник')
        self.window.setGeometry(200, 100, 1000, 700)
        self.widget = Qt.QWidget(self.window)
        self.layout = Qt.QHBoxLayout(self.window)
        self.layout.addWidget(self.widget)
        self.window.show()

    def display_widget(self, widget):
        """
        Displays the widget.
        """
        old = self.widget
        old.deleteLater()
        self.layout.removeWidget(old)
        self.layout.addWidget(widget)
        self.widget = widget

    def start(self):
        """
        Starts application.
        """
        self.display_login_page()
        self.exit(self.exec_())

    def check_ip(self, ip_address):
        """
        Checks ip-address of server.
        """
        try:
            self.widget.set_waiting_state()
            self.client.set_item('server', ip_address)
            self.client.update_server()
            self.client.server.ping()
            self.widget.set_succeeded_state()
        except socket.error:
            self.widget.set_failed_state()

    @safe
    def save_settings(self, settings):
        """
        Saves all settings.
        """
        for item in settings.keys():
            self.client.set_item(item, str(settings[item]))
        self.display_login_page()

    def display_settings_page(self):
        """
        Displays settings page.
        """
        self.display_widget(SettingsPage(self))

    def display_login_page(self):
        """
        Displays login page for student.
        """
        self.display_widget(LoginPage(self))

    def display_register_page(self):
        """
        Displays register page for student.
        """
        self.display_widget(RegisterPage(self))

    @safe
    def register(self, group_name, user_name, password):
        """
        Tries to register the student.
        """
        self.widget.set_waiting_state()
        self.client.user_name = user_name
        self.client.password = password
        password_hash = hashlib.sha1(password.encode('utf-8')).hexdigest()
        success = self.client.server.register(user_name, password_hash, 0, group_name)
        if not success:
            self.widget.set_failed_state()
        else:
            self.display_login_page()

    @safe
    def login(self, user_name, password):
        """
        Tries to login the student.
        """
        self.widget.set_waiting_state()
        self.client.user_name = user_name
        self.client.password = password
        password_hash = hashlib.sha1(password.encode('utf-8')).hexdigest()
        self.client.user = self.client.server.login(user_name, password_hash, 0)
        if not self.client.user:
            self.widget.set_failed_state()
        else:
            self.display_home_page()

    @safe
    def logout(self):
        """
        Logs out the student.
        """
        self.client.user = False
        self.display_login_page()

    def display_home_page(self):
        """
        Displays home page with list of exams.
        """
        self.display_widget(HomePage(self))

    def display_start_exam_page(self, exam_data, cnt_questions):
        """
        Displays page before starting the exam.
        """
        self.display_widget(StartExamPage(self, exam_data, cnt_questions))

    @safe
    def list_of_exams(self):
        """
        Returns list of exams.
        """
        return self.client.server.list_of_published_exams(self.client.user['group_id'])

    @safe
    def start_exam(self, exam_id):
        """
        Starts the exam.
        """
        self.client.server.start_exam(exam_id)
        self.display_exam(exam_id)

    @safe
    def finish_exam(self, exam_id):
        """
        Finishes the exam.
        """
        self.client.server.finish_exam(exam_id)
        self.display_exam(exam_id)

    @safe
    def display_exam(self, exam_id):
        """
        Displays the exam depending on it's current state.
        """
        exam_data = self.client.server.get_exam_data_student(exam_id, self.client.user)
        questions_ids = self.client.server.get_questions_ids(exam_id)
        if not exam_data or not questions_ids:
            self.display_widget(ErrorWidget())
            return
        if exam_data['state'] == 'Not started':
            self.display_start_exam_page(exam_data, len(questions_ids))
        else:
            self.display_widget(ExamPage(self, exam_id))
            self.view_exam_question(questions_ids[0])

    @safe
    def view_exam_question(self, question_id):
        """
        Displays selected question.
        """
        exam_id = self.widget.exam_id
        exam_data = self.client.server.get_exam_data_student(exam_id, self.client.user)
        questions_ids = self.client.server.get_questions_ids(exam_id)
        questions_results = self.client.server.get_questions_results(exam_id, self.client.user)
        question_data = self.client.server.get_question_data_student(question_id, self.client.user)
        self.widget.questions_ids = questions_ids
        self.widget.questions_results = questions_results
        self.widget.display_question(exam_data, question_data)

    def get_exam_status_widget(self, exam_data):
        """
        Returns exam status widget.
        """
        if exam_data['state'] == 'Running':
            return ExamRunning(self, exam_data)
        return ExamFinished(self)

    def get_question_widget(self, exam_data, question_data):
        """
        Returns the question widget depending on it's type.
        """
        if not question_data:
            return ErrorWidget()
        if question_data['type'] == 'Short':
            if exam_data['state'] == 'Finished':
                return QuestionShortDetails(self, question_data)
            if question_data['score'] is not False:
                return QuestionShortChecked(self, question_data)
            return QuestionShort(self, question_data)
        if question_data['type'] == 'Long':
            if exam_data['state'] == 'Finished':
                return QuestionLongDetails(self, question_data)
            return QuestionLong(self, question_data)

    @safe
    def check_short(self, exam, question, answer):
        """
        Checks the student's answer to the short question and refreshes the page.
        """
        self.user.check_short(exam, question, answer)
        self.view_question(exam, question)

    @safe
    def check_long(self, exam, question, answer):
        """
        Checks the student's answer to the long question and refreshes the page.
        """
        self.user.check_long(exam, question, answer)
        self.view_question(exam, question)
        self.widget.widget.update_saved_status()


if __name__ == "__main__":
    APP = Application()
    APP.start()
