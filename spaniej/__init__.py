# %%
import hvplot.pandas  # noqa
import pandas as pd
import panel as pn
from datetime import date
import functools

# %%
pn.extension(theme="dark", sizing_mode="stretch_width")
store = pd.HDFStore("store.h5")

PARAMS = {
    "Czas snu": dict(
        plot_args=dict(color="#007bff"),
        scatter_args=dict(size=200, marker="o"),
        line_args=dict(line_width=3),
    ),
    "Stan fizyczny": dict(
        plot_args=dict(color="#28a745"),
        scatter_args=dict(size=100, marker="s"),
        line_args=dict(line_width=3),
    ),
    "Stan psychiczny": dict(
        plot_args=dict(color="#ffc107"),
        scatter_args=dict(size=200, marker="d"),
        line_args=dict(line_width=3),
    ),
}


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
        df = store["df"]
    except KeyError:
        df = empty_df()
        store["df"] = df

    return df


df = get_data()

df.tail()
# %%
date_picker = pn.widgets.DatePicker(name="Data", value=date.today())
submit_button = pn.widgets.Button(name="Ok", button_type="primary")


def pick_date(event: date):
    global \
        df, \
        sleep_hours_slider, \
        physical_score_slider, \
        mental_score_slider, \
        comment_input, \
        submit_button

    try:
        row = df.loc[event]
        sleep_hours_slider.value = row["Czas snu"]
        physical_score_slider.value = row["Stan fizyczny"]
        mental_score_slider.value = row["Stan psychiczny"]
        comment_input.value = row["Komentarz"]
    except KeyError:
        sleep_hours_slider.value = 7
        physical_score_slider.value = 5
        mental_score_slider.value = 5
        comment_input.value = ""


pn.bind(pick_date, date_picker, watch=True)

sleep_hours_slider = pn.widgets.FloatSlider(
    name="Godziny snu",
    start=0,
    end=12,
    step=0.5,
    value=7,
    bar_color=PARAMS["Czas snu"]["plot_args"]["color"],
)
physical_score_slider = pn.widgets.IntSlider(
    name="Stan fizyczny",
    start=0,
    end=10,
    value=5,
    bar_color=PARAMS["Stan fizyczny"]["plot_args"]["color"],
)
mental_score_slider = pn.widgets.IntSlider(
    name="Stan psychiczny",
    start=0,
    end=10,
    value=5,
    bar_color=PARAMS["Stan psychiczny"]["plot_args"]["color"],
)
comment_input = pn.widgets.TextAreaInput(
    name="Notatka",
    rows=4,
    auto_grow=True,
    height=100,
    resizable="height",
)
Y_VALUES = ["Czas snu", "Stan fizyczny", "Stan psychiczny"]


# %%


def plot_data():
    common = dict(
        x="index",
        ylabel="",
    )
    scatter_common = dict(
        fill_alpha=0.5,
        hover="vline",
    )
    line_common = dict(
        hover=False,
    )

    return functools.reduce(
        lambda x, y: x * y,
        (
            df.hvplot.scatter(
                y=y,
                **common,
                **scatter_common,
                **PARAMS[y]["plot_args"],
                **PARAMS[y]["scatter_args"],
                hover_tooltips=[y, *(["Komentarz"] if i == 0 else [])],
                hover_cols=["Komentarz"],
            )
            * df.hvplot.line(
                y=y,
                **common,
                **line_common,
                **PARAMS[y]["plot_args"],
                **PARAMS[y]["line_args"],
            )
            for i, y in enumerate(Y_VALUES)
        ),
    )


def add_entry(clicked: bool):
    global df

    if clicked:
        new_entry = {
            "Czas snu": sleep_hours_slider.value,
            "Stan fizyczny": physical_score_slider.value,
            "Stan psychiczny": mental_score_slider.value,
            "Komentarz": comment_input.value,
        }
        df.loc[pd.to_datetime(date_picker.value)] = new_entry
        store["df"] = df

    return pn.panel(
        plot_data(),
        sizing_mode="stretch_both",
    )


# %%
data_pane = pn.bind(add_entry, submit_button)
# %%
pn.template.FastListTemplate(
    site="Panel",
    title="SpanieJ",
    sidebar=[
        date_picker,
        sleep_hours_slider,
        physical_score_slider,
        mental_score_slider,
        comment_input,
        submit_button,
    ],
    main=[data_pane],
    accent="#d100d1",
).servable()

# %%
