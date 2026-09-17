import subprocess
import shutil
from pathlib import Path

from fetch import build_historical_dataset, save_historical_dataset


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def find_rscript() -> str:
    """Find Rscript on PATH or at the standard Windows R install location."""
    rscript = shutil.which("Rscript")
    if rscript:
        return rscript

    installed_rscript = Path(r"C:\Program Files\R\R-4.6.1\bin\Rscript.exe")
    if installed_rscript.exists():
        return str(installed_rscript)

    raise FileNotFoundError(
        "Rscript was not found. Add R's bin folder to PATH or update "
        "the fallback path in data/pipeline.py."
    )


def main():
    # seasons = [f"{year}-{str(year + 1)[-2:]}" for year in range(2010, 2025)]
    # stats_historical = build_historical_dataset(seasons)
    # save_historical_dataset(stats_historical)

    script_path = PROJECT_ROOT / "data" / "mvp_scrape.R"

    subprocess.run(
        [find_rscript(), str(script_path)],
        cwd=PROJECT_ROOT,
        check=True,
    )

if __name__ == "__main__":
    main()