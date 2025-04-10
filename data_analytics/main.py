import pandas as pd
import datetime
import numpy as np
import os
import sys

def main():
    data_files = ["dynamic_vessel.csv","dynamic_aton.csv","dynamic_sar.csv"]
    with open("summary.txt", "w") as f:
        sys.stdout = f
        for file in data_files:
            if file == "dynamic_sar.csv":
                timestamp = "ts"
            else:
                timestamp = "t"
            print("----------------------------------------------")
            print(f"processing data for {file}")

            filename = f'./data/{file}'
            df = pd.read_csv(filename, delimiter=",")
            data_size = os.path.getsize(filename) # in bytes

            size_kb = data_size /1024 # kB
            size_mb = data_size / (1024 * 1024) # mb

            print("data size: {} KB".format(size_kb))
            print("data size: {} MB".format(size_mb))

            unique_vessel_ids = df["sourcemmsi"].unique()
            print("number of unique vessel ids: ", len(unique_vessel_ids))

            min_epoch = min(df[timestamp].to_list())
            max_epoch = max(df[timestamp].to_list())

            min_time = datetime.datetime.fromtimestamp(min_epoch)
            max_time = datetime.datetime.fromtimestamp(max_epoch)

            print("min time: ", min_time)
            print("max time: ", max_time)
            between_time = (max_time - min_time)
            print("data is between time", between_time)
            between_days = between_time.days

            print("num of datapoints", len(df))

            vessel_frequency: dict[int, float] = dict()

            for vessel_id in unique_vessel_ids:
                vessel_data = df[df["sourcemmsi"] == vessel_id].copy()
                vessel_data = vessel_data.sort_values(by=timestamp,ascending=True)
                vessel_data["time_freq"] = vessel_data[timestamp].diff()
                #there is some anomalities in the data so lets use the quantiles to get "correct" average
                q1 = vessel_data["time_freq"].quantile(0.02)
                q2 = vessel_data["time_freq"].quantile(0.98)

                filtered = vessel_data[(vessel_data["time_freq"] >= q1) & (vessel_data["time_freq"] <= q2) ]

                average_freq = filtered["time_freq"].mean()
                if not np.isnan(average_freq):
                    vessel_frequency[vessel_id] = average_freq

            average_freq_all_vessels = np.average(list(vessel_frequency.values()))
            max_vessel_frequency = max(list(vessel_frequency.values()))
            print(f"max vessel frequency {max_vessel_frequency} sec")
            print(f"max vessel frequency {max_vessel_frequency/60} min")
            print(f"max vessel frequency {max_vessel_frequency/60/60} hr")
            print(f"max vessel frequency {max_vessel_frequency/60/60/24} days")
            average_day_fred = average_freq_all_vessels / 60 / 60 / 24
            print(f"average vessel frequency {average_freq_all_vessels} sec")
            print(f"average vessel frequency {average_freq_all_vessels / 60} min")
            print(f"average vessel frequency {average_freq_all_vessels / 60 / 60} hr")
            print(f"average vessel frequency {average_day_fred} days")

            messages_between_days_for_vessel = between_days / average_day_fred
            messages_between_days = float(between_days / average_day_fred) * len(unique_vessel_ids)
            print(f"expecting  {messages_between_days_for_vessel} messages for single vessel between {between_days} days")
            print(f"expecting  {messages_between_days} messages for ALL vessels between {between_days} days")
            print(f"expecting  {messages_between_days/(between_days*24*60/10)} messages for ALL vessels between 10 minutes")

        sys.stdout = sys.__stdout__  # reset
        print("done")

if __name__ == '__main__':
    main()