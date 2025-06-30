import streamlit as st
import plotly.express as px
import pandas as pd
from transcriptreader import TranscriptReader
from transcriptreader import TrentUniversity

st.set_page_config(layout="wide")
set_debug_mode = False


def plot(df: pd.DataFrame) -> None:
    # An index column named "sim" or "no_sim" (from main) determines plot type.
    X, title = (
        ("no_sim", "Courses Counted Toward GPA")
        if "sim" not in df.columns
        else ("sim", "Forecast Summary")
    )
    st.subheader(
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
    st.plotly_chart(fig)


def simulator(
    coursesDict: dict,
    df: pd.DataFrame,
    credits: list[int],
    institution_class: TranscriptReader,
) -> pd.DataFrame:
    classes, remove, adding = [], [], []

    for i, (course, grade) in enumerate(coursesDict.items(), 1):
        row = {
            "Course": course,
            "Grade": grade,
            "Credits": credits[i - 1],
            "Course Code": f"Simulation {i}",
        }

        classes.append(row)
        if (df["Course Name"] == course).any():
            remove.append(course)
        else:
            adding.append(course)

    sim_df = pd.concat([df, pd.DataFrame(classes)], ignore_index=True)
    sim_df["x_addition"] = 0

    for i, courses in enumerate(remove, 1):
        sim_df = sim_df[sim_df["Course Name"] != courses]
        sim_df["x_addition"][0] = i
    sim_df.loc[sim_df["Course Name"].isna(), "Course Name"] = sim_df["Course"]

    credits_difference, gpa_difference = (
        sim_df["Credits"].sum() - df["Credits"].sum(),
        round(institution_class.get_gpa(sim_df) - institution_class.get_gpa(df), 4),
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
        f"##### Forecasted GPA: **:blue-badge[{institution_class.get_gpa(sim_df)}]**\n\n ##### **Change in GPA:** **:{gpa_color}[{gpa_sign}{gpa_difference}]**"
    )
    st.markdown(
        f"##### Total Credits After Completion: **:green-badge[{sim_df['Credits'].sum()}]**\n\n ##### **Credits Added:** **:{credits_color}[{credits_sign}{credits_difference}]**"
    )
    st.markdown("")
    return sim_df.drop(columns=["Letter Grade", "Replaced", "Course"])


def main():
    st.markdown("# Transcript Reader")
    st.markdown(
        "##### **Select an Institution to begin. Your transcript data will not be collected.**"
    )
    col1, _ = st.columns([4, 10])
    with col1:
        option = st.selectbox(
            "Institution", ["Select an Institution", "Trent University"]
        )
    institution_class = (
        TrentUniversity if option == "Trent University" else TranscriptReader
    )  # Temporary until additional institutions are supported
    content = institution_class.get_example()
    target = st.file_uploader("Upload Transcript", type=["pdf"])
    if option != "Select an Institution":
        try:
            if target is not None:
                content = institution_class.validate_pdf(target)
                st.markdown(f"## {option} Transcript Data:")
            else:
                st.markdown(f"## Sample Transcript - {option}")
            df_unprocessed = institution_class.list_to_df(content)
            df_all_courses = institution_class.clean_dataframe(df_unprocessed.copy())
            df_gpa_courses = institution_class.remove_replacements(
                df_all_courses.copy()
            )
            st.markdown("")
            st.markdown("### Courses Counted Toward GPA")
            st.markdown(
                f"##### **Grade Point Average (GPA)**: **:blue-badge[{institution_class.get_gpa(df_gpa_courses)}]**"
            )
            st.markdown(
                f"##### **Total Credits Earned**: **:green-badge[{df_gpa_courses['Credits'].sum()}]**"
            )
            with st.expander("Chart"):
                plot(df_gpa_courses.reset_index(names="no_sim"))
            with st.expander("Data Table"):
                st.subheader("Courses Counted Toward GPA")
                st.write(df_gpa_courses)
            if target is not None:
                st.markdown("")
                st.subheader("Total Courses Completed")
                st.markdown(
                    f"##### Overall Average: **:blue-badge[{institution_class.get_gpa(df_all_courses)}]**",
                    help="The average grade of every course you have completed",
                )
                st.markdown(
                    f"##### Deviation from GPA: **:green-badge[{(institution_class.get_gpa(df_gpa_courses) - institution_class.get_gpa(df_all_courses)):.4f}]**",
                    help="The total GPA amount you have recovered by replacing courses",
                )
                with st.expander("Data Table"):
                    st.subheader("Total Courses Completed")
                    st.write(df_all_courses)
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

            st.markdown("")
            st.markdown(
                "## GPA Forecasting",
                help="Course Name: The name of the course you are intending to add or replace (see the \"Course Name\" column in the data table).\n\nAnticipated Grade: The final grade you are expecting to receive for this course.\n\nCredits: O.5 for half credit \"H\" courses (1 semester), 1 for full credit \"Y\" courses (2 semesters).",
            )
            st.markdown("##### **Enter the information for courses you intend to add or replace in the menu below. Select the Forecast button to return a summary.**")
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
                    simulate_courses, credits = {}, []
                    for i in range(st.session_state.num_courses):
                        course = st.session_state.get(f"course_{i}", "").strip()
                        grade = st.session_state.get(f"grade_{i}", None)
                        credit = st.session_state.get(f"credit_{i}", None)
                        if course:
                            simulate_courses[course] = grade
                            credits.append(credit)
                    df_simulation = simulator(
                        simulate_courses, df_gpa_courses, credits, institution_class
                    )
                    with st.expander("Chart"):
                        plot(df_simulation.reset_index(names="sim"))
                    with st.expander("Data Table"):
                        st.subheader("Courses Counted Toward GPA")
                        st.write(df_simulation.drop(columns=["x_addition"]))
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
