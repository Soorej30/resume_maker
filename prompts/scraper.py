from textwrap import dedent


def build_job_summary_prompt(job_text: str) -> str:
    return dedent(
        f"""
        You are extracting signal from a job description for resume tailoring.

        Return valid JSON with this schema:
        {{
          "title": "",
          "company": "",
          "must_have_skills": [],
          "preferred_skills": [],
          "responsibilities": [],
          "ats_keywords": []
        }}

        Keep the output grounded in the source text only.

        Job Description:
        {job_text}
        """
    ).strip()
