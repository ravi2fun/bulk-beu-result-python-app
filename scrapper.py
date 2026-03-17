import requests
import os
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv("BEU_RESULT_URL")

def fetch_student_result(reg_no, sem, year, exam_held):
    params = {
        "redg_no": reg_no,
        "semester": sem,
        "year": year,
        "exam_held": exam_held
    }
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    result = response.json()
    
    if result.get("status") == 200:
        return result["data"]
    return None
