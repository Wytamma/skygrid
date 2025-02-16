from pathlib import Path
import typer

def main(alignment: Path, output: Path):
    samples = []
    with open(alignment) as f:
        for line in f:
            if line.startswith(">"):
                samples.append(line.strip().lstrip(">"))
    with open(output, "w") as f:
        f.write("strain\tdate\n")
        for seq_name in samples:
            date = seq_name.split("|")[-1]
            if "/" in date:
                # ignore uncertainty in the date
                date = date.split("/")[0]
            f.write(f"{seq_name}\t{date}\n")

if __name__ == "__main__":
    typer.run(main)