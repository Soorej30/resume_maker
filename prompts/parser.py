from textwrap import dedent


def build_resume_json_prompt(resume_text: str) -> str:
    return dedent(
        f"""
        You are a resume parser.

        Convert the source resume text into clean JSON using only facts already present in the resume.
        Do not invent achievements, links, dates, contact info, projects, or metrics.
        If a field is missing, use an empty string or empty list.

        Return valid JSON with this schema:
        {{
          "name": "",
          "email": "",
          "phone": "",
          "links": "",
          "summary": "",
          "skills": [],
          "experience": [
            {{
              "role": "",
              "company": "",
              "bullets": []
            }}
          ],
          "projects": [
            {{
              "name": "",
              "bullets": []
            }}
          ]
        }}

        Resume Text:
        {resume_text}
        """
    ).strip()
