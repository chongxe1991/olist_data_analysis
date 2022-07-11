import pandas as pd
import numpy as np
from utils import haversine_distance
from data import Olist


class Order:
    '''
    This function returns a DataFrames containing all orders as index,
    and various properties of these orders as columns
    '''
    def __init__(self):

        # An attribute ".data" is assigned to all new instances of Order
        self.data = Olist().get_data()


    def get_wait_time(self, is_delivered=True):
        """
        This function returns a DataFrame with:
        [order_id, wait_time, expected_wait_time, delay_vs_expected, order_status]
        and filters out non-delivered orders unless specified
        """

        # Within this instance method, we have access to the instance of the
        # class Order in the variable self, as well as all its attributes
        orders = self.data['orders'].copy()

        orders = orders[orders["order_status"] == "delivered"]
        orders["order_purchase_timestamp"] = pd.to_datetime(orders["order_purchase_timestamp"])
        orders["order_approved_at"] = pd.to_datetime(orders["order_approved_at"])
        orders["order_delivered_carrier_date"] = pd.to_datetime(orders["order_delivered_carrier_date"])
        orders["order_delivered_customer_date"] = pd.to_datetime(orders["order_delivered_customer_date"])
        orders["order_estimated_delivery_date"] = pd.to_datetime(orders["order_estimated_delivery_date"])
        orders["wait_time"] = orders["order_delivered_customer_date"] - orders["order_purchase_timestamp"]
        orders["expected_wait_time"] = orders["order_estimated_delivery_date"] - orders["order_purchase_timestamp"]
        orders["delay_vs_expected"] = orders["wait_time"] - orders["expected_wait_time"]
        orders = orders[["order_id", "wait_time", "expected_wait_time", "delay_vs_expected", "order_status"]]
        orders["wait_time"] = orders["wait_time"].dt.days
        orders["expected_wait_time"] = orders["expected_wait_time"].dt.days
        orders["delay_vs_expected"] = orders["delay_vs_expected"].dt.days
        orders["expected_wait_time"] = orders["expected_wait_time"].astype("float64")
        convert_numbers = lambda x: 0 if x <= 0 else x
        orders["delay_vs_expected"] = orders["delay_vs_expected"].apply(convert_numbers)

        return orders


    def get_review_score(self):
        """
        This function returns a DataFrame with:
        order_id, dim_is_five_star, dim_is_one_star, review_score
        """
        reviews = self.data['order_reviews'].copy()
        assign_5 = lambda x: 1 if (x == 5) else 0
        assign_1 = lambda x: 1 if (x == 1) else 0
        reviews["dim_is_five_star"] = reviews["review_score"].apply(assign_5)
        reviews["dim_is_one_star"] = reviews["review_score"].apply(assign_1)
        reviews = reviews[["order_id", "dim_is_five_star", "dim_is_one_star", "review_score"]]

        return reviews


    def get_number_products(self):
        """
        This function returns a DataFrame with:
        order_id, number_of_products
        """
        order_items = self.data["order_items"].copy()
        order_items2 = order_items.groupby("order_id").count()
        order_items2.rename(columns = {"order_item_id": "number_of_products"}, inplace = True)
        order_items2.reset_index(inplace = True)
        order_items2 = order_items2[["order_id", "number_of_products"]]

        return order_items2


    def get_number_sellers(self):
        """
        This function returns a DataFrame with:
        order_id, number_of_sellers
        """
        order_items = self.data["order_items"].copy()
        order_items = order_items.groupby("order_id").nunique()
        order_items.reset_index(inplace = True)
        order_items.rename(columns = {"seller_id": "number_of_sellers"}, inplace = True)
        order_items = order_items[["order_id", "number_of_sellers"]]

        return order_items


    def get_price_and_freight(self):
        """
        This function returns a DataFrame with:
        order_id, price, freight_value
        """
        order_items = self.data["order_items"].copy()
        order_items = order_items.groupby("order_id").sum()
        order_items.reset_index(inplace = True)
        order_items = order_items[["order_id", "price", "freight_value"]]

        return order_items


    def get_distance_seller_customer(self):
        """
        This function returns a DataFrame with:
        order_id, distance_seller_customer
        """

        # Data is imported
        data = self.data
        orders = data['orders']
        order_items = data['order_items']
        sellers = data['sellers']
        customers = data['customers']

        # Since one zip code can map to multiple (lat, lng), the first one is
        # taken
        geo = data['geolocation']
        geo = geo.groupby('geolocation_zip_code_prefix',
                          as_index=False).first()

        # Geo_location is merged for sellers
        sellers_mask_columns = [
            'seller_id', 'seller_zip_code_prefix', 'geolocation_lat', 'geolocation_lng'
        ]

        sellers_geo = sellers.merge(
            geo,
            how='left',
            left_on='seller_zip_code_prefix',
            right_on='geolocation_zip_code_prefix')[sellers_mask_columns]

        # Geo_location is merged for customers
        customers_mask_columns = ['customer_id', 'customer_zip_code_prefix', 'geolocation_lat', 'geolocation_lng']

        customers_geo = customers.merge(
            geo,
            how='left',
            left_on='customer_zip_code_prefix',
            right_on='geolocation_zip_code_prefix')[customers_mask_columns]

        # Customers are matched with sellers in one table
        customers_sellers = customers.merge(orders, on='customer_id')\
            .merge(order_items, on='order_id')\
            .merge(sellers, on='seller_id')\
            [['order_id', 'customer_id','customer_zip_code_prefix', 'seller_id', 'seller_zip_code_prefix']]

        matching_geo = customers_sellers.merge(sellers_geo,
                                            on='seller_id')\
            .merge(customers_geo,
                   on='customer_id',
                   suffixes=('_seller',
                             '_customer'))
        # na() is removed
        matching_geo = matching_geo.dropna()

        matching_geo.loc[:, 'distance_seller_customer'] =\
            matching_geo.apply(lambda row:
                               haversine_distance(row['geolocation_lng_seller'],
                                                  row['geolocation_lat_seller'],
                                                  row['geolocation_lng_customer'],
                                                  row['geolocation_lat_customer']),
                               axis=1)

        # Since an order can have multiple sellers, the average of the distance
        # per order is returned
        order_distance =\
            matching_geo.groupby('order_id',
                                 as_index=False).agg({'distance_seller_customer':
                                                      'mean'})

        return order_distance


    def get_training_data(self,
                          is_delivered=True,
                          with_distance_seller_customer=True):
        """
        This function returns a clean DataFrame (without NaN), with the all
        following columns:
        ['order_id', 'wait_time', 'expected_wait_time', 'delay_vs_expected',
        'order_status', 'dim_is_five_star', 'dim_is_one_star', 'review_score',
        'number_of_products', 'number_of_sellers', 'price', 'freight_value',
        'distance_seller_customer']
        """

        # The instance methods defined above are reused
        df1 = self.get_wait_time()
        df2 = self.get_review_score()
        df3 = self.get_number_products()
        df4 = self.get_number_sellers()
        df5 = self.get_price_and_freight()
        df6 = self.get_distance_seller_customer()
        all_df = (df1.merge(df2, on = "order_id").merge(df3, on = "order_id")
                  .merge(df4, on = "order_id").merge(df5, on = "order_id"))

        if with_distance_seller_customer:
            all_df = all_df.merge(df6, on='order_id')

        all_df.dropna(inplace = True)

        return all_df
