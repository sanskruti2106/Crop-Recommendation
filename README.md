# Crop-Recommendation
ML-based Crop Recommendation System using Random Forest and Flask | 99.55% Accuracy
# 🌱 Crop Recommendation System

A Machine Learning based Crop Recommendation System that recommends the most suitable crop based on soil and environmental conditions.

## 📌 Project Description

This project uses Machine Learning to recommend a suitable crop according to the following parameters:

- Nitrogen (N)
- Phosphorus (P)
- Potassium (K)
- Temperature
- Humidity
- Soil pH
- Rainfall

The system uses a Random Forest Classifier to predict the recommended crop.

## 🎯 Objectives

- Recommend suitable crops based on soil and weather conditions.
- Use Machine Learning for accurate crop prediction.
- Provide a simple and user-friendly web interface.
- Help users make data-driven crop selection decisions.

## 🤖 Machine Learning Model

**Algorithm:** Random Forest Classifier

**Number of Estimators:** 100

**Test Accuracy:** 99.55%

## 🛠️ Technologies Used

- Python
- Pandas
- NumPy
- Scikit-learn
- Flask
- HTML
- CSS
- JavaScript

## 📂 Project Structure

```text
Crop-Recommendation/
│
├── Crop_recommendation.csv
├── crop_recommendation.py
├── app.py
├── app_web.py
│
├── templates/
│   ├── index.html
│   ├── about.html
│   ├── catalog.html
│   ├── how_it_works.html
│   └── layout.html
│
└── static/
