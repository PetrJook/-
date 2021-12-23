import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QHBoxLayout, QVBoxLayout, QPushButton, QLabel

class Calculator(QWidget):
    def __init__(self):
        super(Calculator, self).__init__()
        self.vbox = QVBoxLayout(self)
        self.hbox_input = QHBoxLayout()
        self.hbox_output = QHBoxLayout()
        self.hbox_first = QHBoxLayout()
        self.hbox_result = QHBoxLayout()

        self.vbox.addLayout(self.hbox_input)
        self.vbox.addLayout(self.hbox_output)
        self.vbox.addLayout(self.hbox_first)
        self.vbox.addLayout(self.hbox_result)
        self.input = QLineEdit(self)
        self.hbox_input.addWidget(self.input)

        self.output = QLabel(self)
        self.hbox_output.addWidget(self.output)

        self.b_1 = QPushButton("1", self)
        self.hbox_first.addWidget(self.b_1)

        self.b_2 = QPushButton("2", self)
        self.hbox_first.addWidget(self.b_2)

        self.b_3 = QPushButton("3", self)
        self.hbox_first.addWidget(self.b_3)

        self.b_plus = QPushButton("+", self)
        self.hbox_first.addWidget(self.b_plus)

        self.b_minus = QPushButton("-", self)
        self.hbox_first.addWidget(self.b_minus)

        self.b_div = QPushButton("/", self)
        self.hbox_first.addWidget(self.b_div)

        self.b_mult = QPushButton("*", self)
        self.hbox_first.addWidget(self.b_mult)

        self.b_point = QPushButton(".", self)
        self.hbox_first.addWidget(self.b_point)

        self.b_result = QPushButton("=", self)
        self.hbox_result.addWidget(self.b_result)

        self.b_clear = QPushButton("C", self)
        self.hbox_result.addWidget(self.b_clear)

        self.b_plus.clicked.connect(lambda: self._operation("+"))
        self.b_minus.clicked.connect(lambda: self._operation("-"))
        self.b_div.clicked.connect(lambda: self._operation("/"))
        self.b_mult.clicked.connect(lambda: self._operation("*"))

        self.b_clear.clicked.connect(lambda: self._clear())

        self.b_result.clicked.connect(self._result)

        self.b_1.clicked.connect(lambda: self._button("1"))
        self.b_2.clicked.connect(lambda: self._button("2"))
        self.b_3.clicked.connect(lambda: self._button("3"))
        self.b_point.clicked.connect(lambda: self._button("."))

        self.num_1 = None

    def _button(self, param):
        # output_line = self.output.text()
        input_line = self.input.text()
        if not(param == '.' and '.' in input_line):
            self.input.setText(input_line + param)
        # self.output.setText(output_line + param)

    def _operation(self, op):
        line = self.input.text()
        if line.replace('.', ''):
            self.num_1 = float(self.input.text())
        self.op = op
        self.input.setText('')
        self.output.setText(line + ' ' + op + ' ')

    def _clear(self):
        self.input.setText('')
        self.output.setText('')
    def _result(self):
        output_line = self.output.text()
        input_line = self.input.text()
        if self.num_1 and input_line:
            self.num_2 = float(self.input.text())
            if self.op == "+":
                res = str(self.num_1 + self.num_2)
                self.input.setText(res)
                self.output.setText(output_line + input_line + ' ' + '=' + ' ' + res)
            elif self.op == "-":
                res = str(self.num_1 - self.num_2)
                self.input.setText(res)
                self.output.setText(output_line + input_line + ' ' + '=' + ' ' + res)

            elif self.op == "*":
                res = str(self.num_1 * self.num_2)
                self.input.setText(res)
                self.output.setText(output_line + input_line + ' ' + '=' + ' ' + res)

            elif self.op == "/":
                res = str(self.num_1 / self.num_2)
                self.input.setText(res)
                self.output.setText(output_line + input_line + ' ' + '=' + ' ' + res)
            elif self.op == "C":
                self.input.setText('')
                self.output.setText('')


app = QApplication(sys.argv)

win = Calculator()
win.show()

sys.exit(app.exec_())
