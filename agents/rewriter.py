from pathlib import Path

from config import DEFAULT_REWRITE_MODEL, REWRITER_PROMPT_PATH
from prompts.formatter import build_rewrite_prompt
from utils.llm import call_llm


def _load_extra_instructions(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def rewrite_resume(resume: str, job_desc: str) -> str:
    instructions = _load_extra_instructions(REWRITER_PROMPT_PATH)
    prompt = build_rewrite_prompt(resume, job_desc, instructions=instructions)
    return call_llm(prompt, model=DEFAULT_REWRITE_MODEL)
