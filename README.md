📌 Project Overview

This project analyzes a vehicle operational dataset to explore factors associated with car failures.

The notebook is designed to be:

	• Exploratory Data Analysis (EDA)
	• Data Cleaning and Preprocessing
	• Feature Transformation and Encoding
	• Handling Class Imbalance
	• Training and Evaluating a Classification Model

The primary goal is to understand the dataset's structure and investigate how preprocessing decisions influence classification performance. 

🎯 Objective

The objective of this project is to develop a classification model capable of predicting vehicle failure events based on operational features:

Specifically, the analysis aims to:

	• Identify patterns in vehicle operational metrics
	• Address data quality issues
	• Design appripriate encoding strategies for categorical features
	• Handle significant class imbalance
	• Evaluate model performance using relevant classification metrics

 📊 Dataset Overview

Key characteristics identified during EDA:

	•	⚠️ Negative values present in RPM
	•	📈 Fuel consumption is slightly right-skewed
	•	🌡️ Temperature forms two clearly separable clusters
	•	🚗 High cardinality in car model, making one-hot encoding impractical
	•	🌳 Categorical feature distributions vary widely, favoring tree-based models
	•	🔧 Each car can experience only one failure type
	•	⚖️ Strong target imbalance (>80% non-failure cases)


🔁 Exploratory Data Analysis (EDA)

The exploratory phase focused on:

Numerical Features:

	• Distribution analysis
	• Detection of invalid values
	• Identification of skewness and clustering

Categorical Features:

	• Cardinality assessment
	• Category distribution analysis
	• Encoding suitability evaluation

Target Distribution:

The dataset presents a highly imbalanced classificatin problem:

	• Majority: Non-failure
	• Minority: Failure

This imbalance significantly influences model evaluation and interpretation.

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

📉 Dataset Size After Preparation

Before Train/Test Split:

	•	Balanced dataset: 1,496 rows
	•	Unbalanced dataset: 9,857 rows

 ✅ Key Takeaways
 
	•	Data cleaning significantly improves model reliability
	•	Encoding strategy affects dimensionality and predictive performance
	•	Class imbalance has a strong impact on evaluation metrics
	•	Balancing improves minority class detection but may reduce overall accuracy
