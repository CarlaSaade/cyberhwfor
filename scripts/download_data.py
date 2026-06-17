"""Download NSL-KDD train and test files into data/."""

from pathlib import Path
import urllib.request

URLS = {
    "KDDTrain+.txt": "https://raw.githubusercontent.com/jmnwong/NSL-KDD-Dataset/master/KDDTrain%2B.txt",
    "KDDTest+.txt": "https://raw.githubusercontent.com/jmnwong/NSL-KDD-Dataset/master/KDDTest%2B.txt",
}


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    data_dir = project_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    for filename, url in URLS.items():
        target = data_dir / filename
        relative_target = Path("data") / filename
        if target.exists() and target.stat().st_size > 0:
            print(f"Skipping existing file: {relative_target}")
            continue
        print(f"Downloading {filename}...")
        urllib.request.urlretrieve(url, target)
        print(f"Saved to {relative_target}")


if __name__ == "__main__":
    main()
