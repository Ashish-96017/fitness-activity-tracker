# 🏃 Fitness Activity Tracker & Progress Analyzer

A Python-based desktop application for recording, managing, and analyzing daily fitness activities such as **Walking, Running, and Cycling**.

The application helps users understand their **activity consistency, duration, distance, average speed, activity-type performance, and changes across different time periods**. It provides a simple Tkinter graphical interface, persistent CSV storage, Pandas/NumPy-based analysis, and Matplotlib visual reports.

---

## 📌 Project Information

| Details | Information |
|---|---|
| **Project Title** | Fitness Activity Tracker and Progress Analyzer |
| **Domain** | Sports & Fitness |
| **Student Name** | SHAKORIYA ASHISH VIJAYBHAI |
| **Enrollment Number** | IU2441230435 |
| **Programming Language** | Python |
| **GUI Framework** | Tkinter |
| **Data Storage** | CSV |
| **Data Analysis** | Pandas & NumPy |
| **Visualization** | Matplotlib |

---

## 🎯 Problem Statement

A person records daily fitness activities such as walking, running, or cycling but wants to understand consistency, duration, and changes in activity levels.

This project provides an application that stores fitness activity records and converts them into useful summaries, comparisons, and visual trends.

---

## 🎯 Objective

To develop an application that maintains fitness activity records and provides meaningful progress analysis.

The application makes it easy to:

- Record daily fitness activities
- Store activity information permanently
- Search and filter activity records
- Calculate useful fitness metrics
- Compare different activity types
- Compare recent and previous activity periods
- Identify activity trends
- Generate visual reports

---

## ✨ Features

### 📊 Dashboard

The dashboard provides a quick overview of:

- Total number of activities
- Total distance
- Total duration
- Average speed
- Most frequent activity

### ➕ Add / Edit Activity

Users can enter:

- Activity date
- Activity type
- Duration
- Distance
- Optional notes

Input validation is performed before the record is saved.

### 📋 Activity Records

The application provides a table containing all stored activity records.

Users can:

- View activities
- Search activities
- Filter by activity type
- Filter by date
- Edit records
- Delete records

### 📈 Analytics & Reports

The application calculates:

- Total activity count
- Total distance
- Total duration
- Average speed
- Most frequent activity
- Activity-type comparison
- Seven-day period comparison
- Percentage change between periods
- Activity trends

### 📊 Matplotlib Reports

The project generates two meaningful visual reports:

1. **Daily Distance Trend**
2. **Distance Comparison by Activity Type**

---

## 🛠️ Technologies Used

- **Python** – Core programming language
- **Tkinter** – Graphical User Interface
- **Pandas** – Data processing and analysis
- **NumPy** – Numerical calculations
- **Matplotlib** – Data visualization
- **CSV** – Persistent data storage
- **unittest** – Automated testing

---

## 🧩 Project Architecture

The project follows a modular structure so that each part of the application has a clear responsibility.

```text
                    ┌─────────────────────┐
                    │     Tkinter GUI     │
                    │       main.py       │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
       ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
       │ Validation  │  │   Storage   │  │  Analytics  │
       │validation.py│  │activity_    │  │ analytics.py│
       │             │  │manager.py   │  │             │
       └─────────────┘  └──────┬──────┘  └──────┬──────┘
                                │                │
                                ▼                ▼
                         ┌─────────────┐   ┌─────────────┐
                         │ activities  │   │ Matplotlib  │
                         │    .csv     │   │   Reports   │
                         └─────────────┘   └─────────────┘
