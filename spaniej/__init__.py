# %%
import hvplot.pandas  # noqa
import numpy as np
import pandas as pd
import panel as pn
import sqlite3
from datetime import date

PRIMARY_COLOR = "#0072B5"
SECONDARY_COLOR = "#B54300"
# %%
pn.extension(design="material", sizing_mode="stretch_width")
con = sqlite3.connect("db.sqlite")


# %%
def empty_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Czas snu": pd.Series([], dtype="int"),
            "Stan fizyczny": pd.Series([], dtype="int"),
            "Stan psychiczny": pd.Series([], dtype="int"),
            "Komentarz": pd.Series([], dtype="str"),
        },
        index=pd.Series([], dtype="datetime64[s]"),
    )


def get_data():
    try:
        data = pd.read_sql("SELECT * FROM data", con, index_col="index")
    except (pd.errors.DatabaseError, sqlite3.OperationalError):
        data = empty_df()
        data.to_sql("data", con)

    return data


data = get_data()

data.tail()
# %%
date_picker = pn.widgets.DatePicker(name="Date", value=date.today())
submit_button = pn.widgets.Button(
    name="Dodaj" if date.today() in data.index else "Zakutalizuj", button_type="primary"
)


def pick_date(event: date):
    global \
        data, \
        sleep_hours_slider, \
        physical_score_slider, \
        mental_score_slider, \
        comment_input, \
        submit_button

    try:
        row = data.loc[event]
        sleep_hours_slider.value = row["Czas snu"]
        physical_score_slider.value = row["Stan fizyczny"]
        mental_score_slider.value = row["Stan psychiczny"]
        comment_input.value = row["Komentarz"]
        submit_button.name = "Zaktualizuj"
    except KeyError:
        sleep_hours_slider.value = 7
        physical_score_slider.value = 5
        mental_score_slider.value = 5
        comment_input.value = ""
        submit_button.name = "Dodaj"


pn.bind(pick_date, date_picker, watch=True)

sleep_hours_slider = pn.widgets.FloatSlider(
    name="Godziny snu", start=0, end=12, step=0.5, value=7
)
physical_score_slider = pn.widgets.IntSlider(
    name="Stan fizyczny", start=0, end=10, value=5
)
mental_score_slider = pn.widgets.IntSlider(
    name="Stan psychiczny", start=0, end=10, value=5
)
comment_input = pn.widgets.TextAreaInput(
    name="Notatka", rows=4, auto_grow=True, resizable="height"
)
Y_VALUES = ["Czas snu", "Stan fizyczny", "Stan psychiczny"]


# %%


def plot_data():
    return data.hvplot(
        y=Y_VALUES,
        kind="scatter",
        color=PRIMARY_COLOR,
        hover_cols=["Komentarz"],
    )


def add_entry(clicked: bool):
    global data

    if clicked:
        data.loc[date_picker.value] = {
            "Czas snu": sleep_hours_slider.value,
            "Stan fizyczny": physical_score_slider.value,
            "Stan psychiczny": mental_score_slider.value,
            "Komentarz": comment_input.value,
        }
        data.to_sql("data", con, if_exists="replace")

    return pn.panel(
        data.hvplot(
            y=reversed(Y_VALUES),
            kind="scatter",
            hover_cols=["Komentarz"],
            fill_alpha=0.5,
            size=200,
        ),
        sizing_mode="stretch_both",
    )


# %%
data_pane = pn.bind(add_entry, submit_button)
# %%
pn.template.MaterialTemplate(
    site="Panel",
    title="SuppanieJ",
    sidebar=[
        date_picker,
        sleep_hours_slider,
        physical_score_slider,
        mental_score_slider,
        comment_input,
        submit_button,
    ],
    main=[data_pane],
).servable()

# %%
