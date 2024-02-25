import pandas as pd
import numpy as np
from typing import Type, TypeVar, Dict, Any
import os
import shutil
from datetime import datetime

from .io import create_package_directory

T = TypeVar("T")


class SchemaMismatchError(Exception):
    pass


class ColumnTypeError(Exception):
    pass


class GenericDataFrame:
    df: pd.DataFrame

    def __init__(self, column_types: Dict[str, Type], key_column: str):
        self.column_types = column_types
        self.key_column = key_column
        self.df = self.create_empty_dataframe()

    def create_empty_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(
            {
                col: pd.Series(dtype=self.map_type_to_pandas(ptype))
                for col, ptype in self.column_types.items()
            }
        )

    @staticmethod
    def map_type_to_pandas(python_type: Type) -> str:
        pandas_type_mapping = {
            str: "object",
            int: "int64",
            float: "float64",
            bool: "bool",
            np.float64: "float64",
            np.int64: "int64",
            datetime: "datetime64[ns]",
            "category": "category",
        }
        return pandas_type_mapping.get(python_type, "object")

    def validate_schema(self, data: pd.DataFrame):
        if set(data.columns) != set(self.column_types.keys()):
            raise SchemaMismatchError("DataFrame schema does not match expected schema")

        for column, expected_type in self.column_types.items():
            if not pd.api.types.is_dtype_equal(
                data[column].dtype, pd.Series([0], dtype=expected_type).dtype
            ):
                raise ColumnTypeError(f"Column {column} type mismatch")

    def load_and_append(self, filename: str) -> None:
        full_path = self._gen_path(filename)

        if not os.path.exists(full_path):
            return

        loaded_df = pd.read_parquet(full_path)
        self.validate_schema(loaded_df)
        self.df = pd.concat([self.df, loaded_df], ignore_index=True)

    def is_duplicate(self, key: Any) -> bool:
        return key in self.df[self.key_column].values

    def add_row(self, row_data: Dict[str, Any], force: bool = False) -> None:
        if not isinstance(row_data, dict):
            raise TypeError("row_data must be a dictionary")

        key_exists = row_data[self.key_column] in self.df[self.key_column]
        if key_exists and not force:
            raise ValueError("Duplicate key has been found")

        self.validate_schema(pd.DataFrame([row_data]))

        new_row = pd.DataFrame([row_data])
        if key_exists and force:
            index = self.df[self.df[self.key_column] == row_data[self.key_column]].index
            self.df.loc[index] = new_row
        else:
            self.df = pd.concat([self.df, new_row], ignore_index=True)

    def upsert(self, key: str, entries: dict):
        if self.is_duplicate(key):
            self.df.loc[
                self.df[self.key_column] == key, entries.keys()
            ] = entries.values()
        else:
            new_row = pd.DataFrame([{self.key_column: key, **entries}])
            self.df = pd.concat([self.df, new_row], ignore_index=True)

    def get_values(self, key: str, columns: list):
        if key not in self.df[self.key_column].values:
            return None

        row = self.df.loc[self.df[self.key_column] == key, columns]
        return row.to_dict(orient="records")[0]

    def update_cell(self, index: int, column_name: str, value: Any) -> None:
        if column_name not in self.df.columns:
            raise ValueError(f"Column {column_name} does not exist in DataFrame")

        expected_type = self.get_column_types().get(column_name)

        if not isinstance(value, expected_type):
            raise TypeError(f"Value for {column_name} must be of type {expected_type}")

        self.df.at[index, column_name] = value

    def get_default_value(self, python_type: Type):
        default_values = {
            str: "",
            int: 0,
            float: 0.0,
            bool: False,
            datetime: pd.NaT,
        }
        return default_values.get(python_type, np.nan)

    def upsert(self, key_value: str, entries: Dict[str, Any]) -> None:
        if key_value not in self.df[self.key_column].values:
            new_row = {
                col: self.get_default_value(ptype)
                for col, ptype in self.column_types.items()
            }
            new_row[self.key_column] = key_value

            new_row_df = pd.DataFrame(new_row, index=[0])
            self.df = pd.concat([self.df, new_row_df], ignore_index=True)

        for col, value in entries.items():
            self.df.loc[self.df[self.key_column] == key_value, col] = value

    def store(self, filename: str) -> None:
        full_path = self._gen_path(filename)
        backup_directory = create_package_directory("parquet_backups")

        if os.path.exists(full_path):
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            backup_filename = f"{os.path.splitext(filename)[0]}_{timestamp}.parquet"
            backup_path = os.path.join(backup_directory, backup_filename)
            shutil.move(full_path, backup_path)

        self.df.to_parquet(full_path)

    def _gen_path(self, filename: str) -> str:
        filename = f"{os.path.splitext(filename)[0]}.parquet"
        parquet_directory = create_package_directory("parquets")
        return os.path.join(parquet_directory, filename)
