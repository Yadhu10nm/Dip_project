import os
import win32com.client

def process_with_word():
    doc_path = os.path.abspath("project_report.docx")
    pdf_path = os.path.abspath("project_report.pdf")
    
    print(f"Opening Word to process {doc_path}...")
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    try:
        doc = word.Documents.Open(doc_path)
        # Update all fields
        doc.Fields.Update()
        
        # Calculate statistics
        pages = doc.ComputeStatistics(2) # 2 = wdStatisticPages
        words = doc.ComputeStatistics(0) # 0 = wdStatisticWords
        print(f"Document verified! Total Pages: {pages}, Total Words: {words}")
        
        # Save back updated document
        doc.Save()
        
        # Export as PDF (17 = wdFormatPDF)
        print(f"Exporting PDF to {pdf_path}...")
        doc.SaveAs(pdf_path, FileFormat=17)
        print("PDF export successful!")
        
        doc.Close()
    finally:
        word.Quit()

if __name__ == "__main__":
    process_with_word()
