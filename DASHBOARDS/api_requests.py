import requests
import polars as pl

def fetch_and_clean_df(api_url: str, date_cols=None, time_cols=None, int_cols=None, timedelta_cols=None, drop_cols=None) -> pl.DataFrame:
    response = requests.get(api_url)
    response.raise_for_status()
    data = response.json()

    df = pl.DataFrame(data)

    # Clean date columns
    if date_cols:
        for col in date_cols:
            df = df.with_columns(pl.col(col).str.strip_chars('"').str.to_date("%Y-%m-%d"))

    # Clean time columns
    if time_cols:
        for col in time_cols:
            df = df.with_columns(pl.col(col).str.strip_chars('"').str.to_time("%H:%M:%S"))

    # Clean timedelta columns (HH:MM:SS -> seconds as integer)
    if timedelta_cols:
        for column_name in timedelta_cols:
            df = df.with_columns(
                pl.col(column_name).str.extract_all(r"\d+").alias(column_name)
            ).with_columns(
                pl.duration(
                hours=pl.col(column_name).list.get(0).cast(pl.Int64),
                minutes=pl.col(column_name).list.get(1).cast(pl.Int64),
                seconds=pl.col(column_name).list.get(2).cast(pl.Int64),
            ).alias(column_name)
        )

    # Cast integer columns
    if int_cols:
        for col in int_cols:
            df = df.with_columns(pl.col(col).cast(pl.Int64))

    # Drop unwanted columns
    if drop_cols:
        df = df.drop(drop_cols)

    return df



def get_patients_df(api_url: str) -> pl.DataFrame:
    return fetch_and_clean_df(
        api_url,
        date_cols=["dob"],
        int_cols=["patient_id"],
        drop_cols=["id"]
    )


def get_slots_df(api_url: str) -> pl.DataFrame:
    return fetch_and_clean_df(
        api_url,
        date_cols=["appointment_date"],
        time_cols=["appointment_time"],
        int_cols=["slot_id"],
        drop_cols=["id"]
    )


def get_appointments_df(api_url: str) -> pl.DataFrame:
    return fetch_and_clean_df(
        api_url,
        date_cols=["scheduling_date", "appointment_date"],
        time_cols=["appointment_time", "check_in_time", "start_time", "end_time"],
        timedelta_cols = ["appointment_duration", "waiting_time"],
        int_cols=["appointment_id", "patient_id", "appointment_id"],
        drop_cols=["id", "patient_id"]
    )