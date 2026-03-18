from urllib.parse import urlparse


def _validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(
            f"Invalid job URL: {url}. Provide a full http:// or https:// job posting URL."
        )

def _clean_html(html: str) -> str:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    lines = [line.strip() for line in soup.get_text(separator="\n").splitlines()]
    cleaned = [line for line in lines if line]
    return "\n".join(cleaned).strip()


def scrape_job(job_url: str) -> str:
    import requests

    _validate_url(job_url)
    response = requests.get(
        job_url,
        timeout=20,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
        },
    )
    response.raise_for_status()
    job_text = _clean_html(response.text)
    if not job_text:
        raise ValueError(f"No readable job description content was found at {job_url}")
    return job_text
