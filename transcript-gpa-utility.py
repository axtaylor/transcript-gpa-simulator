import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from transcriptreader import TranscriptReader
from transcriptreader import TrentUniversity

st.set_page_config(layout="wide",
                   page_title="Transcript Reader",
                   page_icon="📚")

set_debug_mode = False

def plot(df: pd.DataFrame, chart_id: str = "null") -> None:
    X, title = (
        ("sim", "#### Forecast Summary")
        if chart_id=="sim"
        else ("no_sim", "#### Courses Counted Toward GPA")
    )
    st.markdown(
        title, help="Hover over any scatter point to display course information"
    )
    fig = px.scatter(
        df,
        x=X,
        y="Grade",
        hover_name="Course Name",
        labels={X: "Order on Transcript", "Grade": "Grade"},
        color="Course Name",
    )
    fig.update_layout(
        height=550,
        xaxis_range=[-1, len(df[X]) + (1 if X == "no_sim" else df["x_addition"][0])],
        yaxis_range=[-5, 105],
        yaxis_dtick=10,
        showlegend=False,
        xaxis=dict(showticklabels=False, ticks="", title=""),
    )
    fig.update_traces(marker=dict(size=8))
    st.plotly_chart(fig, key=f"{chart_id}")

def plot_distribution(
        df: pd.DataFrame,
        chart_id: str,
        institution_class: TranscriptReader
) -> None:
    option = "GPA Weighted" if chart_id=="gpadist" else "GPA Forecasted" if chart_id=="simdist" else "Total"
    st.markdown(f"#### Distribution of {option} Course Grades")
    st.markdown(f"Mean Grade: **{institution_class.get_average(df):.2f}**")
    intervals, grade = np.linspace(-1e-10, 100, 21), df["Grade"]
    dist = pd.cut(grade,
                  bins=intervals,
                  ).value_counts(
                  ).sort_index(
                  ).reset_index(
                  ).astype(str)
    dist.columns=["Grade", "Count"]

    fig = px.bar(
        dist,
        x="Grade",
        y="Count",
    )
    fig.update_layout(
    yaxis_range=[0, dist.max()],
    yaxis_dtick=1,
    )
    fig.update_traces(marker_color='#00B0EE')
    st.plotly_chart(fig, key=f"{chart_id}")


def simulator(
    df: pd.DataFrame,
    courses: list[str],
    credits: list[float],
    grades: list[int],
    institution_class: TranscriptReader,
) -> pd.DataFrame:
    classes, remove, adding = [], [], []

    for i, (course, grade, credit) in enumerate(zip(courses, grades, credits), 0):
        row = {
            "Course": course,
            "Grade": grade,
            "Credits": credit,
            "Course Code": f"Simulation {i+1}",
        }
        classes.append(row)
        if (df["Course Name"] == course).any():
            remove.append(course)
        else:
            adding.append(course)
    
    sim_df = pd.concat([df, pd.DataFrame(classes)], ignore_index=True)
    sim_df["x_addition"] = 0

    for i, c in enumerate(remove, 1):
        sim_df = sim_df[sim_df["Course Name"] != c]
        sim_df["x_addition"][0] = i
    sim_df.loc[sim_df["Course Name"].isna(), "Course Name"] = sim_df["Course"]

    credits_difference, gpa_difference = (
        sim_df["Credits"].sum() - df["Credits"].sum(),
        round(institution_class.get_average(sim_df) - institution_class.get_average(df), 4),
    )
    gpa_sign, gpa_color = (
        "+" if gpa_difference > 0 else "",
        "grey-badge"
        if gpa_difference == 0
        else ("green-badge" if gpa_difference > 0 else "red-badge"),
    )
    credits_sign, credits_color = (
        "+" if credits_difference > 0 else "",
        "grey-badge" if credits_difference == 0 else "green-badge",
    )
    st.markdown("## Forecast Summary")
    st.markdown(
        f"##### Replacing Courses: **{', '.join(remove)}**" if remove else "##### Replacing Courses: :grey-badge[None Selected]"
    )
    st.markdown(
        f"##### Adding Courses: **{', '.join(adding)}**" if adding else "##### Adding Courses: :grey-badge[None Selected]"
    )
    st.markdown("")
    st.markdown(
        f"##### **Forecasted GPA (Grade Point Average)**: **:blue-badge[{institution_class.get_gpa(sim_df)}]**",
    )
    st.markdown(
        f"##### Forecasted Average Grade: **:blue-badge[{institution_class.get_average(sim_df)}]**\n\n ##### **Change in Average Grade:** **:{gpa_color}[{gpa_sign}{gpa_difference}]**"
    )
    st.markdown(
        f"##### Total Credits After Completion: **:green-badge[{sim_df['Credits'].sum()}]**\n\n ##### **Credits Added:** **:{credits_color}[{credits_sign}{credits_difference}]**"
    )
    st.markdown("")
    return sim_df.drop(columns=["Letter Grade", "Course"])


def main():
    st.markdown("# Transcript Reader")
    st.write("")
    col1, _ = st.columns([4, 10])
    with col1:
        option = st.selectbox(
            "Select your institution", ["Select an Institution", "Trent University"]
        )
    institution_class = (
        TrentUniversity if option == "Trent University" else TranscriptReader
    )  # Temporary until additional institutions are supported
    st.write("")
    content = institution_class.get_example()
    target = st.file_uploader("Upload your transcript or select an institution for a preview.", type=["pdf"])
    st.write("___")
    if option != "Select an Institution":
        try:
            if target is not None:
                content = institution_class.validate_pdf(target)
                st.markdown(f"## {option} Transcript Summary")
            else:
                st.markdown(f"## Preview: {option} Transcript")
            df_unprocessed = institution_class.list_to_df(content)
            df_all_courses = institution_class.clean_dataframe(df_unprocessed.copy())
            df_gpa_courses = institution_class.remove_replacements(
                df_all_courses.copy()
            )
            st.markdown("")
            st.markdown("### Courses Counted toward GPA")
            st.markdown(
                f"##### **GPA (Grade Point Average)**: **:blue-badge[{institution_class.get_gpa(df_gpa_courses)}]**",
                help=f"Measured in accordance to the {option} GPA conversion scale based on individual course results.\n\n  https://www.ouac.on.ca/guide/undergraduate-grade-conversion-table"
            )
            st.markdown(
                f"##### **Average Grade**: **:blue-badge[{institution_class.get_average(df_gpa_courses)}]**",
                help=f"Includes only courses that count toward your {option} GPA"
            )
            st.markdown(
                f"##### **Total Credits Earned**: **:green-badge[{df_gpa_courses['Credits'].sum()}]**"
            )
            st.write("")
            with st.expander("Chart"):
                plot(df_gpa_courses.reset_index(names="no_sim"), "gpaplot")
            with st.expander("Table"):
                st.markdown("#### GPA Course Data Table")
                st.write(df_gpa_courses)
            with st.expander("Distribution"):
                plot_distribution(df_gpa_courses,"gpadist", institution_class)

            if target is not None:
                st.markdown("")
                st.subheader("Total Courses Completed")
                st.markdown(
                    f"##### Overall Average: **:blue-badge[{institution_class.get_average(df_all_courses)}]**",
                    help="The average grade of every course you have completed, including duplicate and failed courses.",
                )
                st.markdown(
                    f"##### Difference: **:green-badge[{(institution_class.get_average(df_gpa_courses) - institution_class.get_average(df_all_courses)):.4f}]**",
                    help="The % increase in GPA by replacing courses",
                )
                st.write("")
                with st.expander("Table"):
                    st.markdown("#### Total Courses Completed")
                    st.write(df_all_courses)
                with st.expander("Distribution"):
                    plot_distribution(df_all_courses,"totaldist", institution_class)
            if "num_courses" not in st.session_state:
                st.session_state.num_courses = 1
            if st.session_state.num_courses == 0:
                st.session_state.num_courses = 1

            def clear_all():
                st.session_state.num_courses = 1
                st.session_state["course_0"] = ""
                st.session_state["grade_0"] = 0

            def add_course():
                st.session_state.num_courses += 1

            def delete_course():
                if st.session_state.num_courses > 1:
                    st.session_state.num_courses -= 1
                else:
                    clear_all()

            st.write("___")
            st.markdown(
                "## GPA Forecasting",
                help="Course Name: The name of the course you are intending to add or replace (see the \"Course Name\" column in the data table).\n\nAnticipated Grade: The final grade you are expecting to receive for this course.\n\nCredits: O.5 for half credit \"H\" courses (1 semester), 1 for full credit \"Y\" courses (2 semesters).",
            )
            st.markdown("##### **Enter your course details below to forecast your GPA**")
            st.button("**+**", on_click=add_course)
            st.button("**–**", on_click=delete_course)
            with st.form(key="row", border=True):
                for i in range(st.session_state.num_courses):
                    space = "‎\n\n"
                    header1, header2, header3 = (
                        (f"{space}Course Name", f"{space}Anticipated Grade", f"{space}Credits")
                        if i == 0
                        else ("Course Name", "Anticipated Grade", "Credits")
                    )
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.text_input(f"{header1}", key=f"course_{i}")
                    with col2:
                        st.number_input(
                            f"{header2}",
                            min_value=0,
                            max_value=100,
                            step=1,
                            key=f"grade_{i}",
                        )
                    with col3:
                        st.number_input(
                            f"{header3}",
                            min_value=0.5,
                            max_value=1.0,
                            step=0.5,
                            key=f"credit_{i}",
                        )
                    st.write("___")
                submit = st.form_submit_button("Forecast")
            if submit:
                try:
                    courses, credits, grades = [], [], []
                    for i in range(st.session_state.num_courses):
                        course = st.session_state.get(f"course_{i}", "").strip()
                        grade = st.session_state.get(f"grade_{i}", None)
                        credit = st.session_state.get(f"credit_{i}", None)
                        if course:
                            courses.append(course)
                            credits.append(credit)
                            grades.append(grade)
                    df_simulation = simulator(
                        df_gpa_courses, courses, credits, grades, institution_class
                    )
                    with st.expander("Chart"):
                        plot(df_simulation.reset_index(names="sim"), "sim")
                    with st.expander("Table"):
                        st.markdown("#### Forecasted Courses (GPA)")
                        st.write(df_simulation.drop(columns=["x_addition"]))
                    with st.expander("Distribution"):
                        plot_distribution(df_simulation, "simdist", institution_class)
                except KeyError:
                    st.write("Enter information for at least one (1) course to prompt a forecast.")
            if set_debug_mode:
                views = {
                    "---- \n\n## Debug Mode\n\n#### list_to_df() Result;": df_unprocessed,
                    "#### clean_dataframe() (Prod. Grade) Result;": df_all_courses,
                    "#### remove_replacements() (Prod. Grade) Result;": df_gpa_courses,
                    "#### validate_pdf() Result;": content,
                }
                for heading, view in views.items():
                    st.markdown(heading)
                    st.write(view)
        except ValueError:
            st.write(
                "\nTranscript Read Error: Please verify that the provided transcript matches the selected University."
            )

if __name__ == "__main__":
    main()
