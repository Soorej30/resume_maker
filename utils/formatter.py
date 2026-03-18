import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Optional, Tuple, Union

PathLike = Union[str, Path]

ACTUAL_RESUME_LATEX = r"""
\documentclass[letterpaper,11pt]{article}

\usepackage{latexsym}
\usepackage[hidelinks]{hyperref}
\usepackage[english]{babel}
\usepackage{tabularx}
\pagestyle{empty}

\addtolength{\oddsidemargin}{-0.75in}
\addtolength{\evensidemargin}{-0.75in}
\addtolength{\textwidth}{1.5in}
\addtolength{\topmargin}{-0.75in}
\addtolength{\textheight}{1.5in}

\urlstyle{same}
\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

\newcommand{\resumeItem}[1]{
  \item\normalsize{
    {#1 \vspace{0pt}}
  }
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{0pt}
}

\newcommand{\resumeProjectHeading}[2]{
    \vspace{-2pt}\item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \small#1 & #2 \\
    \end{tabular*}\vspace{0pt}
}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}\vspace{0pt}}
\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{0pt}}

\begin{document}
\begin{center}
    \textbf{\Huge \scshape {{name}}} \\ \vspace{2pt}
    \small {{contact_line}}
\end{center}

\vspace{-19pt}

\section*{EDUCATION}

\newcommand{\eduentry}[4]{%
  \noindent
  \begin{tabularx}{\linewidth}{@{}X r@{}}
    \textbf{#1} & #2 \\
    #3 & #4 \\
  \end{tabularx}
  \vspace{-2pt}
}

\eduentry
{University of Colorado, Boulder}
{Aug 2025 -- May 2027}
{Master of Science in Data Science \;|\; GPA: 4.00}
{Boulder, CO}

\eduentry
{Birla Institute of Technology and Science, Pilani}
{Aug 2017 -- May 2021}
{Bachelor of Engineering in Computer Science}
{Pilani, India}

\vspace{-12pt}

\section{Technical Skills}
\begin{itemize}
\small{\item{
\textbf{Skills}{: {{skills_line}}}
}}
\end{itemize}
\vspace{-12pt}

{{summary_section}}

\section{Experience}
\resumeSubHeadingListStart
{{experience}}
\resumeSubHeadingListEnd
\vspace{-12pt}

\section{Projects}
\resumeSubHeadingListStart
{{projects}}
\resumeSubHeadingListEnd

\end{document}
"""


LATEX_SPECIAL_CHARS = {
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


def escape_latex(text):
    text = "" if text is None else str(text)
    for char, replacement in LATEX_SPECIAL_CHARS.items():
        text = text.replace(char, replacement)
    return text


def _clean_items(items):
    return [str(item).strip() for item in items if str(item).strip()]


def _format_contact_line(data):
    parts = []
    phone = str(data.get("phone", "")).strip()
    email = str(data.get("email", "")).strip()
    links = str(data.get("links", "")).strip()

    if phone:
        parts.append(escape_latex(phone))
    if email:
        escaped_email = escape_latex(email)
        parts.append(rf"\href{{mailto:{escaped_email}}}{{\underline{{{escaped_email}}}}}")

    if links:
        raw_links = [piece.strip() for piece in links.replace("\n", "|").split("|") if piece.strip()]
        for link in raw_links:
            escaped_link = escape_latex(link)
            href_target = link if link.startswith(("http://", "https://")) else f"https://{link}"
            parts.append(rf"\href{{{href_target}}}{{\underline{{{escaped_link}}}}}")

    return " $|$ ".join(parts) if parts else ""


def _format_summary_section(summary):
    if not str(summary).strip():
        return ""
    return (
        "\\section{Summary}\n"
        f"{escape_latex(summary)}\n\n"
        "\\vspace{-8pt}\n"
    )


def _format_skills_line(skills):
    return ", ".join(escape_latex(skill) for skill in _clean_items(skills))


def format_experience(experiences):
    blocks = []
    for exp in experiences:
        role = escape_latex(exp.get("role", ""))
        company = escape_latex(exp.get("company", ""))
        bullets = "\n".join(
            [f"\\resumeItem{{{escape_latex(bullet)}}}" for bullet in _clean_items(exp.get("bullets", []))]
        )
        block = (
            "\\resumeSubheading\n"
            f"{{{role}}}{{}}\n"
            f"{{{company}}}{{}}\n"
            "\\resumeItemListStart\n"
            f"{bullets}\n"
            "\\resumeItemListEnd"
        )
        blocks.append(block)
    return "\n".join(blocks)


def format_projects(projects):
    blocks = []
    for proj in projects:
        name = escape_latex(proj.get("name", ""))
        bullets = "\n".join(
            [f"\\resumeItem{{{escape_latex(bullet)}}}" for bullet in _clean_items(proj.get("bullets", []))]
        )
        block = (
            "\\resumeProjectHeading\n"
            f"{{\\textbf{{{name}}}}}{{}}\n"
            "\\resumeItemListStart\n"
            f"{bullets}\n"
            "\\resumeItemListEnd"
        )
        blocks.append(block)
    return "\n".join(blocks)


def generate_latex(data, template_path=None):
    latex = ACTUAL_RESUME_LATEX

    latex = latex.replace("{{contact_line}}", _format_contact_line(data))
    latex = latex.replace("{{skills_line}}", _format_skills_line(data.get("skills", [])))
    latex = latex.replace("{{summary_section}}", _format_summary_section(data.get("summary", "")))
    latex = latex.replace("{{experience}}", format_experience(data.get("experience", [])))
    latex = latex.replace("{{projects}}", format_projects(data.get("projects", [])))

    return latex


def write_latex(latex: str, output_path: PathLike) -> Path:
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(latex, encoding="utf-8")
    return target


def compile_pdf(latex: str, output_dir: PathLike, job_name: str = "tailored_resume") -> Tuple[Optional[Path], Path]:
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    tex_path = write_latex(latex, output_root / f"{job_name}.tex")

    pdflatex_path = shutil.which("pdflatex")
    if not pdflatex_path:
        return None, tex_path

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        temp_tex = temp_path / tex_path.name
        temp_pdf = temp_path / f"{job_name}.pdf"
        temp_tex.write_text(latex, encoding="utf-8")
        latex_env = dict(os.environ)
        latex_env["TEXMFVAR"] = str(temp_path / ".texmf-var")
        latex_env["VARTEXFONTS"] = str(temp_path / ".texfonts")
        Path(latex_env["TEXMFVAR"]).mkdir(parents=True, exist_ok=True)
        Path(latex_env["VARTEXFONTS"]).mkdir(parents=True, exist_ok=True)

        last_output = ""
        for _ in range(2):
            result = subprocess.run(
                [pdflatex_path, "-interaction=nonstopmode", temp_tex.name],
                cwd=temp_path,
                check=False,
                capture_output=True,
                text=True,
                env=latex_env,
            )
            last_output = (result.stdout or "") + "\n" + (result.stderr or "")
            if result.returncode != 0 and not temp_pdf.exists():
                preview = "\n".join(last_output.strip().splitlines()[-20:])
                raise RuntimeError(
                    "pdflatex failed while compiling the generated resume.\n"
                    f"TeX file: {tex_path}\n"
                    f"Last log lines:\n{preview}"
                )

        pdf_path = output_root / f"{job_name}.pdf"
        if not temp_pdf.exists():
            preview = "\n".join(last_output.strip().splitlines()[-20:])
            raise RuntimeError(
                "pdflatex finished without producing a PDF.\n"
                f"TeX file: {tex_path}\n"
                f"Last log lines:\n{preview}"
            )
        pdf_path.write_bytes(temp_pdf.read_bytes())
        return pdf_path, tex_path
