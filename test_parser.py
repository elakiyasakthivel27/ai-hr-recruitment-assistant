from recruitment.services.resume_parser import extract_text_from_pdf

pdf_path = "test_resume.pdf"

text = extract_text_from_pdf(pdf_path)

print(text)