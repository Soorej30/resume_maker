from textwrap import dedent


def build_rewrite_prompt(resume_text: str, job_text: str, instructions: str = "") -> str:
    base_rules = dedent(
        """
        Rewrite the resume so it better matches the job description while staying truthful.

        Return valid JSON in this exact shape:
        {
          "name": "",
          "email": "",
          "phone": "",
          "links": "",
          "summary": "",
          "skills": [],
          "experience": [
            {
              "role": "",
              "company": "",
              "bullets": []
            }
          ],
          "projects": [
            {
              "name": "",
              "bullets": []
            }
          ]
        }

        Rules:
        - Use only facts already present in the resume.
        - Tailor wording and emphasis to the job description.
        - Prefer concise, impact-oriented bullet points.
        - Keep the overall content suitable for a one-page resume.
        - Do not wrap the JSON in markdown fences.
        """
    ).strip()

    extra = instructions.strip()
    if extra:
        extra = f"\nAdditional instructions:\n{extra}"

    return dedent(
        f"""
        {base_rules}
        {extra}

        Source Resume:
        {resume_text}

        Job Description:
        {job_text}
        """
    ).strip()


def build_validation_prompt(resume_json: str, job_text: str) -> str:
    return dedent(
        f"""
        You are a strict resume reviewer.

        Review the tailored resume against the job description. Make sure that the resume is 1 page ONLY if it crosses 1 page, set score to 0.
        Score from 0 to 10 based on relevance, clarity, truthfulness, brevity, and ATS alignment.

        Return valid JSON only:
        {{
          "score": 0,
          "issues": [],
          "suggestions": []
        }}

        Tailored Resume JSON:
        {resume_json}

        Job Description:
        {job_text}
        """
    ).strip()
