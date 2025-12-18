import requests
from openai import OpenAI
from PyPDF2 import PdfReader
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

with open("prompt.txt", "r") as file1:
    prompt = file1.read()

# with open("api_key_2.txt", "r") as file2:
#     api_key = file2.read()

resume_text = ""
for page in PdfReader("Soorej resume 2025-10-21.pdf").pages:
    resume_text += page.extract_text()

with open("job_description.txt", "r") as file3:
    job_description = file3.read()

prompt = prompt.format(resume_text = resume_text, job_description = job_description)
print(prompt)

def ollama_chat(prompt):
    r = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.1:8b",
            "prompt": prompt,
            "stream": False
        }
    )
    return r.json()["response"]

optimized_resume_text = ollama_chat(prompt)

# client = OpenAI(api_key = api_key)
# response = client.chat.completions.create(
#     model="gpt-4o",
#     messages=[{"role": "user", "content": prompt}]
# )

# optimized_resume_text = response.choices[0].message.content

print("*******************___________________***********************")
print(optimized_resume_text)
print("*******************___________________***********************")

def text_to_pdf(text, filename="new_resume.pdf"):
    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()
    story = [Paragraph(line, styles["Normal"]) for line in text.split("\n") if line.strip()]
    doc.build(story)

text_to_pdf(optimized_resume_text)