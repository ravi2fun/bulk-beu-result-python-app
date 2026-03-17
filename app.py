from nicegui import ui
import pandas as pd
import asyncio
from datetime import datetime
from scrapper import fetch_student_result
from data_manager import get_beu_mappings, get_exam_held_records

# Load mappings from beu_data.xml
colleges, departments, batches, semesters = get_beu_mappings()

now = datetime.now()

class Data:
    def __init__(self):
        self.enabled = False

data = Data()

async def start_process():
    # 1. Validation
    if not college_select.value or not dept_select.value:
        ui.notify('Please select both College and Department', type='negative')
        return

    # 2. Build Registration List
    # Format: [CollegeCode][DeptCode][Batch][3-Digit-ID]
    c_code = college_select.value
    d_code = dept_select.value
    b_code = batch_select.value
    
    reg_list = [f"{b_code}{d_code}{c_code}{i:03d}" for i in range(int(start_id.value), int(end_id.value) + 1)]
    if checkbox.value:
        reg_list += [f"{int(b_code)+1}{d_code}{c_code}{i:03d}" for i in range(901, 920)]
    total = len(reg_list)
    
    # 3. UI Setup for Progress
    progress_container.clear()
    with progress_container:
        ui.label(f'Processing students...').classes('text-sm font-bold')
        bar = ui.linear_progress(value=0, show_value=False).classes('w-full mt-2')
        status_label = ui.label('Initializing...').classes('text-xs italic')

    all_students = []
    sem = semesters[sem_select.value]
    year = exam_year.value
    exam_month_year = exam_held.value

    # 4. Scrape Loop
    for index, reg in enumerate(reg_list):
        try:
            # Update Status
            status_label.set_text(f"Fetching {reg}...")

            # Use the core logic from your scrapper.py
            data = fetch_student_result(reg, sem, year, exam_month_year)

            if data:
                student_info = create_student_info(data)
                all_students.append(student_info)
            
            # Update Progress Bar
            bar.set_value((index + 1) / total)
            await asyncio.sleep(0.1)  # Small delay to keep UI responsive
            
        except Exception as e:
            print(f"Error {reg}: {e}")
    # 5. Finalize
    if all_students:
        pd.DataFrame(all_students).to_excel("BEU_Results_Report.xlsx", index=False)
        ui.notify("Success! Report saved to BEU_Results_Report.xlsx", type='positive')
        status_label.set_text("Completed. File saved.")
    else:
        ui.notify("No data was retrieved.", type='warning')
        status_label.set_text("Failed to retrieve data.")

# Helper to calculate academic timing
def update_exam_details():
    try:
        # Calculate year of exam based on batch and semester
        calculated_year = 2000 + int(batch_select.value) + int(sem_select.value) // 2

        # Set Default Exam Held as Current Month/Year
        exam_held_record = now.strftime("%B/%Y")

        # Find Exam Held Month/Year details
        exam_held_records = get_exam_held_records()
        for record in exam_held_records.values():
            if record['sem'] == sem_select.value and record['batch'] == batch_select.value:
                exam_held_record = record['exam_held']
        # Update UI fields
        exam_year.value = calculated_year
        exam_held.value = exam_held_record
        
    except Exception as e:
        print(f"Calculation error: {e}")

def create_student_info(data):
    # --- Student Info ---
    student_basic_info = {
        "Reg No": data["redg_no"],
        "Name": data["name"],
        "Father": data["father_name"],
        "Mother": data["mother_name"],
        "College": data["college_name"],
        "Course": data["course"],
        "Semester": data["semester"]
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
    return student_info

    # Write student-specific sheet
    #sheet_name = str(data["redg_no"])
    #info_df = pd.DataFrame(student_info.items(), columns=["Field", "Value"])
    #info_df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=0)
    #theory_df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=len(info_df)+3)
    #practical_df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=len(info_df)+len(theory_df)+6)



# --- GUI Layout ---
with ui.card().classes('w-full max-w-2xl mx-auto mt-10 p-6 shadow-lg'):
    ui.label("BEU Bulk Result Downloader").classes("text-h4 text-blue-800 mb-4")
    
    with ui.row().classes('w-full gap-4'):
        college_select = ui.select(colleges, label="Select College").classes('flex-1')
        dept_select = ui.select(departments, label="Select Branch").classes('flex-1')

    with ui.row().classes('w-full gap-4 mt-2'):
        batch_select = ui.select(
            {str(b): f"20{b}-20{b+4}" for b in batches}, 
            label="Batch",
            on_change=update_exam_details
        ).classes('flex-1')
        sem_select = ui.select(
            semesters, 
            label="Semester", 
            on_change=update_exam_details
        ).classes('flex-1')

    with ui.row().classes('w-full gap-4 mt-2'):
        exam_year = ui.number("Exam Year").classes('flex-1')
        exam_held = ui.input("Exam Held").classes('flex-1')
    
    with ui.row().classes('w-full gap-4 mt-2'):
        start_id = ui.number("Registartion Start", value=1, format='%d').classes('flex-1')
        end_id = ui.number("Registration End", value=60, format='%d').classes('flex-1')

    checkbox = ui.checkbox('Lateral Students').bind_value(data, 'enabled')

    ui.button("Start Bulk Scrape", on_click=start_process).classes("w-full mt-6 py-4 bg-blue-700 text-white font-bold")
    
    # Empty container where the progress bar will appear
    progress_container = ui.column().classes('w-full mt-6')

ui.run(title="BEU Result Downloader")