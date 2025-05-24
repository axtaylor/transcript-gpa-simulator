import streamlit as st
import plotly.express as px
import pandas as pd
from transcriptreader import TranscriptReader
from transcriptreader import TrentUniversity
st.set_page_config(layout="wide")
#set_debug_mode = True

def plot(df: pd.DataFrame) -> None:
    # An index column named "sim" or "no_sim" (from main) determines plot type.
    X, title = (
        ("no_sim", "Courses Counted Toward GPA") 
        if "sim" not in df.columns
        else ("sim", "Simulation Overview")
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


def simulator(coursesDict: dict, df: pd.DataFrame, credits: list[int], institution_class: TranscriptReader) -> pd.DataFrame:
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
    st.markdown(
        f"##### Courses selected to replace: **{', '.join(remove)}**"
        if remove
        else ""
    )
    st.markdown(
        f"##### Courses selected to add: **{', '.join(adding)}**"
        if adding
        else ""
    )
    st.markdown(
        f"##### Simulated GPA: **:blue-badge[{institution_class.get_gpa(sim_df)}]**, Difference: **:{gpa_color}[{gpa_sign}{gpa_difference}]**",
        help="Total GPA after simulation",
    )
    st.markdown(
        f"##### Credits: **:green-badge[{sim_df['Credits'].sum()}]**, Difference: **:{credits_color}[{credits_sign}{credits_difference}]**",
        help="Total credits after simulation",
    )

    return sim_df.drop(columns=["Letter Grade", "Replaced", "Course"])


def main():
    st.markdown("# Transcript GPA Utility - Manage GPA and Simulate Course Load")
    st.write("Upload a transcript and select an institution to begin. Your data will not be collected or redistributed.")
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
                st.markdown(f"## Uploaded Transcript - {option}:")
            else:
                st.markdown(f"## Sample Transcript - {option}")
            df_unprocessed = institution_class.list_to_df(content)
            df_all_courses = institution_class.clean_dataframe(df_unprocessed.copy())
            df_gpa_courses = institution_class.remove_replacements(df_all_courses.copy())
            st.markdown(
                f"##### Current GPA: **:blue-badge[{institution_class.get_gpa(df_gpa_courses)}]**"
            )
            st.markdown(
                f"##### Credits: **:green-badge[{df_gpa_courses['Credits'].sum()}]**"
            )
            plot(df_gpa_courses.reset_index(names="no_sim"))
            st.write(df_gpa_courses)
            if target is not None:
                st.subheader("Total Courses Completed")
                st.markdown(
                    f"##### Overall Average: **:blue-badge[{institution_class.get_gpa(df_all_courses)}]**",
                    help="The mean grade of every course you have completed",
                )
                st.markdown(
                    f"##### Deviation from GPA: **:green-badge[{(institution_class.get_gpa(df_gpa_courses) - institution_class.get_gpa(df_all_courses)):.4f}]**",
                    help="The total GPA amount you have recovered by replacing courses",
                )
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

            st.markdown("## Course Addition and Replacement Simulator", help="Notice: If you are replacing a course, verify that the your input matches the course name on your transcript.")
            st.button("**+**", on_click=add_course)
            st.button("**–**", on_click=delete_course)
            with st.form(key="row", border=True):
                for i in range(st.session_state.num_courses):
                    space = "‎\n\n"
                    header1, header2, header3 = (
                        (f"{space}Course Name", f"{space}Grade", f"{space}Credits")
                        if i == 0
                        else ("Course Name", "Grade", "Credits")
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
                submit = st.form_submit_button("Simulate")
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
                    plot(df_simulation.reset_index(names="sim"))
                    st.write(df_simulation.drop(columns=["x_addition"]))
                except KeyError:
                    st.write("Please enter a course and grade to prompt a simulation.")
        except ValueError:
            st.write(
                "\nTranscript Read Error: Please verify that the provided transcript matches the selected University."
            )


if __name__ == "__main__":
    main()
