import xml.etree.ElementTree as ET
import os

def get_xml_root():
    file_path = 'beu_data.xml'
    if not os.path.exists(file_path):
        return {}, {}

    tree = ET.parse(file_path)
    root = tree.getroot()
    return root

def get_beu_mappings():
    root = get_xml_root()
    
    # Parse and Sort Colleges
    colleges = {c.get('code'): c.text for c in root.find('colleges')}
    sorted_colleges = dict(sorted(colleges.items(), key=lambda item: item[1]))

    # Parse and Sort Departments
    departments = {d.get('code'): d.text for d in root.find('departments')}
    sorted_depts = dict(sorted(departments.items(), key=lambda item: item[1]))

    # Parse and Sort Batches
    batches = [int(d.text) for d in root.find('batches')]
    sorted_batches = sorted(batches)

    # Parse and Sort Semesters
    semesters = {d.get('code'): d.text for d in root.find('semesters')}
    sorted_semesters = dict(sorted(semesters.items(), key=lambda item: item[1]))

    return sorted_colleges, sorted_depts, sorted_batches, sorted_semesters

def get_exam_held_records():
    root = get_xml_root()

    # Parse Exam Held Records
    exam_held_records = {
        d.get('id'):{
            "batch":d.get('batch'),
            "sem":d.get('sem'),
            "exam_held":d.text
        } for d in root.find('exam_held_records')
    }

    return exam_held_records