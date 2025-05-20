import streamlit as st
st.set_page_config(layout="wide")
import plotly.express as px
import pypdf
from pypdf import PdfReader
import pandas as pd
import numpy as np
import re
class TranscriptGPAUtility():

    def plot(df: pd.DataFrame):
        X, title = ("index", "Simulation Overview") if "Index" not in df.columns else ("Index", "Courses Counted Toward GPA")
        st.subheader(title)
        fig = px.scatter(df, x=X, y="Grade", hover_name="Course Name", labels={X: "Order of Transcript", "Grade": "Grade"}, color="Course Name")
        fig.update_layout(height=550, xaxis_range=[-1, len(df[X])], yaxis_range=[-5, 105], yaxis_dtick = 10)
        fig.update_traces(marker=dict(size=8)) 
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig)

    def get_gpa(df: pd.DataFrame) -> float:
        if (df["Credits"] == 1).any():
            df["CalcGrd"] = df["Grade"]
            df.loc[df["Credits"] == 1, ["CalcGrd"]] = df['CalcGrd']*2
            grd = df['CalcGrd'].sum()
            crd = df['Credits'].sum()*2
            return round(grd/crd,4)
        else:
            return round(df['Grade'].mean(),4)
          
    def get_example() -> list[str]:
        return 
    def validate_pdf(target: str) -> list[str]: 
        return
    def list_to_df(list: list[str]) -> pd.DataFrame:
        return
    def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        return
    def remove_replacements(df: pd.DataFrame) -> pd.DataFrame:
        return 
    def simulator(coursesDict: dict, df: pd.DataFrame, credits: list[int]) -> pd.DataFrame:
        return

class TrentUniversity(TranscriptGPAUtility):

    def get_example() -> list[str]:
        return " Trent University                                           1600 "," West Bank Drive                                         "," Peterborough, Ontario                                          K 9 H  0 G 2 , Canada                                  "," To: Anonymous User                                                           4 "," Water St                                          "," Page:    1  of    2           "," Peterborough ON K 9 H  3 M 2                                   "," Student Number:   9999999                                                                    "," Date of Birth : "," Jan  30                                                                           "," Issued On     :   2025 "," Apr  22                                                                                                     "," Name: Anonymous User                                                             "," Undergraduate                                                        "," Creds Mark Grade  R        __________________________________________________________________________________________                  "," Trent National Renewable Scholarship - Fall          "," Trent National renewable Scholarship - Winter                                 "," Business Administration        0000 H: Course0       0.5     71    B-              "," Economics                      0001 H:  Course1      0.5     75    B               "," Economics                      0002 H: Course2      0.5     72    B-              "," Indigenous Studies             0003 H: Course3    0.5     90    A+              "," Business Administration        0004 H: Course4             0.5     75    B               "," Computer Science                      0005 H: Course5        0.5     89    A               "," Computer Science     0006 H: Course6   0.5     77    B+              "," Indigenous Studies             0007 H: Course7     0.5     75    B               "," Media Studies                  0008 H: Course8                   0.5     92    A+                                          "," Sociology                      0009 H: Course9      0.5     81    A-                                            DEAN'S HONOUR ROLL                                 "," Business Administration        0010 H: Course16        0.5     92    A+              "," Business Administration        0011 H: Course10         0.5     96    A+               "," Business Administration        0012 H: Course11        0.5     86    A               "," Business Administration        0013 H: Course12              0.5     75    B               "," Economics                      0014 H: Course99            0.5     52    D-              "," Business Administration        0015 H: Course14                0.5     84    A-              "," Business Administration        0016 H: Course13                0.5     73    B               "," Business Administration        0017 H: Course17           0.5     85    A               "," Economics                      0018 H: Course18   0.5     71    B-              "," Economics                      0019 H: Course99            0.5     78    B+    R                                     "," Business Administration        1999 H: Course100       0.5     61    C-                                      "," Business Administration        0020 H: Course100       0.5     80    A-    R         "," Business Administration        0021 H: Course19                      0.5     85    A               "," Business Administration        0022 H: Course20          0.5     92    A+              "," Business Administration        0023 H: Course21       0.5     81    A-              "," Business Administration        0024 H: Course22       0.5     85    A              "," Economics                      0025 H: Course23   0.5     90    A+              "," Business Administration        0026 H: Course24    0.5     80    A-              "," Business Administration        0027 H: Course25             0.5     80    A-              "," Business Administration        0028 H: Course26         0.5     90    A+              "," Business Administration        0029 H: Course27     0.5     85    A               "," Business Administration        0030 H: Course28   0.5     95    A+                                            DEAN'S HONOUR ROLL                                     "," Computer Science               0031 H: Course29                     0.5     93    A+                                            DEAN'S HONOUR ROLL                                                                     \f                                                          "," Trent University                                           1600 "," West Bank Drive                                         "," Peterborough, Ontario                                          K 9 H  0 G 2 , Canada                                  "," To: Anonymous User                                                           4 "," Water St                                          "," Page:    2  of    2           "," Peterborough ON K 9 H  3 M 2                                   "," Student Number:   9999999                                                                    "," Date of Birth : "," Jan  30                                                                           "," Issued On     :   2025 "," Apr  22                                                                                                     "," Name: Anonymous User                                                             "," Undergraduate                                                        "," Creds Mark Grade  R        __________________________________________________________________________________________                  "," Trent National Renewable Scholarship - Fall          "," Trent National renewable Scholarship - Winter                                 "," Business Administration        0032 H: Course32          0.5     81    A-              "," Business Administration        0033 H: Course30             0.5     85    A               "," Business Administration        0034 H: Course31   0.5     83    A-              "," Computer Science               0035 H: Course33    0.5     88    A               "," Business Administration        0036 H: Course34                            "," Business Administration        0037 H: Course35      0.5     88    A               "," Communications                 0038 H: Course36                                           "," Political Science        0039 H: Course37                             "," Philosophy                     0040 H: Course38                                                                "," Current Academic Status : Good Standing                                                                                                 *** End of UNOFFICIAL Record *** "

    def validate_pdf(target: str) -> list[str]:
        def apply_regex(pdf: str) -> str:
            pdf = re.sub(r"---+", '', pdf) 
            pdf = re.sub(r"\n", " ", pdf)
            pdf = re.sub(r"\b\d{4}-\d{4}\s+Academic Year\b", "", pdf)
            pdf = re.sub(r"\b\d{4}\s+\w\w Summer Term\b", "", pdf) 
            return re.sub(r'(?<=\s)(?= [A-Z][a-z]+(?: [A-Z][a-z]+)*)', "\n", pdf) # Selected one whitespace before classname
        transcript, content = PdfReader(target), ""
        for page in transcript.pages:
            page_text = page.extract_text()
            if page_text:
                content += apply_regex(page_text)
        return [i for i in content.split("\n") if i.strip()]
    
    def list_to_df(items: list[str]) -> pd.DataFrame:
        return pd.DataFrame(
            [[i.strip() for i in item.split("   ") if i.strip()] for item in items],
            columns=["Major", "Course", "Credits", "Grade", "Letter Grade", "Replaced"])

    def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        df[["Course Code", "Course Name"]] = df["Course"].str.split(":", n=1, expand=True)
        df["Course Code"] = (df["Major"] +" "+ df["Course Code"]).str.replace(r'\s+', ' ', regex=True).str.strip()
        df.loc[df["Letter Grade"] == "R", ["Replaced", "Letter Grade"]] = ["R", None]
        df.loc[df["Grade"] == "PRE", "Grade"] = None
        df.loc[df["Replaced"] == "DEAN'S HONOUR ROLL", ["Replaced"]] = None
        df = df.dropna(subset=['Grade']).copy()
        df["Index"] = df.reset_index().index
        df['Grade'] = df['Grade'].astype(int)
        df['Credits'] = df['Credits'].astype(float)

        for col in ["Course Name", "Letter Grade", "Course Code"]:
            df[col] = df[col].str.strip()

        return df.drop(columns=['Major', 'Course']).reindex(["Index", "Course Code", "Course Name", "Credits", "Grade", "Letter Grade", "Replaced"], axis=1)

    def remove_replacements(df: pd.DataFrame) -> pd.DataFrame:
        df = df.loc[df.groupby('Course Name')['Grade'].idxmax()]
        df = df.loc[df.groupby('Course Code')['Grade'].idxmax()]
        st.markdown(f"##### Calculated GPA: **:blue-badge[{TrentUniversity.get_gpa(df)}]**")
        st.markdown(f"##### Credits: **:green-badge[{df["Credits"].sum()}]**")
        return df.sort_values(by="Index", ascending=True).reset_index().drop(columns=["Index", "index"])

    def simulator(coursesDict: dict, df: pd.DataFrame, credits: list[int]) -> pd.DataFrame:
        classes, remove, adding = [], [], []
        for i, (course, grade) in enumerate(coursesDict.items(), 1):
            row = {
                'Course': course,
                'Grade': grade,
                'Credits': credits[i-1],
                'Course Code': f"Simulation {i}",
            }
            classes.append(row)
            if (df["Course Name"] == course).any():
                remove.append(course)
            else:
                adding.append(course)
                
        sim_df = pd.concat([df, pd.DataFrame(classes)], ignore_index=True)
        for courses in remove:
            sim_df = sim_df[sim_df["Course Name"] != courses]
        sim_df.loc[sim_df["Course Name"].isna(), "Course Name"] = sim_df["Course"]

        st.markdown(f"##### Courses selected to replace: **{', '.join(remove)}**" if remove else "")
        st.markdown(f"##### Courses selected to add: **{', '.join(adding)}**" if adding else "")
        credits_difference = sim_df["Credits"].sum()-df["Credits"].sum()
        gpa_difference = round(TrentUniversity.get_gpa(sim_df)-TrentUniversity.get_gpa(df),4)
        gpa_sign = "+" if gpa_difference > 0 else ""
        gpa_color = "grey-badge" if gpa_difference == 0 else ("green-badge" if gpa_difference > 0 else "red-badge")
        st.markdown(f"##### Simulated GPA: **:blue-badge[{TrentUniversity.get_gpa(sim_df)}]**, Difference: **:{gpa_color}[{gpa_sign}{gpa_difference}]**")
        credits_sign = "+" if credits_difference > 0 else ""
        credits_color = "grey-badge" if credits_difference == 0 else "green-badge"
        st.markdown(f"##### Credits: **:green-badge[{sim_df['Credits'].sum()}]**, Difference: **:{credits_color}[{credits_sign}{credits_difference}]**")
        return sim_df.drop(columns=["Letter Grade", "Replaced", "Course"])

def main():
    st.markdown("# Transcript GPA Utility - Manage GPA and Simulate Course Load")
    st.write("Upload a transcript and select an institution to begin. Your data will not be collected or redistributed.")
    col1, _ = st.columns([4,10])
    with col1:
        option = st.selectbox("Institution", ["Select an Institution", "Trent University"])
    institution_class = TrentUniversity if option == "Trent University" else TranscriptGPAUtility
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
            df_all_courses = institution_class.clean_dataframe(df_unprocessed)
            df_gpa_courses = institution_class.remove_replacements(df_all_courses)
            institution_class.plot(df_gpa_courses.reset_index(names="Index"))
            st.write(df_gpa_courses)
            if target is not None:
                st.subheader("Total Courses Completed")
                st.write(df_all_courses.reset_index().drop(columns=["Index", "index"]))
            if "num_courses" not in st.session_state:
                st.session_state.num_courses = 1
            if (st.session_state.num_courses == 0):
                st.session_state.num_courses = 1
            def addCourse():
                st.session_state.num_courses += 1
            def deleteCourse():
                if (st.session_state.num_courses > 1): 
                    st.session_state.num_courses -= 1
                else:
                    clearAll()
            def clearAll():
                st.session_state.num_courses = 1
                st.session_state["course_0"] = ""
                st.session_state["grade_0"] = 0
            st.markdown("## Course Addition and Replacement Simulator")
            st.markdown("Notice: If you are replacing a course, verify that the your input matches the course name on your transcript.")
            st.button("**+**", on_click=addCourse)
            st.button("**–**", on_click=deleteCourse)
            with st.form(key="row", border=True):
                for i in range(st.session_state.num_courses):
                    space = "‎\n\n"
                    header1, header2, header3 = (f"{space}Course Name", f"{space}Grade", f"{space}Credits") if i == 0 else ("Course Name","Grade","Credits")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.text_input(f"{header1}", key=f"course_{i}")
                    with col2:
                        st.number_input(f"{header2}", min_value=0, max_value=100, step=1, key=f"grade_{i}")
                    with col3:
                        st.number_input(f"{header3}", min_value=0.5, max_value=1.0, step=0.5, key=f"credit_{i}")
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
                    df_simulation = institution_class.simulator(simulate_courses, df_gpa_courses, credits)
                    institution_class.plot(df_simulation.reset_index())
                    st.write(df_simulation.sort_values(by="Grade", ascending=False))
                except KeyError:
                    st.write("Please enter a course and grade to prompt a simulation.")     
        except ValueError:
            st.write(f"\nTranscript Read Error: Please verify that the provided transcript matches the selected University.")

if __name__ == "__main__":
    main()
