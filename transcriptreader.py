import re
import pandas as pd
import numpy as np
from pypdf import PdfReader

# Base class for future expansion.
class TranscriptReader:
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
    def get_average(df: pd.DataFrame) -> float:
        return
    def get_gpa(df: pd.DataFrame) -> float:
        return
    def gpa_conversion(scale: int, grades: list[float]) -> float: # https://www.ouac.on.ca/guide/undergraduate-grade-conversion-table
        if (scale==3):
            levels = [
                (90, 4.0),
                (85, 3.9),
                (80, 3.7),
                (77, 3.3),
                (73, 3.0),
                (70, 2.7),
                (67, 2.3),
                (63, 2.0),
                (60, 1.7),
                (57, 1.3),
                (53, 1.0),
                (50, 0.7),
                (0, 0),
            ]
        else:
            return "Error"
        def convert(grade):
            for level, gpa in levels:
                if grade >= level:
                    return gpa
        return [convert(p) for p in grades]

# Reader class for Trent University.
class TrentUniversity(TranscriptReader):   

    def scale() -> int:
        return 3 # https://www.ouac.on.ca/guide/undergraduate-grade-conversion-table

    def get_example() -> list[str]:
        return " Trent University                                           1600 "," West Bank Drive                                         "," Peterborough, Ontario                                          K 9 H  0 G 2 , Canada                                  "," To: Anonymous User                                                           4 "," Water St                                          "," Page:    1  of    2           "," Peterborough ON K 9 H  3 M 2                                   "," Student Number:   9999999                                                                    "," Date of Birth : "," Jan  30                                                                           "," Issued On     :   2025 "," Apr  22                                                                                                     "," Name: Anonymous User                                                             "," Undergraduate                                                        "," Creds Mark Grade  R        __________________________________________________________________________________________                  "," Trent National Renewable Scholarship - Fall          "," Trent National renewable Scholarship - Winter                                 "," Business Administration        0000 H: Course0       0.5     71    B-              "," Economics                      0001 H:  Course1      0.5     75    B               "," Economics                      0002 H: Course2      0.5     72    B-              "," Indigenous Studies             0003 H: Course3    0.5     90    A+              "," Business Administration        0004 H: Course4             0.5     75    B               "," Computer Science                      0005 H: Course5        0.5     89    A               "," Computer Science     0006 H: Course6   0.5     77    B+              "," Indigenous Studies             0007 H: Course7     0.5     75    B               "," Media Studies                  0008 H: Course8                   0.5     92    A+                                          "," Sociology                      0009 H: Course9      0.5     85    A-                                            DEAN'S HONOUR ROLL                                 "," Business Administration        0010 H: Course16        0.5     92    A+              "," Business Administration        0011 H: Course10         0.5     96    A+               "," Business Administration        0012 H: Course11        0.5     86    A               "," Business Administration        0013 H: Course12              0.5     75    B               "," Economics                      0014 H: Course99            0.5     52    D-              "," Business Administration        0015 H: Course14                0.5     84    A-              "," Business Administration        0016 H: Course13                0.5     73    B               "," Business Administration        0017 H: Course17           0.5     85    A               "," Economics                      0018 H: Course18   0.5     71    B-              "," Economics                      0019 H: Course99            0.5     78    B+    R                                     "," Business Administration        1999 H: Course100       0.5     61    C-                                      "," Business Administration        0020 H: Course100       0.5     80    A-    R         "," Business Administration        0021 H: Course19                      0.5     85    A               "," Business Administration        0022 H: Course20          0.5     92    A+              "," Business Administration        0023 H: Course21       0.5     81    A-              "," Business Administration        0024 H: Course22       0.5     85    A              "," Economics                      0025 H: Course23   0.5     90    A+              "," Business Administration        0026 H: Course24    0.5     80    A-              "," Business Administration        0027 H: Course25             0.5     80    A-              "," Business Administration        0028 H: Course26         0.5     90    A+              "," Business Administration        0029 H: Course27     0.5     85    A               "," Business Administration        0030 H: Course28   0.5     95    A+                                            DEAN'S HONOUR ROLL                                     "," Computer Science               0031 H: Course29                     0.5     93    A+                                            DEAN'S HONOUR ROLL                                                                     \f                                                          "," Trent University                                           1600 "," West Bank Drive                                         "," Peterborough, Ontario                                          K 9 H  0 G 2 , Canada                                  "," To: Anonymous User                                                           4 "," Water St                                          "," Page:    2  of    2           "," Peterborough ON K 9 H  3 M 2                                   "," Student Number:   9999999                                                                    "," Date of Birth : "," Jan  30                                                                           "," Issued On     :   2025 "," Apr  22                                                                                                     "," Name: Anonymous User                                                             "," Undergraduate                                                        "," Creds Mark Grade  R        __________________________________________________________________________________________                  "," Trent National Renewable Scholarship - Fall          "," Trent National renewable Scholarship - Winter                                 "," Business Administration        0032 H: Course32          0.5     81    A-              "," Business Administration        0033 H: Course30             0.5     85    A               "," Business Administration        0034 H: Course31   0.5     83    A-              "," Computer Science               0035 H: Course33    0.5     88    A               "," Business Administration        0036 H: Course34                            "," Business Administration        0037 H: Course35      0.5     88    A               "," Communications                 0038 H: Course36                                           "," Political Science        0039 H: Course37                             "," Philosophy                     0040 H: Course38                                                                "," Current Academic Status : Good Standing                                                                                                 *** End of UNOFFICIAL Record *** "

    def validate_pdf(target: str) -> list[str]:
        def apply_regex(pdf: str) -> str:
            pdf = re.sub(r"---+", "", pdf)
            pdf = re.sub(r"\n", " ", pdf)
            pdf = re.sub(r"\b\d{4}-\d{4}\s+Academic Year\b", "", pdf)
            pdf = re.sub(r"\b\d{4}\s+\w\w Summer Term\b", "", pdf)
            return re.sub(r"(?<=\s)(?= [A-Z][a-z]+(?: [A-Z][a-z]+)*)", "\n", pdf)

        transcript, content = PdfReader(target), ""
        for page in transcript.pages:
            page_text = page.extract_text()
            if page_text:
                content += apply_regex(page_text)
        return [i for i in content.split("\n") if i.strip()]

    # Strip sentences split by >three whitespace for column entries;
    # Iterate for each line of the list as a new row.
    def list_to_df(items: list[str]) -> pd.DataFrame:
        return pd.DataFrame(
            [[i.strip() for i in item.split("   ") if i.strip()] for item in items],
            columns=["Major", "Course", "Credits", "Grade", "Letter Grade", "Replaced"],
        )

    def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        # ["1000 H", "Course Name"]
        df[["Course Code", "Course Name"]] = df["Course"].str.split(
            ":", n=1, expand=True
        )
        df["Course Code"] = df["Major"] + " " + df["Course Code"]
        df.loc[df["Letter Grade"] == "R", ["Replaced", "Letter Grade"]] = ["R", None]
        df.loc[df["Grade"] == "PRE", "Grade"] = None
        df.loc[df["Replaced"] == "DEAN'S HONOUR ROLL", ["Replaced"]] = None

        # Drop courses not taken yet
        df = df.dropna(subset=["Grade"]).copy()

        df["Grade"] = df["Grade"].astype(int)
        df["Credits"] = df["Credits"].astype(float)

        for col in ["Course Name", "Letter Grade", "Course Code"]:
            df[col] = df[col].str.strip()

        return (
            df.drop(columns=["Major", "Course"])
            .reindex(
                [
                    "Course Code",
                    "Course Name",
                    "Credits",
                    "Grade",
                    "Letter Grade",
                    #"Replaced",
                ],
                axis=1,
            )
            .reset_index()
            .drop(columns=["index"])
        )

    def remove_replacements(df: pd.DataFrame) -> pd.DataFrame:
        df = df.loc[df.groupby("Course Name")["Grade"].idxmax()]
        df = df.loc[df.groupby("Course Code")["Grade"].idxmax()]
        return df.sort_index().reset_index().drop(columns=["index"])

    def get_average(input: pd.DataFrame) -> float:
        df = input.copy()
        if (df["Credits"] == 1).any():
            df["adj_grade"] = df["Grade"]
            df.loc[df["Credits"] == 1, ["adj_grade"]] = df["adj_grade"] * 2
            adjusted_grade, adjusted_courses_complete = (
                df["adj_grade"].sum(),
                df["Credits"].sum() * 2,
            )
            return round(adjusted_grade / adjusted_courses_complete, 4)
        else:
            return round(df["Grade"].mean(), 4)
        
    def get_gpa(input: pd.DataFrame) -> float:
        input["GPA"] = TranscriptReader.gpa_conversion(TrentUniversity.scale(), input["Grade"])
        df = input.copy()
        if (df["Credits"] == 1).any():
            df = pd.concat([df, df[df["Credits"] == 1]],
                           ignore_index=True,
                           )
        gpa = TranscriptReader.gpa_conversion(TrentUniversity.scale(), df["Grade"])
        return f"{np.mean(gpa):.2f}"
