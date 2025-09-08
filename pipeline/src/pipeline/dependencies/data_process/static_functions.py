import pandas as pd

def apply_now_to_df(df: pd.DataFrame, column:str="sourcemmsi") -> pd.DataFrame:
    """
    applies now epoch to the source column
    """
    return pd.DataFrame()

def divide_mmsi_and_country_code(df: pd.DataFrame) -> pd.DataFrame:
    """
    divide mmsi and country code into separate fields
    """
    mmsi_codes = df["sourcemmsi"].tolist()
    raw_mmsi_codes = []
    country_codes = []

    for code in mmsi_codes:

        str_mmsi_code = str(code)
        country_code = int(str_mmsi_code[:3])
        try:
            mmsi_code = int(str_mmsi_code[3:])
        except Exception as e:
            mmsi_code = int(float(str_mmsi_code[3:]))
        raw_mmsi_codes.append(mmsi_code)
        country_codes.append(country_code)
    df["sourcemmsi"] = raw_mmsi_codes
    df["country_code"] = country_codes
    return df