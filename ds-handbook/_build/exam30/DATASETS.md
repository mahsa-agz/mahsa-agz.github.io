# Practice datasets (downloaded and checked 2026-10-07)

All files are in `exam_prep/data/`. Every one was downloaded with `_build/exam30/fetch_data.py`
and then loaded with pandas (CSV) or sqlite3 (DB). Each URL is a direct download with no login, so the same URL works in Colab, for example:

```python
import pandas as pd
df = pd.read_csv("https://raw.githubusercontent.com/robguilarr/ab_testing_cookie_cats/main/datasets/cookie_cats.csv")
# zip sources (MovieLens, UCI):  !wget -q <url> && unzip -o <file>.zip
# SQLite:  !wget -q <url> -O chinook.sqlite ; import sqlite3; con = sqlite3.connect("chinook.sqlite")
```

Supports: **SQL** = joins / window functions / aggregation; **Stats** = distributions, CIs, tests, regression; **A/B** = experiment analysis; **ML** = supervised or unsupervised modelling; **NLP** = text classification.

## Product / user-behaviour datasets (start here)

| Local file | Source URL (direct download) | License / terms | Size | Rows | Columns | Supports |
|---|---|---|---|---|---|---|
| `cookie_cats.csv` | https://raw.githubusercontent.com/robguilarr/ab_testing_cookie_cats/main/datasets/cookie_cats.csv | Real mobile-game A/B test, released through the DataCamp project "Mobile Games A/B Testing". The mirror repo has no license, so treat it as educational use only. A second mirror is https://raw.githubusercontent.com/basilghauri/A-B-Testing-of-Mobile-Game/main/cookie_cats.csv | 2.7 MB | 90,189 | `userid`; `version` (gate_30 = control, gate_40 = treatment); `sum_gamerounds` (rounds played in week 1); `retention_1` and `retention_7` (bool, came back on day 1 / day 7) | **A/B** (two-proportion test, bootstrap, heavy-tailed metric), Stats, SQL |
| `ab_data.csv` | https://raw.githubusercontent.com/F-Zarian/Analyze_AB_test_results/main/ab_data.csv | Udacity Data Analyst ND "Analyze A/B Test Results" project data. The mirror repo has no license, so treat it as educational use only. A second mirror is the hwangmpaula/Analyze-A-B-Test-Results repo (branch hwangmpaula-patch-1) | 15.9 MB | 294,478 | `user_id`, `timestamp`, `group` (control/treatment), `landing_page` (old/new), `converted` (0/1). It contains deliberate group/page mismatches and duplicate users to clean | **A/B** (data-quality checks, SRM, z-test, logistic regression), SQL |
| `ab_countries.csv` | https://raw.githubusercontent.com/F-Zarian/Analyze_AB_test_results/main/countries.csv | Same as above | 2.9 MB | 290,584 | `user_id`, `country` (UK/US/CA). Join it to ab_data | **A/B** segment / heterogeneous effects, SQL joins |
| `telco_churn.csv` | https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv | IBM sample data; the repo is Apache-2.0 (archived but still served) | 0.97 MB | 7,043 | `customerID`, demographics (`gender`, `SeniorCitizen`, `Partner`, `Dependents`), `tenure`, 9 service columns (`PhoneService`, `InternetService`, `StreamingTV`...), `Contract`, `PaymentMethod`, `MonthlyCharges`, `TotalCharges` (text with blanks), `Churn` (Yes/No) | **ML** (churn classification, imbalance, metrics), Stats, SQL, product sense (retention drivers) |
| `googleplaystore.csv` | https://raw.githubusercontent.com/malborroni/Foundations_of_Computer-Science/master/datasets/googleplaystore.csv | Scraped Google Play data, a mirror of Kaggle "lava18/google-play-store-apps". The mirror repo has no license; check the Kaggle page for terms. Use it for study only | 1.35 MB | 10,841 | `App`, `Category`, `Rating`, `Reviews`, `Size`, `Installs` ("10,000+"), `Type` (Free/Paid), `Price`, `Content Rating`, `Genres`, `Last Updated`, `Current Ver`, `Android Ver`. Messy strings and one shifted row | Data cleaning, Stats, SQL, product sense (app-store metrics) |
| `googleplaystore_user_reviews.csv` | https://raw.githubusercontent.com/malborroni/Foundations_of_Computer-Science/master/datasets/googleplaystore_user_reviews.csv | Same as above | 7.6 MB | 64,295 | `App`, `Translated_Review`, `Sentiment` (Positive/Neutral/Negative), `Sentiment_Polarity`, `Sentiment_Subjectivity`. Many rows are NaN | **NLP** (sentiment classification), join with apps |
| `movielens_ratings.csv`, `movielens_movies.csv`, `movielens_tags.csv`, `movielens_links.csv` | https://files.grouplens.org/datasets/movielens/ml-latest-small.zip (only the 4 CSVs are kept) | GroupLens usage license: research/education use, acknowledge it, no endorsement claims, commercial use needs permission | 2.5 + 0.49 + 0.12 + 0.2 MB | 100,836 ratings; 9,742 movies; 3,683 tags; 9,742 links | ratings: `userId`, `movieId`, `rating` (0.5 to 5), `timestamp` (unix). movies: `movieId`, `title`, `genres` (pipe-separated). tags: `userId`, `movieId`, `tag`, `timestamp` | **ML** (recommender, matrix factorisation), SQL (windows, cohorts), Stats |
| `online_retail.csv.gz` | https://archive.ics.uci.edu/static/public/352/online+retail.zip (the xlsx was converted to gzipped CSV) | UCI ML Repository, CC BY 4.0 | 7.7 MB (gz) | 541,909 | `InvoiceNo` (a "C" prefix means a cancellation), `StockCode`, `Description`, `Quantity`, `InvoiceDate`, `UnitPrice`, `CustomerID` (about 25% missing), `Country`. UK online retailer, 2010-12 to 2011-12 | SQL (RFM, cohorts, retention, revenue windows), Stats, ML (segmentation) |
| `bank_marketing.csv` (read with `sep=";"`) | https://archive.ics.uci.edu/static/public/222/bank+marketing.zip, then the inner `bank-additional.zip` and `bank-additional/bank-additional-full.csv` | UCI ML Repository, CC BY 4.0 | 5.8 MB | 41,188 | client info (`age`, `job`, `marital`, `education`, `default`, `housing`, `loan`), campaign (`contact`, `month`, `day_of_week`, `duration` (leaky!), `campaign`, `pdays`, `previous`, `poutcome`), macro (`emp.var.rate`, `cons.price.idx`, `cons.conf.idx`, `euribor3m`, `nr.employed`), target `y` (yes/no, about 11% yes) | **ML** (imbalanced classification, leakage discussion), Stats |
| `sms_spam.tsv` (read with `sep="\t", header=None, names=["label","text"]`) | https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip (file `SMSSpamCollection`) | UCI ML Repository, CC BY 4.0 | 0.48 MB | 5,572 | `label` (ham/spam, about 13% spam), `text` | **NLP** (TF-IDF + LR/NB, embeddings, precision/recall) |

## SQL databases

| Local file | Source URL | License | Size | Tables (rows) | Supports |
|---|---|---|---|---|---|
| `chinook.sqlite` | https://github.com/lerocha/chinook-database/releases/download/v1.4.5/Chinook_Sqlite.sqlite | MIT-style license (lerocha/chinook-database LICENSE.md) | 1.07 MB | Album 347, Artist 275, Customer 59, Employee 8 (self-join manager), Genre 25, Invoice 412, InvoiceLine 2,240, MediaType 5, Playlist 18, PlaylistTrack 8,715, Track 3,503 | **SQL**: a digital music store. Multi-joins, revenue by country or genre, top-N per group, self-joins |
| `northwind.db` | https://raw.githubusercontent.com/jpwhite3/northwind-SQLite3/main/dist/northwind.db | MIT | 24.7 MB | Customers 93, Orders 16,282, "Order Details" 609,283 (quote the name), Products 77, Categories 8, Employees 9, Suppliers 29, Shippers 3, Territories 53, Regions 4 (dates extended, so the data is enlarged) | **SQL**: orders and e-commerce. Window functions, YoY/MoM growth, retention, basket analysis |
| `jaffle_raw_customers.csv`, `jaffle_raw_orders.csv`, `jaffle_raw_payments.csv` | https://raw.githubusercontent.com/dbt-labs/jaffle_shop/main/seeds/raw_customers.csv (also `raw_orders.csv`, `raw_payments.csv` in the same folder) | Apache-2.0 (archived repo, still served) | < 10 KB each | 100 customers (`id`, `first_name`, `last_name`); 99 orders (`id`, `user_id`, `order_date`, `status`); 113 payments (`id`, `order_id`, `payment_method`, `amount` in cents) | **SQL** warm-ups. Tiny enough to check answers by hand: first/last order, LTV, payment mix |

## Classic small tables (seaborn-data)

Source: `https://raw.githubusercontent.com/mwaskom/seaborn-data/master/<name>.csv`. Terms: there is no license file. The repo describes itself as "not a general-purpose data archive" for the seaborn docs, and files may change. The original sources are mostly public (ggplot2, UCI, NYC TLC, Kaggle). Use them for study only.

| Local file | Size | Rows | Columns | Supports |
|---|---|---|---|---|
| `tips.csv` | 8 KB | 244 | `total_bill`, `tip`, `sex`, `smoker`, `day`, `time`, `size` | Stats (t-test, regression, CI), SQL basics |
| `penguins.csv` | 14 KB | 344 | `species`, `island`, `bill_length_mm`, `bill_depth_mm`, `flipper_length_mm`, `body_mass_g`, `sex` (has NaN) | ML classification/clustering, ANOVA, missing data |
| `titanic.csv` | 57 KB | 891 | `survived`, `pclass`, `sex`, `age`, `sibsp`, `parch`, `fare`, `embarked`, `class`, `who`, `adult_male`, `deck`, `embark_town`, `alive`, `alone` | ML (logistic regression, trees), chi-square, SQL group-bys |
| `taxis.csv` | 0.87 MB | 6,433 | `pickup`, `dropoff` (datetimes), `passengers`, `distance`, `fare`, `tip`, `tolls`, `total`, `color`, `payment`, `pickup_zone`, `dropoff_zone`, `pickup_borough`, `dropoff_borough` | Marketplace/product metrics, SQL time functions, regression (tip %) |
| `diamonds.csv` | 2.8 MB | 53,940 | `carat`, `cut`, `color`, `clarity`, `depth`, `table`, `price`, `x`, `y`, `z` | Regression, log transforms, feature engineering |
| `flights.csv` | 2 KB | 144 | `year`, `month`, `passengers` (monthly airline passengers 1949 to 1960) | Time series (seasonality, trend), window functions |
| `mpg.csv` | 21 KB | 398 | `mpg`, `cylinders`, `displacement`, `horsepower` (has NaN), `weight`, `acceleration`, `model_year`, `origin`, `name` | Regression, correlation, missing values |

## Notes / caveats
- The two A/B files (Cookie Cats, Udacity ab_data) and Google Play come from personal GitHub mirrors with no license file, so they could disappear. A second mirror is listed above for each A/B file. The DataCamp and Kaggle originals need a login.
- `northwind.db` is near the 30 MB limit (24.7 MB) because the jpwhite3 build extends the order dates. That is fine for practice.
- `online_retail.csv.gz` was converted locally from the UCI xlsx. In Colab, either download the zip and use `pd.read_excel` (needs openpyxl, about 20 MB in memory) or upload the gz file.
- To re-download everything, run `python _build/exam30/fetch_data.py`. Files that already exist are skipped.
