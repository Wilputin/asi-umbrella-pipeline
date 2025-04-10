"""

this simple script transforms csv to parque in the spesific folders
"""
import os
import pathlib
import pandas as pd
import numpy as np

repo_root = pathlib.Path(__file__).parents[0]
folders = [
    repo_root/ "pipeline/data/"]

files = [
    "dynamic_aton",
    "dynamic_sar",
    "dynamic_vessel",
    "dynamic_voyage"
]

source_file_type = ".csv"
destination_file_type = ".parquet"

def run():
    for folder in folders:
        for file in files:
            source_filepath = folder / f"{file}{source_file_type}"
            df = pd.read_csv(source_filepath)
            if file != "dynamic_vessel":
                dest_filepath = folder / f"{file}{destination_file_type}"
                df.to_parquet(dest_filepath, engine="pyarrow")
                size_bytes = os.path.getsize(dest_filepath)
                size_mb = size_bytes / (1024 * 1024)
                print(f"{file} Parquet file size: {size_mb:.2f} MB")
            else:
                chunks = np.array_split(df, 10)
                for i, chunk in enumerate(chunks):
                    dest_filepath  = folder / f"{file}_part{i+1}{destination_file_type}"
                    chunk.to_parquet(dest_filepath,engine="pyarrow")
                    size_bytes = os.path.getsize(dest_filepath)
                    size_mb = size_bytes / (1024 * 1024)

                    print(f"{file} Parquet (part {i+1}) file size: {size_mb:.2f} MB")





if __name__ == "__main__":
    run()