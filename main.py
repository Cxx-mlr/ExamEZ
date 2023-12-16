from textual.app import App, ComposeResult
from textual.widgets import Input, Button, Label, Static
from textual.widget import Widget

from textual.containers import Horizontal, Container, Vertical, Grid

from textual import on
from textual.screen import ModalScreen

from textual.message import Message
import copy

from typing_extensions import Union

class GradePercentaje(Widget):
    DEFAULT_CSS = """
    GradePercentaje Input {
        width: 1fr;
    }

    GradePercentaje {
        height: 3;
    }

    #remove {
        text-style: none;
        background: red 10%;
        dock: right;
    }
    """

    def __init__(self, supr: bool = True, id: Union[str, None] = None) -> None:
        super().__init__(id=id)
        self.supr = supr

    def compose(self) -> ComposeResult:
        with Horizontal(id="inputs"):
            yield Input(placeholder="Nota:", id="grade")
            yield Input(placeholder="Porcentaje %", id="percentaje")
        yield Button("X", id="remove")

    class GradeChanged(Message):
        def __init__(self, grade: str) -> None:
            super().__init__()
            self.grade = grade

    class PercentajeChanged(Message):
        def __init__(self, percentaje: str) -> None:
            super().__init__()
            self.percentaje = percentaje

    @on(Input.Changed, "#grade")
    def handle_grade_changed(self, event: Input.Changed):
        self.post_message(self.GradeChanged(event.value))
    
    @on(Input.Changed, "#percentaje")
    def handle_percentaje_changed(self, event: Input.Changed):
        self.post_message(self.PercentajeChanged(event.value))

    def on_mount(self) -> None:
        if not self.supr:
            self.query_one(Button).styles.visibility = "hidden"

    @on(Button.Pressed, "#remove")
    def handle_remove_grade(self) -> None:
        self.remove()

    def get_grade(self):
        return float(self.query_one("#grade", Input).value or "0")
    
    def get_percentaje(self):
        return float(self.query_one("#percentaje", Input).value or "0")

class InputWithLabel(Widget):
    def __init__(self, value: Union[str, None] = None, input_label: str = "", input_id: Union[str, None] = None):
        super().__init__()
        self.input_label = input_label
        self.value = value
        self.input_id = input_id

    def compose(self) -> ComposeResult:
        yield Label(self.input_label)
        yield Input(self.value, id=self.input_id)

class SettingsScreen(ModalScreen):
    DEFAULT_CSS = """
    #settings {
        grid-size: 2 3;
        grid-rows: 1fr 1fr auto;
        width: 40%;
        height: 40%;
        height: 14;
        grid-gutter: 0 1;
        border: $accent;
    }

    #settings Button {
        width: 1fr;
        color: $accent;
        text-style: none;
    }
    """
    def compose(self):
        with Grid(id="settings"):
            yield InputWithLabel(f"{self.app.settings.min_grade}", input_label="Nota mínima:", input_id="min-grade")
            yield InputWithLabel(f"{self.app.settings.max_grade}", input_label="Nota máxima:", input_id="max-grade")
            yield InputWithLabel(f"{self.app.settings.passing_threshold}", input_label="Nota mínima para aprobar:", input_id="passing-threshold")
            yield InputWithLabel(f"{self.app.settings.target_grade}", input_label="Nota que deseo:", input_id="target-grade")
            yield Button("Cancelar", id="cancel")
            yield Button("Guardar", id="save")

    class InputChanged(Message):
        def __init__(self, input: Input) -> None:
            super().__init__()
            self.input = input

    def on_input_changed(self, event: Input.Changed) -> None:
        self.post_message(self.InputChanged(event.input))

    class Save(Message):
        pass

    class Cancel(Message):
        pass

    @on(Button.Pressed, "#save")
    def handle_save(self) -> None:
        self.post_message(self.Save())
        app.pop_screen()
    
    @on(Button.Pressed, "#cancel")
    def handle_cancel(self) -> None:
        self.post_message(self.Cancel())
        app.pop_screen()

    def key_escape(self) -> None:
        self.app.pop_screen()

class Gear(Widget):
    def __init__(self, id: Union[str, None] = None):
        super().__init__(id=id)

    def compose(self) -> ComposeResult:
        yield Static(":gear:", id=self.id)

    def on_click(self) -> None:
        self.app.push_screen(SettingsScreen())

class ModalMessage(ModalScreen):
    DEFAULT_CSS = """
    ModalMessage Static {
        width: 50%;
        height: 50%;
        max-height: 12;
        text-align: center;
        content-align: center middle;
        border: wide white;
    }
    """
    def __init__(self, TEXT: str = ""):
        super().__init__()
        self.TEXT = TEXT

    def compose(self) -> ComposeResult:
        yield Static(self.TEXT)
    
    def key_escape(self) -> None:
        self.app.pop_screen()

    def on_click(self) -> None:
        self.app.pop_screen()

class ResettableObject:
    def __init__(self, min_grade, max_grade, passing_threshold, target_grade):
        self.min_grade = min_grade
        self.max_grade = max_grade
        self.passing_threshold = passing_threshold
        self.target_grade = target_grade

        self.save_state()

    def save_state(self):
        self._initial_state = copy.deepcopy(self.__dict__)
    
    def reset(self):
        self.__dict__.update(self._initial_state)

class GradesApp(App[None]):
    DEFAULT_CSS = """
    Screen {
        align: center middle;
    }

    #main-panel {
        border: round $accent;
        width: 55%;
        height: auto;
        border-title-align: center;
        border-title-style: bold;
    }

    #subtitle {
        margin: 1;
    }

    #buttons {
        dock: bottom;
        height: auto;
    }

    #add {
        margin: 1;
        text-style: none;
        color: $accent;
    }

    #compute-grades {
        text-style: none;
        color: $accent;
        width: 40%;
    }

    #gear:hover {
        color: $accent-darken-1 70%;
    }

    #gear {
        width: 3;
        height: 1;
        color: $boost;
        text-style: bold;
        content-align-horizontal: right;
    }

    #gear-container {
        height: 1;
        align: right middle;
    }

    #compute-grades-container {
        height: 3;
        align: left middle;
    }
    """

    settings = ResettableObject(
        min_grade=0, max_grade=5, passing_threshold=3, target_grade=3
    )

    def compose(self) -> ComposeResult:
        with Container(id="main-panel"):
            yield Label("Ingresa aquí tus notas actuales:", id="subtitle")
            yield GradePercentaje(supr=False, id="first")
            with Vertical(id="buttons"):
                yield Button("㊉ Agregar Nota", id="add")
                with Container(id="compute-grades-container"):
                    yield Button("CALCULAR NOTA :mortar_board:", id="compute-grades")
                with Container(id="gear-container"):
                    yield Gear(id="gear")
    
    def on_mount(self) -> None:
        main_panel = self.query_one("#main-panel", Container)
        main_panel.border_title = "¿Cuánto Necesito para el Final?"
    
    @on(Button.Pressed, "#add")
    def handle_add_grade(self) -> None:
        self.query_one("#main-panel", Container).mount(
            GradePercentaje()
        )

    @on(Button.Pressed, "#compute-grades")
    def handle_compute_grades(self) -> None:
        average: float = 0
        percentaje_sum: float = 0.0
        for grade_percentaje in self.query(GradePercentaje):
            grade, percentaje = grade_percentaje.get_grade(), grade_percentaje.get_percentaje()
            average += grade * (percentaje / 100)
            percentaje_sum += percentaje

        percentaje_sum /= 100

        if percentaje_sum.is_integer():
            percentaje_sum = int(percentaje_sum)

        if percentaje_sum < 1:
            grade_q = round((self.settings.passing_threshold - average)/(1 - percentaje_sum), 1)
            grade_k = round((self.settings.target_grade - average)/(1 - percentaje_sum), 1)
            average = round(average, 1)

            if grade_q <= 0: grade_q = 0
            if grade_k <= 0: grade_k = 0

            self.push_screen(ModalMessage(f"Calificación necesaria para aprobar: {grade_q}\nCalificación necesaria para alcanzar la meta: {grade_k}\nPromedio actual: {average}"))
        elif percentaje_sum == 1:
            average = round(average, 1)
            self.push_screen(ModalMessage(f"Obtuviste una calificación final de {average} porque ya se ingresó el 100% de las notas."))
        else:
            self.push_screen(ModalMessage(f"La suma de los porcentajes no debe exceder el 100%"))

    def on_grade_percentaje_grade_changed(self, event: GradePercentaje.GradeChanged):
        try:
            value = float(event.grade or "0")
            if value < self.settings.min_grade or value > self.settings.max_grade:
                raise ValueError()
        except ValueError:
            self.query_one("#compute-grades", Button).disabled = True
        else:
            self.query_one("#compute-grades", Button).disabled = False

    def on_grade_percentaje_percentaje_changed(self, event: GradePercentaje.PercentajeChanged):
        try:
            value = float(event.percentaje or "0")
            if value > 100:
                raise ValueError()
        except ValueError:
            self.query_one("#compute-grades", Button).disabled = True
        else:
            self.query_one("#compute-grades", Button).disabled = False
    
    def on_settings_screen_input_changed(self, event: SettingsScreen.InputChanged) -> None:
        settings_screen = self.query_one(SettingsScreen)
        try:
            value = float(event.input.value or "0")

            if value.is_integer():
                value = int(value)
        except ValueError:
            settings_screen.query_one("#save", Button).disabled = True
        else:
            settings_screen.query_one("#save", Button).disabled = False
            id = event.input.id

            if id == "min-grade":
                self.settings.min_grade = value
            elif id == "max-grade":
                self.settings.max_grade = value
            elif id == "passing-threshold":
                self.settings.passing_threshold = value
            elif id == "target-grade":
                self.settings.target_grade = value
        finally:
            min_grade, max_grade, passing_threshold, target_grade = (
                self.settings.min_grade,
                self.settings.max_grade,
                self.settings.passing_threshold,
                self.settings.target_grade
            )

            if all((
                    min_grade < max_grade,
                    passing_threshold >= min_grade,
                    passing_threshold <= max_grade,
                    target_grade >= min_grade,
                    min_grade <= max_grade
                )): pass
            else:
                settings_screen.query_one("#save", Button).disabled = True
    
    def on_settings_screen_save(self) -> None:
        self.settings.save_state()

    def on_settings_screen_cancel(self) -> None:
        self.settings.reset()

if __name__ == "__main__":
    app = GradesApp()
    app.run()
