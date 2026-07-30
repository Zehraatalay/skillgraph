from pathlib import Path
import shutil

import kagglehub


def main() -> None:
    print("Downloading Job Skill Set dataset...")

    downloaded_path = Path(
        kagglehub.dataset_download(
            "batuhanmutlu/job-skill-set"
        )
    )

    project_root = Path(__file__).resolve().parent.parent

    destination = (
        project_root
        / "data"
        / "jobs"
    )

    destination.mkdir(
        parents=True,
        exist_ok=True,
    )

    copied_files = []

    for file in downloaded_path.iterdir():
        if file.is_file():
            shutil.copy2(
                file,
                destination / file.name,
            )
            copied_files.append(file.name)

    print("\nDataset downloaded successfully.")
    print(f"Destination: {destination}")

    print("\nCopied files:")

    for file in copied_files:
        print(f" - {file}")


if __name__ == "__main__":
    main()