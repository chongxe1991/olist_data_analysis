import os
import pandas as pd


class Olist:
    def get_data(self):
        """
        This function returns a Python dict.
        Its keys should be 'sellers', 'orders', 'order_items' etc...
        Its values should be pandas.DataFrames loaded from csv files
        """
        # csv_path is built as "absolute path" so that this method can be called from anywhere.
            # Path cannot be hardcoded as it only works on my machine ('Users/username/code...')
            # __file__ is used instead as an absolute path anchor independent of my usename
        # os.path library is used to construct path independent of Mac vs. Unix vs. Windows specificities

        root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_path = os.path.join(root_path, "data", "csv")
        file_names = []
        for item in os.listdir(csv_path):
            if item.endswith(".csv"):
                file_names.append(item)

        key_names = []
        for item in file_names:
            item = item.replace("_dataset.csv", "")
            item = item.replace(".csv", "")
            item = item.replace("olist_", "")
            key_names.append(item)

        data = {}
        for (x, y) in zip(key_names, file_names):
            data[x] = pd.read_csv(os.path.join(csv_path, y))

        return data
