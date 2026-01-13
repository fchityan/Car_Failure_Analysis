📌 Project Overview

This project presents an end-to-end machine learning workflow for analyzing car failure data, from exploratory data analysis (EDA) through feature engineering, model training, tuning, and evaluation.

The notebook is designed to be:

	•	📓 Self-contained and reproducible
	•	🔬 Exploratory yet production-aware
	•	🤖 Suitable for benchmarking multiple model types

All analysis, preprocessing, and modeling steps are executed directly within the notebook.

🎯 Objective

The goal is to build a reliable classification pipeline that:

	•	Identifies patterns associated with vehicle failures
	•	Handles data quality issues and feature imbalance
	•	Evaluates the trade-offs between accuracy and class balance
	•	Compares multiple machine learning models using consistent preprocessing

 📊 Key Findings from Exploratory Data Analysis

Initial EDA revealed several important characteristics of the dataset:

	•	⚠️ Negative values present in RPM
	•	📈 Fuel consumption is slightly right-skewed
	•	🌡️ Temperature forms two clearly separable clusters
	•	🚗 High cardinality in car model, making one-hot encoding impractical
	•	🌳 Categorical feature distributions vary widely, favoring tree-based models
	•	🔧 Each car can experience only one failure type
	•	⚖️ Strong target imbalance (>80% non-failure cases)

Due to the imbalance, down-sampling improves class balance but may reduce overall accuracy.

🔁 Pipeline Stages

The notebook follows a structured 6-step pipeline:

	1.	🧹 Data Cleaning
	2.	🏷️ Feature Encoding
	3.	🧪 Data Preparation
	4.	🤖 Model Training
	5.	🎯 Hyperparameter Tuning
	6.	📈 Model Evaluation

 📦 Initial Dataset Size
 
	•	10,081 rows
	•	14 columns

 🌡️ Temperature Encoding Rationale

The distribution of temperature values showed a clean separation into two low-variance clusters. Encoding these as High and Low reduces noise while preserving signal.

After cleaning:

	•	9,857 rows
	•	13 columns

 🏷️ Feature Encoding

After cleaning:

	•	Numerical features: RPM, Fuel Consumption
	•	All other features are categorical

Encoding Strategy
	•	🔢 Mean weight encoding for high-cardinality features
	•	🔠 One-hot encoding for low-cardinality features
	•	🔧 Failure columns merged into a single Faults column

After encoding:

	•	9,857 rows
	•	23 columns

🧪 Data Preparation

The notebook supports optional preparation steps:

	•	📉 Log transformation of fuel consumption
	•	⚖️ Target label balancing
	•	📐 Feature standardization

After preparation, the dataset is split into training and testing sets (70% / 30%).

📉 Dataset Size After Preparation

Before Train/Test Split:

	•	Balanced dataset: 1,496 rows
	•	Unbalanced dataset: 9,857 rows

 🧠 Modeling Approach

The notebook evaluates:

	•	Baseline classifiers for performance benchmarking
	•	Multiple model families to assess bias–variance trade-offs
	•	Hyperparameter tuning using cross-validation
	•	Performance metrics appropriate for imbalanced data

 ✅ Key Takeaways
 
	•	🧹 Strong preprocessing improves model stability
	•	⚖️ Balancing improves minority-class detection at an accuracy cost
	•	🌳 Tree-based models perform well with mixed feature types
	•	📊 Proper encoding dramatically reduces dimensionality
