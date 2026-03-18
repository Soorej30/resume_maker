import json
import re
from argparse import ArgumentParser

from agents.rewriter import rewrite_resume
from agents.validator import validate_resume
from config import (
    DEFAULT_MAX_ITERS,
    DEFAULT_VALIDATION_THRESHOLD,
    OUTPUT_DIR,
)
from utils.formatter import compile_pdf, generate_latex
from utils.parser import parse_resume
from utils.scraper import scrape_job


def _extract_json_block(payload: str) -> str:
    cleaned = payload.strip()
    if not cleaned:
        raise ValueError("Model response was empty.")

    fenced_match = re.search(r"```(?:json)?\s*(.*?)```", cleaned, flags=re.DOTALL)
    if fenced_match:
        cleaned = fenced_match.group(1).strip()

    if cleaned.startswith("{") or cleaned.startswith("["):
        return cleaned

    start_positions = [pos for pos in (cleaned.find("{"), cleaned.find("[")) if pos != -1]
    if not start_positions:
        preview = cleaned[:300].replace("\n", " ")
        raise ValueError(f"Model response did not contain JSON. Response preview: {preview}")

    start = min(start_positions)
    opening = cleaned[start]
    closing = "}" if opening == "{" else "]"
    depth = 0

    for index in range(start, len(cleaned)):
        char = cleaned[index]
        if char == opening:
            depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0:
                return cleaned[start : index + 1]

    preview = cleaned[:300].replace("\n", " ")
    raise ValueError(f"Found the start of JSON but not a complete object. Response preview: {preview}")


def _extract_json(payload: str):
    json_payload = _extract_json_block(payload)
    try:
        return json.loads(json_payload)
    except json.JSONDecodeError as exc:
        preview = json_payload[:300].replace("\n", " ")
        raise ValueError(
            f"Model response was not valid JSON: {exc}. Response preview: {preview}"
        ) from exc


def run_pipeline_logic(resume_text: str, job_desc: str, max_iters: int = DEFAULT_MAX_ITERS):
    current_resume = resume_text
    rewritten = None

    for i in range(max_iters):
        print(f"\nIteration {i+1}")

        rewritten = rewrite_resume(current_resume, job_desc)
        validation = validate_resume(rewritten, job_desc)
        validation_json = _extract_json(validation)

        score = int(validation_json.get("score", 0))
        print("Score:", score)

        if score >= DEFAULT_VALIDATION_THRESHOLD:
            return rewritten

        feedback = json.dumps(validation_json, indent=2)
        current_resume = (
            f"{rewritten}\n\nImprove this resume JSON using the reviewer feedback below:\n{feedback}"
        )

    return rewritten


def run_pipeline(resume_path: str, job_url: str, max_iters: int = DEFAULT_MAX_ITERS):
    resume_text = parse_resume(resume_path)
    job_desc = scrape_job(job_url)

    final_resume = run_pipeline_logic(resume_text, job_desc, max_iters=max_iters)
    if not final_resume:
        raise RuntimeError("Resume generation failed before any rewrite was produced.")

    structured = _extract_json(final_resume)

    latex = generate_latex(structured)
    pdf_path, tex_path = compile_pdf(latex, OUTPUT_DIR)

    return {
        "structured": structured,
        "latex": latex,
        "pdf_path": str(pdf_path) if pdf_path else None,
        "tex_path": str(tex_path),
    }


def build_arg_parser():
    parser = ArgumentParser(description="Tailor a resume to a target job posting URL.")
    parser.add_argument("resume_path", help="Path to a source resume file (.pdf, .docx, .txt, .md)")
    parser.add_argument(
        "job_url",
        help="Full job posting URL to scrape for the target job description.",
    )
    parser.add_argument(
        "--max-iters",
        type=int,
        default=DEFAULT_MAX_ITERS,
        help=f"Maximum rewrite/validate iterations (default: {DEFAULT_MAX_ITERS})",
    )
    return parser


def main():
    parser = build_arg_parser()
    args = parser.parse_args()
    result = run_pipeline(args.resume_path, args.job_url, max_iters=args.max_iters)

    print(f"LaTeX written to: {result['tex_path']}")
    if result["pdf_path"]:
        print(f"PDF generated: {result['pdf_path']}")
    else:
        print("PDF was not generated because `pdflatex` is not installed. The .tex file is ready.")


if __name__ == "__main__":
    main()
