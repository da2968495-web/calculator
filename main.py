from decimal import Decimal, InvalidOperation

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

MAX_DIGITS = 12


def fmt(d):
    s = format(d, "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


class Calculator(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=dp(10),
                         spacing=dp(10), **kwargs)
        self.current = ""    # the number being typed
        self.total = None    # the number before the operator
        self.op = None       # "+" or "-"
        self.fresh = False   # True right after "="

        self.display = Label(text="0", font_size=dp(48), halign="right",
                             valign="middle", size_hint_y=0.25)
        self.display.bind(size=lambda w, s: setattr(w, "text_size", s))
        self.add_widget(self.display)

        grid = GridLayout(cols=4, spacing=dp(8))
        keys = ["7", "8", "9", "+",
                "4", "5", "6", "-",
                "1", "2", "3", "=",
                "C", "0", ".", "DEL"]
        for k in keys:
            if k in "+-=":
                color = (1, 0.6, 0.1, 1)
            elif k in ("C", "DEL"):
                color = (0.6, 0.2, 0.2, 1)
            else:
                color = (0.25, 0.25, 0.25, 1)
            btn = Button(text=k, font_size=dp(30), background_normal="",
                         background_color=color)
            btn.bind(on_release=lambda b: self.press(b.text))
            grid.add_widget(btn)
        self.add_widget(grid)

    # ---------- logic ----------
    def press(self, key):
        if key.isdigit():
            self.digit(key)
        elif key == ".":
            self.dot()
        elif key in ("+", "-"):
            self.operator(key)
        elif key == "=":
            self.equals()
        elif key == "C":
            self.current, self.total, self.op, self.fresh = "", None, None, False
        elif key == "DEL":
            self.delete()
        self.refresh()

    def digit(self, d):
        if self.fresh:
            self.current, self.fresh = "", False
        if len(self.current.replace("-", "").replace(".", "")) >= MAX_DIGITS:
            return
        if self.current == "0":
            self.current = d
        elif self.current == "-0":
            self.current = "-" + d
        else:
            self.current += d

    def dot(self):
        if self.fresh:
            self.current, self.fresh = "", False
        if "." in self.current:
            return
        if self.current in ("", "-"):
            self.current += "0."
        else:
            self.current += "."

    def operator(self, key):
        if self.current in ("", "-"):
            if self.total is None:
                if key == "-" and self.current == "":
                    self.current = "-"      # negative first number
            else:
                self.op = key               # change the operator
            return
        try:
            value = Decimal(self.current)
        except InvalidOperation:
            return
        if self.op is None:
            self.total = value
        elif self.op == "+":
            self.total = self.total + value
        else:
            self.total = self.total - value
        self.op, self.current, self.fresh = key, "", False

    def equals(self):
        if self.op is None or self.current in ("", "-"):
            return
        try:
            value = Decimal(self.current)
        except InvalidOperation:
            return
        result = self.total + value if self.op == "+" else self.total - value
        self.current = fmt(result)
        self.total, self.op, self.fresh = None, None, True

    def delete(self):
        if self.fresh:
            return
        if self.current:
            self.current = self.current[:-1]
        elif self.op is not None:           # undo the operator
            self.current = fmt(self.total)
            self.total, self.op = None, None

    def refresh(self):
        left = f"{fmt(self.total)} {self.op} " if self.op else ""
        text = left + (self.current or ("" if self.op else "0"))
        self.display.text = text
        n = len(text)
        self.display.font_size = dp(48) if n <= 10 else dp(32) if n <= 16 else dp(22)


class CalculatorApp(App):
    def build(self):
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        return Calculator()


if __name__ == "__main__":
    CalculatorApp().run()
