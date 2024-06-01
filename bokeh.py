import pandas as pd
from math import pi
from bokeh.io import push_notebook, show, output_notebook
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource, HoverTool, LinearColorMapper, FactorRange
from bokeh.palettes import Category20, Viridis256
from bokeh.plotting import figure
from bokeh.transform import factor_cmap, cumsum
from sklearn.feature_extraction.text import CountVectorizer
import json
import ipywidgets as widgets
from IPython.display import display

# Enable Bokeh to output directly into the notebook
output_notebook()

# Load data
try:
    with open('data_ana.json', 'r') as json_file:
        data = json.load(json_file)
    df = pd.DataFrame(data)
except FileNotFoundError:
    raise FileNotFoundError("The specified JSON file was not found.")

# Data preparation
df["location"] = df["location"].str.strip().str.upper()

# Function to create visualizations
def create_figures(filtered_df):
    #1: Histogram of job offers by location
    heatmap_data = (
        filtered_df["location"]
        .value_counts()
        .reset_index(name="count")
        .head(20)
        .sort_values(by="count", ascending=False)
    )
    heatmap_data.columns = ["location", "count"]
    locations_list = heatmap_data["location"].tolist()
    counts_list = heatmap_data["count"].tolist()

    source_histogram = ColumnDataSource(data={"x": locations_list, "top": counts_list})
    p_histogram = figure(
        x_range=FactorRange(*locations_list),
        title="Histogram of Job Offers by Location",
        toolbar_location=None,
        tools="tap",
    )
    p_histogram.vbar(
        x="x",
        top="top",
        width=0.9,
        source=source_histogram,
        fill_color={
            "field": "top",
            "transform": LinearColorMapper(
                palette=Viridis256, low=min(counts_list), high=max(counts_list)
            ),
        },
    )
    p_histogram.xaxis.axis_label = "Locations"
    p_histogram.yaxis.axis_label = "Number of Listings"
    p_histogram.xaxis.major_label_orientation = 45
    p_histogram.add_tools(
        HoverTool(tooltips=[("Location", "@x"), ("Number", "@top")])
    )

    # 2: most demanded functions
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(filtered_df["Fonction"].fillna(""))
    word_freq = dict(zip(vectorizer.get_feature_names_out(), X.toarray().sum(axis=0)))
    word_freq_df = pd.DataFrame(list(word_freq.items()), columns=["Fonction", "Frequency"])
    top_10_functions = (
        word_freq_df.sort_values(by="Frequency", ascending=False).head(20)
    )

    source_functions = ColumnDataSource(top_10_functions)
    p_functions = figure(
        x_range=FactorRange(*top_10_functions["Fonction"]),
        title="Most Demanded Functions",
        toolbar_location=None,
        tools="",
    )
    p_functions.vbar(
        x="Fonction",
        top="Frequency",
        width=0.9,
        source=source_functions,
        line_color="white",
        fill_color=factor_cmap(
            "Fonction", palette=Category20[20], factors=top_10_functions["Fonction"]
        ),
    )
    p_functions.xaxis.major_label_orientation = 45
    p_functions.add_tools(
        HoverTool(tooltips=[("Function", "@Fonction"), ("Frequency", "@Frequency")])
    )

    #3: Pie chart of experience levels
    experience_counts = filtered_df["Niveau_etude"].value_counts().reset_index()
    experience_counts.columns = ["Experience", "Count"]
    experience_counts["angle"] = (
        experience_counts["Count"] / experience_counts["Count"].sum() * 2 * pi
    )
    experience_counts["color"] = Category20[len(experience_counts)]

    source_sector = ColumnDataSource(experience_counts)
    p_sector = figure(
        title="Distribution of Experience Levels",
        toolbar_location=None,
        tools="hover",
        tooltips="@Experience: @Count",
        x_range=(-1.5, 1.5),
    )
    p_sector.wedge(
        x=0,
        y=1,
        radius=0.6,
        start_angle=cumsum("angle", include_zero=True),
        end_angle=cumsum("angle"),
        line_color="white",
        fill_color="color",
        legend_field="Experience",
        source=source_sector,
    )
    p_sector.axis.axis_label = None
    p_sector.axis.visible = False
    p_sector.grid.grid_line_color = None

    #4: Ring chart of job offers by industry
    secteur_counts = filtered_df["Fonction"].value_counts().reset_index(name="count")
    secteur_counts.columns = ["Fonction", "count"]
    secteur_counts["angle"] = (
        secteur_counts["count"] / secteur_counts["count"].sum() * 2 * pi
    )
    secteur_counts["color"] = [
        Category20[20][i % 20] for i in range(len(secteur_counts))
    ]

    source_pie = ColumnDataSource(secteur_counts)
    p_pie = figure(
        title="Distribution of Job Offers by Industry",
        toolbar_location=None,
        tools="hover",
        tooltips="@Fonction: @count",
        x_range=(-1.5, 1.5),
    )
    p_pie.annular_wedge(
        x=0,
        y=0,
        inner_radius=0.3,
        outer_radius=0.5,
        start_angle=cumsum("angle", include_zero=True),
        end_angle=cumsum("angle"),
        line_color="white",
        fill_color="color",
        legend_field="Fonction",
        source=source_pie,
    )
    p_pie.axis.axis_label = None
    p_pie.axis.visible = False
    p_pie.grid.grid_line_color = None

    #5: job titles
    nombre_postes = filtered_df["title"].value_counts().head(20).reset_index(name="count")
    nombre_postes.columns = ["title", "count"]

    source_top_postes = ColumnDataSource(nombre_postes)
    p_top_postes = figure(
        x_range=FactorRange(*nombre_postes["title"]),
        title="Job Titles",
        x_axis_label="Job Title",
        y_axis_label="Number of Positions",
        toolbar_location=None,
    )
    p_top_postes.vbar(
        x="title",
        top="count",
        width=0.8,
        source=source_top_postes,
        color="orange",
    )
    p_top_postes.add_tools(
        HoverTool(tooltips=[("Job Title", "@title"), ("Number of Positions", "@count")])
    )
    p_top_postes.xaxis.major_label_orientation = 45

    #6: internship providers
    nombre_entreprises = filtered_df["Entreprise"].value_counts().head(20).reset_index(name="count")
    nombre_entreprises.columns = ["Entreprise", "count"]

    source_top_entreprises = ColumnDataSource(nombre_entreprises)
    p_top_entreprises = figure(
        x_range=FactorRange(*nombre_entreprises["Entreprise"]),
        title="Internship Providers",
        x_axis_label="Company",
        y_axis_label="Number of Internships",
        toolbar_location=None,
    )
    p_top_entreprises.vbar(
        x="Entreprise",
        top="count",
        width=0.8,
        source=source_top_entreprises,
        color="skyblue",
    )
    p_top_entreprises.add_tools(
        HoverTool(tooltips=[("Company", "@Entreprise"), ("Number of Internships", "@count")])
    )
    p_top_entreprises.xaxis.major_label_orientation = 45

    #7:  Salary distribution
    salaire_counts = filtered_df["salaire"].value_counts().reset_index()
    salaire_counts.columns = ["salaire", "count"]

    source_salaire = ColumnDataSource(salaire_counts)

    p_salaire = figure(
        x_range=source_salaire.data["salaire"],
        title="Distribution of Salaries",
        toolbar_location=None,
        tools="",
        width=800,
        height=400,
    )
    p_salaire.vbar(
        x="salaire",
        top="count",
        width=0.9,
        source=source_salaire,
        line_color="white",
        fill_color=factor_cmap("salaire", palette="Viridis256", factors=source_salaire.data["salaire"]),
    )

    hover_salaire = HoverTool()
    hover_salaire.tooltips = [("Salary", "@salaire"), ("Frequency", "@count")]
    p_salaire.add_tools(hover_salaire)
    p_salaire.xaxis.major_label_orientation = 1.2

    return {
        'histogram': (source_histogram, p_histogram),
        'functions': (source_functions, p_functions),
        'sector': (source_sector, p_sector),
        'pie': (source_pie, p_pie),
        'top_postes': (source_top_postes, p_top_postes),
        'top_entreprises': (source_top_entreprises, p_top_entreprises),
        'salaire': (source_salaire, p_salaire),
    }

# Update function to be called when selection changes
def update(attr, old, new):
    selected_city = new
    filtered_df = df[df["location"] == selected_city]
    figures = create_figures(filtered_df)

    # Update each plot with new data
    for key, value in figures.items():
        source, plot = value
        plot_source[key].data.update(source.data)

# Initialize the dashboard with all locations data
initial_figures = create_figures(df)
plot_source = {key: value[0] for key, value in initial_figures.items()}

# Create the Dropdown widget for location selection
cities = df["location"].unique().tolist()
select_widget = widgets.Dropdown(
    options=cities,
    value=cities[0],
    description='Select City:',
    disabled=False,
)

# Layout
layout = column(
    row(initial_figures['histogram'][1], initial_figures['functions'][1]),
    row(initial_figures['sector'][1], initial_figures['pie'][1]),
    row(initial_figures['top_postes'][1], initial_figures['top_entreprises'][1]),
    initial_figures['salaire'][1],
)

def update_plot(change):
    update(None, None, change['new'])
    push_notebook(handle=handle)

select_widget.observe(update_plot, names='value')

display(select_widget)

# Display the layout in the notebook
handle = show(layout, notebook_handle=True)