import requests
import re
import json
import subprocess
from pdflatex import PDFLaTeX

def latex_escape(text):
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }

    for char, replacement in replacements.items():
        text = text.replace(char, replacement)

    return text

def ollama_chat(prompt):
    schema = {
    "type": "object",
    "properties": {
        "bullets": {
            "type": "array",
            "items": {
                "type": "string",
                "description": "A single rewritten resume bullet point"
            }
        }
    },
    "required": ["bullets"]
}
    r = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.1:8b",
            "prompt": prompt,
            "stream": False,
            "format": schema
        }
    )
    return r.json()["response"]


with open("prompt.txt", "r") as file1:
    prompt = file1.read()

RESUME_TEX_PATH = "resume.tex"
with open(RESUME_TEX_PATH, "r") as f:
    latex_resume = f.read()

with open("job_description.txt", "r") as file3:
    job_description = file3.read()

items = re.findall(r'\\resumeItem\{(.*?)\}', latex_resume, re.DOTALL)
items = [item for item in items if len(item) > 10]

print(f"Found {len(items)} bullet points to optimize...")

prompt = prompt.format(resume_items = chr(10).join(items), job_description = job_description)

optimized_resume_text = ollama_chat(prompt)

new_points = json.loads(optimized_resume_text)

new_resume = latex_resume
new_points["bullets"] = [latex_escape(t) for t in new_points["bullets"]]

for old, new in zip(items, new_points["bullets"]):
    new_resume = new_resume.replace(old, new)

new_resume_tex = 'tailored_resume.tex'
new_resume_pdf = 'tailored_resume.pdf'

with open(new_resume_tex, "w") as f:
    f.write(new_resume)
