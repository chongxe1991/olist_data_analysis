# Introduction

Olist is a Brazilian ecommerce company. It connects merchants and their products to the main market places of Brazil. Olist Data Analysis aims to perform an analysis on Olist public dataset, and suggest some ways to improve the profits of the company.

# Dataset

The dataset can be downloaded from Kaggle [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce). It includes several csv files which are related to Olist such as its order reviews, customers and order geolocations.

# Analysis

Several initial analysis were done on the dataset itself to inspect the data structures and distribution. **Data wrangling and feature engineering** were done to transform the data into useful information, such as getting the revenue per seller and profit that the seller brings into Olist. As Olist is a Brazilian platform and the reviews were in Portuguese language, the reviews are also translated from Portuguese into English using an **API**. Simple **OLS models** were used to test and explain the relationship of various features with the rating of the order. Finally, some analysis was done on the sellers of the platform to **suggest ways to improve Olist's profits**, as some of the sellers bring losses to the company due to the cost of handling customer complaints and low ratings.

# Conclusion

Based on the analysis, [three ways](https://github.com/chongxe1991/olist_data_analysis/blob/master/ceo_request.ipynb) are suggested to improve Olist's profit, based on different scenarios:

1. **Removing all loss-bearing sellers from the platform altogether** - This will result in the removal of 1004 sellers, and if these sellers are not in Olist from the start, Olist could have improved its profits by approximately 66%.
2. **Removing just enough loss-bearing sellers from the platform to achieve maximum profit** - This method is done by iterating over the profits achieved on every removal of one seller, as we also need to take IT costs into consideration (IT costs scale much slower by each increased order, so the number of orders brought in by sellers matter as well in this case). By this method, it is found that Olist only needs to remove 486 sellers to achieve max profits, and Olist would have improved its profits by approximately 120%, if these sellers were not present in the platform since the start.
3. **Removing based on the number of months of sellers** - The analysis provided insights that, most of the sellers that brought losses to Olist have just been onboarded or has only one month in the platform. If network effect or opportunity costs are considered, Olist may lose in future profits if these sellers have the potential to turn profitable in the future. Based on the median number of months of sellers making profits in Olist, it is suggested that Olist remove sellers that do not break even only after four months. This results in the removal of 135 sellers from Olist platform, and has these sellers not been in the platform since the start, Olist could have improved its profits by approximately 58% -- without losing opportunity costs or scare potential sellers away from its platform.
