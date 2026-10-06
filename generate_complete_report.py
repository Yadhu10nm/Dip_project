import os
import sys
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from report_sections.front_matter import update_existing_front_matter, update_toc_table, add_abstract_and_lists
from report_sections.chapter1 import add_chapter1
from report_sections.chapter2 import add_chapter2
from report_sections.chapter3 import add_chapter3
from report_sections.chapter4 import add_chapter4
from report_sections.chapter5 import add_chapter5
from report_sections.chapter6 import add_chapter6
from report_sections.back_matter import add_back_matter

def build_report():
    template_path = "project_report_template_original.docx"
    output_path = "project_report.docx"
    
    if not os.path.exists(template_path):
        print(f"Error: Template {template_path} not found!")
        return

    print("Opening template document...")
    doc = docx.Document(template_path)
    
    # Page Map for Table of Contents
    page_map = {
        1: "i",
        2: "ii",
        3: "iii",
        4: "iv",
        5: "v",
        6: "vi",
        7: "vii",
        8: "1",
        9: "1",
        10: "1",
        11: "2",
        12: "2",
        13: "3",
        14: "4",
        15: "4",
        16: "5",
        17: "5",
        18: "6",
        19: "7",
        20: "8",
        21: "9",
        22: "10",
        23: "10",
        24: "10",
        25: "11",
        26: "12",
        27: "12",
        28: "13",
        29: "14",
        30: "15",
        31: "16",
        32: "17",
        33: "18",
        34: "19",
        35: "19",
        36: "20",
        37: "21",
        38: "22",
        39: "23",
        40: "24",
        41: "25",
        42: "26",
        43: "29",
        44: "29",
        45: "29",
        46: "30",
        47: "32",
        48: "34",
        49: "37",
        50: "37",
        51: "37",
        52: "38",
        53: "39",
        54: "40",
        55: "41",
        56: "47",
    }
    
    print("Updating existing front matter (Title, Certificate, Declaration)...")
    update_existing_front_matter(doc)
    
    print("Updating Table of Contents table...")
    update_toc_table(doc, page_map)
    
    print("Adding Abstract, List of Figures, List of Tables...")
    add_abstract_and_lists(doc)
    
    print("Adding Chapter 1: INTRODUCTION...")
    add_chapter1(doc)
    
    print("Adding Chapter 2: PROJECT REQUIREMENTS...")
    add_chapter2(doc)
    
    print("Adding Chapter 3: PROPOSED SYSTEM AND METHODOLOGY...")
    add_chapter3(doc)
    
    print("Adding Chapter 4: IMPLEMENTATION...")
    add_chapter4(doc)
    
    print("Adding Chapter 5: RESULTS AND DISCUSSION...")
    add_chapter5(doc)
    
    print("Adding Chapter 6: CONCLUSION AND FUTURE SCOPE...")
    add_chapter6(doc)
    
    print("Adding Back Matter (References, Appendix A, Appendix B)...")
    add_back_matter(doc)
    
    print(f"Saving compiled document to {output_path}...")
    doc.save(output_path)
    print("Project report successfully generated!")

if __name__ == "__main__":
    build_report()
