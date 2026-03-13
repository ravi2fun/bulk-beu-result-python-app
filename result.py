import requests
import pandas as pd

regNos = []
start_regular_reg = int(input("Enter the first registration no of regular students:-"))
end_regular_reg = int(input("Enter the last registration no of regular students:-"))
start_lateral_reg = int(input("Enter the first registration no of lateral students:-"))
end_lateral_reg = int(input("Enter the last registration no of lateral students:-"))
year_back_count = int(input("Enter count of year back students:-"))
for i in range(year_back_count):
    regNos.append(int(input("Enter registration no. of year back student {}:-".format(i+1))))
regNos += list(range(start_regular_reg,end_regular_reg+1)) + list(range(start_lateral_reg,end_lateral_reg+1))
sem = input("Enter semester in roman caps(Example-I):-")
year = int(input("Enter original year in which exam to be held(Example-2024):-"))
exam_held = input("Enter month/year in which exam is held(Example-May/2025):-")

# Common API params
base_url = "https://beu-bih.ac.in/backend/v1/result/get-result?"
params_template = {
    "semester": sem,
    "year": year,
    "exam_held": exam_held
}

all_students = []   # store all student info
writer = pd.ExcelWriter("BEU_Bulk_Results.xlsx", engine="openpyxl")

for reg in regNos:
    params = params_template.copy()
    params["redg_no"] = reg

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        result = response.json()

        if result["status"] != 200:
            print(f"❌ Result not found for {reg}")
            continue

        data = result["data"]

        # --- Student Info ---
        student_basic_info = {
            "Reg No": data["redg_no"],
            "Name": data["name"],
            "Father": data["father_name"],
            "Mother": data["mother_name"],
            "College": data["college_name"],
            "Course": data["course"],
            "Semester": data["semester"],
            "Exam Held": data["exam_held"],
            "Exam Year": data["examYear"],
        }
        

        # --- Theory Subjects ---
        theory_df = pd.DataFrame(data["theorySubjects"])
        student_theory_subjects = dict(zip(theory_df['code']+' : '+theory_df['name'], theory_df['ese']))

        # --- Practical Subjects ---
        practical_df = pd.DataFrame(data["practicalSubjects"])
        student_practical_subjects = dict(zip(practical_df['code']+' : '+practical_df['name'], practical_df['ese']))

        # --- SGPA, CGPA, Fail ---
        student_result = {
            "SGPA": data["sgpa"][0],
            "CGPA": data["cgpa"],
            "Result": data["fail_any"]
        }

        # Save student info in summary list
        student_info = student_basic_info | student_theory_subjects | student_practical_subjects | student_result
        all_students.append(student_info)

        # Write student-specific sheet
        #sheet_name = str(data["redg_no"])
        #info_df = pd.DataFrame(student_info.items(), columns=["Field", "Value"])
        #info_df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=0)
        #theory_df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=len(info_df)+3)
        #practical_df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=len(info_df)+len(theory_df)+6)

        print(f"✅ Saved {reg}")

    except Exception as e:
        print(f"⚠️ Error fetching {reg}: {e}")

# --- Master Summary Sheet ---
summary_df = pd.DataFrame(all_students)
summary_df.to_excel(writer, sheet_name="Summary", index=False)

writer.close()
print("📂 All results saved in BEU_Bulk_Results.xlsx")
