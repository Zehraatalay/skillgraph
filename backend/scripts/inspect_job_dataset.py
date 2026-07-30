from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_DIRECTORY = PROJECT_ROOT / "data" / "jobs"


def find_dataset_files() -> list[Path]:
    supported_extensions = {
        ".csv",
        ".json",
        ".jsonl",
        ".parquet",
        ".xlsx",
    }

    return sorted(
        file_path
        for file_path in DATASET_DIRECTORY.rglob("*")
        if (
            file_path.is_file()
            and file_path.suffix.lower()
            in supported_extensions
        )
    )


def load_dataset(file_path: Path) -> pd.DataFrame:
    extension = file_path.suffix.lower()

    if extension == ".csv":
        return pd.read_csv(file_path)

    if extension == ".json":
        try:
            return pd.read_json(file_path)
        except ValueError:
            return pd.read_json(
                file_path,
                lines=True,
            )

    if extension == ".jsonl":
        return pd.read_json(
            file_path,
            lines=True,
        )

    if extension == ".parquet":
        return pd.read_parquet(file_path)

    if extension == ".xlsx":
        return pd.read_excel(file_path)

    raise ValueError(
        f"Unsupported dataset format: {extension}"
    )


def print_value_preview(
    dataframe: pd.DataFrame,
    column_name: str,
    sample_count: int = 5,
) -> None:
    print(f"\nCOLUMN PREVIEW: {column_name}")
    print("-" * 80)

    non_null_values = (
        dataframe[column_name]
        .dropna()
        .astype(str)
        .head(sample_count)
    )

    if non_null_values.empty:
        print("No non-null values.")
        return

    for index, value in enumerate(
        non_null_values,
        start=1,
    ):
        shortened_value = (
            value
            if len(value) <= 500
            else value[:500] + "..."
        )

        print(f"\nSample {index}:")
        print(shortened_value)


def inspect_dataframe(
    dataframe: pd.DataFrame,
    file_path: Path,
) -> None:
    print("\n" + "=" * 80)
    print(f"FILE: {file_path.name}")
    print(f"PATH: {file_path}")
    print("=" * 80)

    print(f"\nRows: {len(dataframe):,}")
    print(f"Columns: {len(dataframe.columns)}")

    print("\nCOLUMN NAMES")
    print("-" * 80)

    for column_name in dataframe.columns:
        print(f"- {column_name}")

    print("\nDATA TYPES")
    print("-" * 80)
    print(dataframe.dtypes.to_string())

    print("\nMISSING VALUES")
    print("-" * 80)

    missing_values = (
        dataframe.isna()
        .sum()
        .sort_values(ascending=False)
    )

    missing_percentages = (
        dataframe.isna()
        .mean()
        .mul(100)
        .round(2)
    )

    missing_summary = pd.DataFrame(
        {
            "missing_count": missing_values,
            "missing_percentage": (
                missing_percentages[
                    missing_values.index
                ]
            ),
        }
    )

    print(missing_summary.to_string())

    print("\nDUPLICATE ROWS")
    print("-" * 80)
    print(
        dataframe.duplicated().sum()
    )

    print("\nFIRST 3 ROWS")
    print("-" * 80)
    print(
        dataframe.head(3).to_string(
            index=False,
        )
    )

    likely_columns = [
        column_name
        for column_name in dataframe.columns
        if any(
            keyword in column_name.lower()
            for keyword in [
                "title",
                "description",
                "skill",
                "company",
                "location",
                "job",
            ]
        )
    ]

    for column_name in likely_columns:
        print_value_preview(
            dataframe,
            column_name,
        )

    print("\nUNIQUE VALUE COUNTS")
    print("-" * 80)

    for column_name in dataframe.columns:
        unique_count = (
            dataframe[column_name]
            .nunique(dropna=True)
        )

        print(
            f"{column_name}: "
            f"{unique_count:,}"
        )


def main() -> None:
    if not DATASET_DIRECTORY.exists():
        raise FileNotFoundError(
            "Dataset directory does not exist: "
            f"{DATASET_DIRECTORY}"
        )

    dataset_files = find_dataset_files()

    if not dataset_files:
        raise FileNotFoundError(
            "No supported dataset files were found "
            f"inside {DATASET_DIRECTORY}"
        )

    print("Dataset files found:")

    for file_path in dataset_files:
        print(f"- {file_path.name}")

    for file_path in dataset_files:
        try:
            dataframe = load_dataset(file_path)

            inspect_dataframe(
                dataframe,
                file_path,
            )
        except Exception as error:
            print("\n" + "!" * 80)
            print(
                f"Could not inspect "
                f"{file_path.name}: {error}"
            )
            print("!" * 80)


if __name__ == "__main__":
    main()