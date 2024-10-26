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
def get_data():
    try:
        data = pd.read_sql("SELECT * FROM data", con)
    except (pd.errors.DatabaseError, sqlite3.OperationalError) as e:
        print(e)
        data = pd.DataFrame(
            {
                "Data": [],
                "Czas snu": [],
                "Stan fizyczny": [],
                "Stan psychiczny": [],
                "Komentarz": [],
            },
        )
        data.to_sql("data", con)

    return data


data = get_data()

data.tail()
# %%
date_picker = pn.widgets.DatePicker(name="Date", value=date.today())
sleep_hours_slider = pn.widgets.FloatSlider(
    name="Sleep Hours", start=0, end=12, step=0.5, value=7
)
physical_score_slider = pn.widgets.IntSlider(
    name="Physical Score", start=0, end=10, value=5
)
mental_score_slider = pn.widgets.IntSlider(
    name="Mental Score", start=0, end=10, value=5
)
comment_input = pn.widgets.TextAreaInput(name="Comment")
Y_VALUES = ["Czas snu", "Stan fizyczny", "Stan psychiczny"]
checkbutton_group = pn.widgets.CheckButtonGroup(
    name="Values", value=Y_VALUES, options=Y_VALUES
)


# %%
def append_row(df, row):
    return pd.concat([df, pd.DataFrame([row], columns=row.index)]).reset_index(
        drop=True,
    )


def plot_data():
    y_values = checkbutton_group.value
    return data.hvplot(
        x="Data",
        y=y_values,
        kind="scatter",
        height=400,
        width=800,
        title="Data",
        color=PRIMARY_COLOR,
        tools=["hover"],
    )


def add_entry(clicked: bool, y_values):
    global data

    if clicked:
        new_entry = pd.Series({
            "Data": date_picker.value,
            "Czas snu": sleep_hours_slider.value,
            "Stan fizyczny": physical_score_slider.value,
            "Stan psychiczny": mental_score_slider.value,
            "Komentarz": comment_input.value,
        })

        data = append_row(data, new_entry)
        data.to_sql("data", con, if_exists="replace", index=False)

    return pn.Column(
        data.hvplot(
            x="Data",
            y=y_values,
            kind="scatter",
            color=PRIMARY_COLOR,
            hover_cols=["Komentarz"],
        ),
        pn.pane.DataFrame(data),
    )


# %%
submit_button = pn.widgets.Button(name="Add Entry", button_type="primary")
data_pane = pn.bind(add_entry, submit_button, checkbutton_group)
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
        checkbutton_group,
    ],
    main=[data_pane],
).servable()  # The ; is needed in the notebook to not display the template. Its not needed in a script

# %%
