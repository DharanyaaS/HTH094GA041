import os
import pymupdf as fitz

def generate_test_policy_pdf():
    upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "uploads"))
    os.makedirs(upload_dir, exist_ok=True)
    pdf_path = os.path.join(upload_dir, "test_policy.pdf")

    doc = fitz.open()

    # Page 1: Sections 1, 2, 3
    page1 = doc.new_page(width=595, height=842) # A4
    text_page1 = """Company Data Protection Policy

1. Purpose
This policy defines the core requirements for managing and safeguarding customer data across corporate operations.

2. Data Access
Employees may access confidential customer data only when access is required for their assigned work.

3. Data Sharing
Confidential customer information must not be shared with external parties without written approval from the Data Protection Officer.
"""
    # Insert text on page 1 with nice positioning
    page1.insert_text(fitz.Point(50, 70), "Company Data Protection Policy", fontsize=18, fontname="helv", color=(0.1, 0.1, 0.3))
    page1.insert_text(fitz.Point(50, 110), "Document Reference: POL-DPA-2024 | Version 2.1 | Page 1", fontsize=9, color=(0.4, 0.4, 0.4))
    
    # Section 1
    page1.insert_text(fitz.Point(50, 160), "1. Purpose", fontsize=14, fontname="helv", color=(0.15, 0.2, 0.4))
    page1.insert_text(fitz.Point(50, 185), "This policy defines mandatory requirements for safeguarding customer data across all operations.", fontsize=11, fontname="helv")

    # Section 2
    page1.insert_text(fitz.Point(50, 240), "2. Data Access", fontsize=14, fontname="helv", color=(0.15, 0.2, 0.4))
    page1.insert_text(fitz.Point(50, 265), "Employees may access confidential customer data only when access is required for their assigned work.", fontsize=11, fontname="helv")

    # Section 3
    page1.insert_text(fitz.Point(50, 320), "3. Data Sharing", fontsize=14, fontname="helv", color=(0.15, 0.2, 0.4))
    page1.insert_text(fitz.Point(50, 345), "Confidential customer information must not be shared with external parties without written approval\nfrom the Data Protection Officer.", fontsize=11, fontname="helv")

    # Page 2: Sections 4 and 5
    page2 = doc.new_page(width=595, height=842)
    page2.insert_text(fitz.Point(50, 70), "Company Data Protection Policy (Continued)", fontsize=16, fontname="helv", color=(0.1, 0.1, 0.3))
    page2.insert_text(fitz.Point(50, 100), "Document Reference: POL-DPA-2024 | Page 2", fontsize=9, color=(0.4, 0.4, 0.4))

    # Section 4
    page2.insert_text(fitz.Point(50, 140), "4. Data Retention", fontsize=14, fontname="helv", color=(0.15, 0.2, 0.4))
    page2.insert_text(fitz.Point(50, 165), "Customer records must be retained for a maximum of five years unless a legal requirement requires a longer period.", fontsize=11, fontname="helv")

    # Section 5
    page2.insert_text(fitz.Point(50, 220), "5. Security", fontsize=14, fontname="helv", color=(0.15, 0.2, 0.4))
    page2.insert_text(fitz.Point(50, 245), "Employees must use company-approved systems.", fontsize=11, fontname="helv")

    doc.save(pdf_path)
    doc.close()
    print(f"Successfully generated demo policy PDF at: {pdf_path}")

if __name__ == "__main__":
    generate_test_policy_pdf()
