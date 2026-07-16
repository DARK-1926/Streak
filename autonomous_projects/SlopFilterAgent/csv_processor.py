import csv
import io
from typing import Dict, List


def parse_csv_content(input_stream: io.TextIOBase, text_column: str = "text") -> List[Dict[str, str]]:
    """
    Parse CSV content from a text stream using Dependency Injection.

    Args:
        input_stream: A text stream (e.g., io.StringIO) containing CSV data.
        text_column: The name of the column containing the text to be analyzed.

    Returns:
        A list of dictionaries representing the CSV rows.

    Raises:
        TypeError: If the input stream is not an instance of io.TextIOBase.
        ValueError: If the text column is missing from the CSV headers.
        csv.Error: If there is an error parsing the CSV data.
    """
    if not isinstance(input_stream, io.TextIOBase):
        raise TypeError("input_stream must be an instance of io.TextIOBase")

    reader = csv.DictReader(input_stream)

    if reader.fieldnames is None or text_column not in reader.fieldnames:
        raise ValueError(f"Required column '{text_column}' not found in CSV headers.")

    parsed_data: List[Dict[str, str]] = []
    try:
        for row in reader:
            parsed_data.append(row)
    except csv.Error as e:
        raise csv.Error(f"Error parsing CSV content: {e}")

    return parsed_data


def format_csv_content(comments: List[Dict[str, str]], output_stream: io.TextIOBase) -> None:
    """
    Format and write a list of dictionaries to a CSV text stream.

    Args:
        comments: A list of dictionaries representing the CSV rows to write.
        output_stream: A text stream (e.g., io.StringIO) to write the CSV data to.

    Raises:
        TypeError: If the output stream is not an instance of io.TextIOBase.
        csv.Error: If there is an error writing the CSV data.
    """
    if not isinstance(output_stream, io.TextIOBase):
        raise TypeError("output_stream must be an instance of io.TextIOBase")

    if not comments:
        return

    fieldnames = list(comments[0].keys())
    writer = csv.DictWriter(output_stream, fieldnames=fieldnames)

    try:
        writer.writeheader()
        writer.writerows(comments)
    except csv.Error as e:
        raise csv.Error(f"Error writing CSV content: {e}")