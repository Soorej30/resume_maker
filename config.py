from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
UTILS_DIR = BASE_DIR / "utils"
PROMPTS_DIR = BASE_DIR / "prompts"
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "output"

DEFAULT_REWRITE_MODEL = "llama-3.3-70b-versatile"
DEFAULT_VALIDATION_MODEL = "llama-3.3-70b-versatile"
DEFAULT_MAX_ITERS = 3
DEFAULT_VALIDATION_THRESHOLD = 8

REWRITER_PROMPT_PATH = UTILS_DIR / "rewriter_prompt.txt"
VALIDATOR_PROMPT_PATH = UTILS_DIR / "validate_prompt.txt"
LATEX_TEMPLATE_PATH = TEMPLATES_DIR / "resume.tex"
