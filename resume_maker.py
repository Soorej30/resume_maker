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

def ollama_chat(prompt, schema):
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

def create_resume():
    print("Beginning resume optimization.")
    with open("prompts/resume_prompt.txt", "r") as file1:
        prompt = file1.read()

    RESUME_TEX_PATH = "latex_files/resume.tex"
    with open(RESUME_TEX_PATH, "r") as f:
        latex_resume = f.read()

    with open("job_description.txt", "r") as file3:
        job_description = file3.read()

    items = re.findall(r'\\resumeItem\{(.*?)\}', latex_resume, re.DOTALL)
    items = [item for item in items if len(item) > 10]

    print(f"Found {len(items)} bullet points to optimize...")

    prompt = prompt.format(resume_items = chr(10).join(items), job_description = job_description)

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

    optimized_resume_text = ollama_chat(prompt, schema)

    new_points = json.loads(optimized_resume_text)

    new_resume = latex_resume
    new_points["bullets"] = [latex_escape(t) for t in new_points["bullets"]]

    for old, new in zip(items, new_points["bullets"]):
        new_resume = new_resume.replace(old, new)

    new_resume_tex = 'latex_files/tailored_resume.tex'
    # new_resume_pdf = 'latex_files/tailored_resume.pdf'

    with open(new_resume_tex, "w") as f:
        f.write(new_resume)

    print("Resume completed.")

def create_cover_letter():
    print("Beginning cover letter optimization.")
    with open("prompts/cover_letter_prompt.txt", "r") as file1:
        prompt = file1.read()

    COVER_LETTER_TEX_PATH = "latex_files/cover_letter_template.tex"
    with open(COVER_LETTER_TEX_PATH, "r") as f:
        latex_cover_letter = f.read()

    with open("job_description.txt", "r") as file3:
        job_description = file3.read()
    
    with open("resume_dump.txt", "r") as file3:
        resume_dump = file3.read()

    prompt = prompt.format(resume_dump = resume_dump, job_description = job_description)
    schema = {
        "type": "object",
        "properties": {
            "company_name": {
                "type": "string",
                "description": "The company name for which the application is for."
            },
            "opening_paragraph": {
                "type": "string",
                "description": "Opening paragraph introducing the candidate and role. In pure text string format. No special characters."
            },
            "body_paragraph": {
                "type": "string",
                "description": "A body paragraph highlighting relevant experience and skills. In pure text string format. No special characters."
            },
            "closing_paragraph": {
                "type": "string",
                "description": "Closing paragraph expressing interest and next steps. In pure text string format. No special characters."
            }
        },
        "required": [
            "company_name",
            "opening_paragraph",
            "body_paragraph",
            "closing_paragraph"
        ]
    }

    optimized_cover_letter = ollama_chat(prompt, schema)

    new_cover_letter = json.loads(optimized_cover_letter)

    try:
        latex_cover_letter = latex_cover_letter.replace('company_name', latex_escape(new_cover_letter['company_name']['text']))
        latex_cover_letter = latex_cover_letter.replace('opening_paragraph', latex_escape(new_cover_letter['opening_paragraph']['text']))
        latex_cover_letter = latex_cover_letter.replace('body_paragraph', latex_escape(new_cover_letter['body_paragraph']['text']))
        latex_cover_letter = latex_cover_letter.replace('closing_paragraph', latex_escape(new_cover_letter['closing_paragraph']['text']))
    
    except:
        latex_cover_letter = latex_cover_letter.replace('company_name', latex_escape(new_cover_letter['company_name']))
        latex_cover_letter = latex_cover_letter.replace('opening_paragraph', latex_escape(new_cover_letter['opening_paragraph']))
        latex_cover_letter = latex_cover_letter.replace('body_paragraph', latex_escape(new_cover_letter['body_paragraph']))
        latex_cover_letter = latex_cover_letter.replace('closing_paragraph', latex_escape(new_cover_letter['closing_paragraph']))

    new_cover_letter_tex = 'latex_files/tailored_cover_letter.tex'

    with open(new_cover_letter_tex, "w") as f:
        f.write(latex_cover_letter)

    print("Cover letter optimized.")


# create_resume()
create_cover_letter()