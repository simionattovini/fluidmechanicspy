import numpy as np
from kivymd.app import MDApp
import FluidMechanicsModule as Fm
from kivy.garden.matplotlib import FigureCanvasKivyAgg
import matplotlib.pyplot as plot
from kivy.core.window import Window
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField

"""
This file creates a user interface using kivymd just to test the capabilities of the FluidMechanicsModule. It is not intended to be a part of any application.
It is just some code for testing :)
"""

def moody_data_re():
    Re_lam = np.linspace(500, 5000, 10)
    Re_turb = np.linspace(2300, 1e4, 10)
    for n in range(4, 9):
        Re_turb = np.hstack((Re_turb, np.linspace(10 ** n, 10 ** (n + 1), 100)))
    return Re_lam, Re_turb


def moody_data():
    Re_lam, Re_turb = moody_data_re()

    f_lam = np.array(list(map(lambda x: Fm.f_laminar(x, True), Re_lam)))

    f_turb = []
    for rr in Fm.__REL_ROUGH_STD_VALS:
        if len(f_turb) == 0:
            f_turb = np.array(list(map(lambda x: Fm.f_colebrook(rr, x), Re_turb)))
        else:
            f_turb = np.vstack((np.array(list(map(lambda x: Fm.f_colebrook(rr, x), Re_turb))), f_turb))

    return Re_lam, Re_turb, f_lam, f_turb


class MyPlotCanvas(FigureCanvasKivyAgg):
    def __init__(self):
        self.fig: plot.Figure = plot.figure()
        self.update_background_plot()
        super().__init__(self.fig)

    def update_background_plot(self):
        Re_lam, Re_turb, f_lam, f_turb = moody_data()
        self.fig = plot.figure()
        ax: plot.Axes = plot.axes()
        axs = ax.secondary_yaxis('right', functions=(Fm.f2rr_colebrook, Fm.rr2f_colebrook))
        ax.set_xlabel('Reynolds Number (Re) [-]')
        ax.set_ylabel('Friction Factor (f) [-]')
        axs.set_ylabel('Relative Roughness (e/D) [-]')
        self.fig.add_axes(ax)
        plot.loglog(Re_lam, f_lam, 'b', axes=ax)
        plot.loglog(Re_turb, f_turb.T, 'b', axes=ax)
        plot.grid(True, which='both', color=[0.8 for _ in range(3)], linewidth=0.5)
        plot.margins(x=0, y=0)

    def plot_point(self, reynolds: float, relrough: float, f: float) -> None:
        Re_lam, Re_turb = moody_data_re()

        if reynolds < 2300:
            y_lam = 64/Re_lam
            plot.loglog(Re_lam, y_lam, 'r')
        else:
            y_turb = np.array(list(map(lambda x: Fm.f_colebrook(relrough, x), Re_turb)))
            plot.loglog(Re_turb, y_turb, 'r')

        plot.loglog(reynolds, f, 'ko')
        xh = np.array([min(Re_lam), reynolds])
        yh = np.ones(2)*f
        xv = np.ones(2)*reynolds
        yv = np.array([Fm.f_colebrook(0, max(Re_turb)), f])
        plot.loglog(xh, yh, 'k--', linewidth=1)
        plot.loglog(xv, yv, 'k--', linewidth=1)
        self.draw()


class Moody1App(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_box_layout = MDBoxLayout(
            orientation="vertical"
        )
        self.clear_button = MDRaisedButton(
            text="Limpar Diagrama",
            size_hint=[0.8, 1]
        )
        self.reynolds_textfield = MDTextField(
            hint_text="Número de Reynolds",
            size_hint_y=1
        )
        self.relrough_textfield = MDTextField(
            hint_text="e/D (Rugosidade Relativa)",
            size_hint_y=1
        )
        self.update_button = MDRaisedButton(
            text="Calcular!",
            size_hint=[0.6, 1]
        )
        self.result_label = MDLabel(
            text="f = ???",
            size_hint_y=1
        )
        self.top_boxlayout = MDBoxLayout(size_hint_y=0.9)
        self.bottom_boxlayout = MDBoxLayout(size_hint_y=0.1)
        self.plot_canvas = MyPlotCanvas()

    def build(self):
        self.top_boxlayout.add_widget(self.plot_canvas)

        self.bottom_boxlayout.add_widget(self.clear_button)
        self.bottom_boxlayout.add_widget(self.reynolds_textfield)
        self.bottom_boxlayout.add_widget(self.relrough_textfield)
        self.bottom_boxlayout.add_widget(self.update_button)
        self.bottom_boxlayout.add_widget(self.result_label)
        self.bottom_boxlayout.spacing = 10

        self.main_box_layout.add_widget(self.top_boxlayout)
        self.main_box_layout.add_widget(self.bottom_boxlayout)
        Window.size = (1000, 600)
        return self.main_box_layout

    def refresh_plot(self) -> None:
        self.top_boxlayout.remove_widget(self.plot_canvas)
        self.plot_canvas = MyPlotCanvas()
        self.top_boxlayout.add_widget(self.plot_canvas)


thisapp = Moody1App()


def clear_button_callback(app: Moody1App) -> None:
    app.refresh_plot()
    app.reynolds_textfield.text = ""
    app.relrough_textfield.text = ""
    app.result_label.text = "f = ???"


thisapp.clear_button.on_release = lambda: clear_button_callback(thisapp)


def update_button_callback(app: Moody1App) -> None:
    try:
        reynolds = float(app.reynolds_textfield.text)
        relrough = float(app.relrough_textfield.text)
    except Exception as ex:
        print(ex.__str__())
        app.result_label.text = 'f = ???'
        return

    try:
        f = Fm.f_regardless(reynolds, relrough)
    except ValueError as ve:
        print(ve.__str__())
        app.result_label.text = 'f = ???'
        return

    app.refresh_plot()
    app.plot_canvas.plot_point(reynolds, relrough, f)
    app.result_label.text = f'f = {f}'


thisapp.update_button.on_release = lambda: update_button_callback(thisapp)

thisapp.run()
