from datetime import datetime, timedelta
from dataclasses import dataclass


def decimal_year_to_date(decimal_year):
    """
    Converts a decimal year to a date in the format '%Y-%m-%d'.

    Args:
      decimal_year (float): The decimal year to convert.

    Returns:
      str: The date in the format '%Y-%m-%d'.

    Examples:
      >>> decimal_year_to_date(2020.5)
      '2020-07-02'
    """
    year = int(decimal_year)
    remainder = decimal_year - year
    start_of_year = datetime(year, 1, 1)
    end_of_year = datetime(year + 1, 1, 1)
    days_in_year = (end_of_year - start_of_year).days
    days = remainder * days_in_year
    date = start_of_year + timedelta(days=days)
    return date.strftime('%Y-%m-%d')

def date_to_decimal_year(date_str):
    """
    Converts a date in the format '%Y-%m-%d' to a decimal year.

    Args:
      date_str (str): The date in the format '%Y-%m-%d'.

    Returns:
      float: The decimal year.

    Examples:
      >>> date_to_decimal_year('2020-07-02')
      2020.5
    """
    date = datetime.strptime(date_str, '%Y-%m-%d')
    year = date.year
    start_of_year = datetime(year, 1, 1)
    end_of_year = datetime(year + 1, 1, 1)
    days_in_year = (end_of_year - start_of_year).days
    days_passed = (date - start_of_year).days
    decimal_year = year + days_passed / days_in_year
    return decimal_year


@dataclass
class Taxon:
    """
    Dataclass representing a taxon.

    Attributes:
      id (str): The id of the taxon.
      sequence (str): The sequence of the taxon.
      date (float): The date of the taxon.
      uncertainty (float): The uncertainty of the taxon's date.
    """
    id: str
    sequence: str
    date: float
    uncertainty: float = 0.0


def taxa_from_fasta(fasta_path, date_delimiter="|", date_index=-1):
    """
    Parses a fasta file into a list of Taxon objects.

    Args:
      fasta_path (Path): The path to the fasta file.
      date_delimiter (str): The delimiter for the date in the fasta header.
      date_index (int): The index of the date in the fasta header.

    Returns:
      List[Taxon]: A list of Taxon objects representing the taxa in the fasta file.

    Raises:
      ValueError: If the fasta file is invalid.
    """
    # Read the fasta file
    with open(fasta_path) as fasta_file:
        fasta_lines = fasta_file.readlines()

    # check if valid fasta
    if not fasta_lines[0].startswith(">"):
        raise ValueError("Invalid fasta file.")
    # Parse the fasta file into Taxon objects. Support multi-line sequences.
    taxa = []
    for line in fasta_lines:
        if line.startswith(">"):
            header = line[1:].strip()
            # 1992-XX-XX
            date_with_uncertainty = header.split(date_delimiter)[date_index].lower().strip()
            uncertainty = None
            if date_with_uncertainty.endswith("-xx-xx"):
                uncertainty = 1 # 1 year
            elif date_with_uncertainty.endswith("-xx"):
                uncertainty = 0.0833 # 1 month
            date = date_with_uncertainty.replace("xx", "01")
            try:
                date = date_to_decimal_year(date)
            except ValueError:
                raise ValueError(f"Invalid date in header: {header}")
            taxa.append(Taxon(id=header, sequence="", date=float(date), uncertainty=uncertainty))
        else:
            taxa[-1].sequence += line.strip()

    return taxa