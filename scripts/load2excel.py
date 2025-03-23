"""Load from directory with CSV files to Excel."""

import os
from pathlib import Path
import pandas as pd

def load2excel(data_dir: str | Path) -> None:
    files = os.listdir(data_dir)
    print(f"Files: {files}")

    # one sheet for each file
    with pd.ExcelWriter("output.xlsx") as writer:
        for f in files:
            if f.endswith(".csv"):
                df = pd.read_csv(Path(data_dir, f))
                df.to_excel(writer, sheet_name=f.split(".")[0], index=False)


if __name__ == "__main__":
    load2excel("./tests/fixtures")
