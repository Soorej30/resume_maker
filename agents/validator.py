from pathlib import Path

from config import DEFAULT_VALIDATION_MODEL, VALIDATOR_PROMPT_PATH
from prompts.formatter import build_validation_prompt
from utils.llm import call_llm


def _load_extra_instructions(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def validate_resume(resume: str, job_desc: str) -> str:
    prompt = build_validation_prompt(resume, job_desc)
    extra = _load_extra_instructions(VALIDATOR_PROMPT_PATH)
    if extra:
        prompt = f"{prompt}\n\nAdditional review instructions:\n{extra}"
    return call_llm(prompt, model=DEFAULT_VALIDATION_MODEL)
