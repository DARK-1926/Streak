import os
import time
import datetime
from typing import Dict, Any, Tuple
from io import BytesIO

# The following imports require external libraries that must be installed
# in your local environment. Install them with:
#   pip install transformers fpdf
# If you prefer a different lightweight LLM, replace the imports and
# loading logic accordingly.
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
except ImportError as e:
    raise ImportError(
        "Missing required library 'transformers'. "
        "Install it with: pip install transformers"
    ) from e

try:
    from fpdf import FPDF
except ImportError as e:
    raise ImportError(
        "Missing required library 'fpdf'. "
        "Install it with: pip install fpdf"
    ) from e


def load_local_llm() -> Tuple[Any, Any]:
    """
    Load a lightweight local language model from disk.

    The function attempts to load a TinyLlama or similar model from a
    predefined directory. The model must be downloaded manually and
    extracted into the ``model_dir``. If the model files are not found,
    a clear error message is raised with instructions.

    Returns
    -------
    tuple
        A tuple containing the tokenizer and the model pipeline ready
        for text generation.

    Notes
    -----
    - Replace ``model_dir`` with the actual path where your model is
      stored.
    - Ensure that the model files are compatible with the
      ``transformers`` library.
    """
    # Placeholder path – replace with the actual location of your model
    model_dir = "./models/tinylm"

    if not os.path.isdir(model_dir):
        raise FileNotFoundError(
            f"Model directory '{model_dir}' not found. "
            "Please download a TinyLlama or similar model and "
            "extract it to this path. "
            "You can find models at https://github.com/facebookresearch/TinyLlama."
        )

    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForCausalLM.from_pretrained(model_dir)

    # Create a generation pipeline
    generator = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        device=0 if torch.cuda.is_available() else -1,
    )

    return tokenizer, generator


def generate_proposal_section(prompt: str, timeout: int = 30, max_retries: int = 3) -> str:
    """
    Generate a proposal section using the local LLM.

    Parameters
    ----------
    prompt : str
        The prompt to send to the language model.
    timeout : int, optional
        Maximum number of seconds allowed for a single generation attempt.
        Default is 30 seconds.
    max_retries : int, optional
        Number of retry attempts if generation fails. Default is 3.

    Returns
    -------
    str
        The generated proposal section.

    Raises
    ------
    RuntimeError
        If all retry attempts fail or if a timeout occurs.
    """
    tokenizer, generator = load_local_llm()

    for attempt in range(1, max_retries + 1):
        start_time = time.time()
        try:
            # The generator returns a list of dicts; we take the first one
            result = generator(
                prompt,
                max_new_tokens=512,
                do_sample=True,
                top_k=50,
                top_p=0.95,
                temperature=0.7,
                return_full_text=False,
            )
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise TimeoutError(f"Generation exceeded {timeout}s timeout.")
            return result[0]["generated_text"]
        except Exception as exc:
            if attempt == max_retries:
                raise RuntimeError(
                    f"Failed to generate proposal section after {max_retries} attempts: {exc}"
                ) from exc
            # Exponential backoff before retrying
            backoff = 2 ** attempt
            time.sleep(backoff)


def calculate_eligibility(data: Dict[str, Any]) -> int:
    """
    Compute a simple eligibility score based on user-provided data.

    The heuristic awards points as follows:
    - 1 point per year in business, capped at 5 points.
    - 1 point per 10 employees, capped at 5 points.
    - 2 points per prior federal contract, capped at 3 contracts.

    Parameters
    ----------
    data : dict
        Dictionary containing at least the keys:
        - 'years_in_business' (int)
        - 'employee_count' (int)
        - 'prior_federal_contracts' (int)

    Returns
    -------
    int
        Total eligibility score.
    """
    years = int(data.get("years_in_business", 0))
    employees = int(data.get("employee_count", 0))
    contracts = int(data.get("prior_federal_contracts", 0))

    years_score = min(years, 5)
    employees_score = min(employees // 10, 5)
    contracts_score = min(contracts, 3) * 2

    return years_score + employees_score + contracts_score


def render_pdf(proposal_text: str, metadata: Dict[str, Any]) -> bytes:
    """
    Render a PDF containing the proposal text and metadata.

    Parameters
    ----------
    proposal_text : str
        The full proposal content to include in the PDF.
    metadata : dict
        Dictionary of metadata fields (e.g., title, author, date).

    Returns
    -------
    bytes
        The PDF content as a byte stream.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Title
    title = metadata.get("title", "Grant Proposal")
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, title, ln=True, align="C")

    # Metadata block
    pdf.set_font("Helvetica", "", 12)
    for key, value in metadata.items():
        if key.lower() == "title":
            continue
        pdf.cell(0, 8, f"{key.title()}: {value}", ln=True)

    pdf.ln(10)  # Add space before proposal content

    # Proposal content
    pdf.set_font("Helvetica", "", 12)
    # Split the proposal text into lines that fit the page width
    lines = proposal_text.splitlines()
    for line in lines:
        pdf.multi_cell(0, 6, line)

    # Output to bytes
    pdf_bytes = pdf.output(dest="S").encode("latin1")
    return pdf_bytes


def deadline_countdown(target_date: str) -> str:
    """
    Return a human‑readable countdown string to a target date.

    Parameters
    ----------
    target_date : str
        Target date in ISO format (YYYY-MM-DD). Time component is optional
        and defaults to 00:00:00.

    Returns
    -------
    str
        Countdown string such as "12 days left" or "Deadline passed".
    """
    try:
        target_dt = datetime.datetime.fromisoformat(target_date)
    except ValueError:
        raise ValueError(
            f"Invalid date format: '{target_date}'. "
            "Expected ISO format 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:MM:SS'."
        )

    now = datetime.datetime.now(target_dt.tzinfo)
    delta = target_dt - now

    if delta.total_seconds() <= 0:
        return "Deadline passed"

    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes = remainder // 60

    parts = []
    if days > 0:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")

    return ", ".join(parts) + " left"


__all__ = [
    "load_local_llm",
    "generate_proposal_section",
    "calculate_eligibility",
    "render_pdf",
    "deadline_countdown",
]