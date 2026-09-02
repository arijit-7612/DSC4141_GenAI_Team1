# 🍽️ AI Meal Planner & Grocery Assistant

> **AI-powered personalized meal planning and automated grocery list generation.**

A GenAI-powered application that helps users plan healthy meals based on their **diet, health goals, budget, allergies, cuisine preferences, and cooking time** — then automatically generates a grocery list from the selected meals.

## ✨ Features

* 🤖 **AI Meal Planning** — Generate personalized weekly meal plans.
* 🥗 **Dietary Personalization** — Supports dietary preferences, allergies, goals, and cuisines.
* 🔎 **RAG-based Recipe Recommendations** — Retrieves relevant recipes from a structured recipe database.
* 🛒 **Automatic Grocery Lists** — Aggregates ingredients and quantities across the meal plan.
* 💬 **AI Assistant** — Modify meals using natural language.
* 💰 **Budget-Aware Planning** — Generate and optimize meals within a weekly budget.
* 📊 **Nutrition Overview** — Track calories, protein, carbohydrates, and fats.

## 🧠 How It Works

```text
User Preferences
       ↓
   AI / LLM
       ↓
Recipe Retrieval (RAG)
       ↓
Personalized Meal Plan
       ↓
Nutrition & Budget Validation
       ↓
Automatic Grocery List
       ↓
AI-powered Modifications
```

## 🏗️ Architecture

```text
Frontend (React / Next.js)
          ↓
     FastAPI Backend
          ↓
 ┌────────┼─────────┐
 ↓        ↓         ↓
Users   Recipes   Grocery Engine
          ↓
      pgvector
          ↓
         LLM
```

## 🛠️ Tech Stack

| Layer         | Technology                          |
| ------------- | ----------------------------------- |
| Frontend      | React / Next.js, Tailwind CSS       |
| Backend       | Python, FastAPI                     |
| Database      | PostgreSQL                          |
| Vector Search | pgvector                            |
| GenAI         | LLM API                             |
| AI            | RAG, Embeddings, Structured Outputs |

## 📁 Project Structure

```text
meal-planner/
├── frontend/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── services/
│   │   └── rag/
│   └── main.py
├── data/
│   ├── recipes/
│   └── nutrition/
├── tests/
├── .env.example
└── README.md
```

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/meal-planner.git
cd meal-planner
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
```

Activate the environment and install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
DATABASE_URL=your_database_url
OPENAI_API_KEY=your_api_key
```

Run the backend:

```bash
uvicorn app.main:app --reload
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## 💬 Example

**User:**

> "I'm vegetarian, have a ₹2000 weekly budget, want high-protein meals, and can cook for only 30 minutes."

**AI:**

Generates a personalized 7-day meal plan, validates the budget and nutrition requirements, and creates the required grocery list automatically.

Users can then say:

> "Replace paneer with a cheaper protein."

The AI updates the meal plan and grocery list accordingly.

## 🎯 Target Users

* Working professionals
* Students
* People living alone
* Fitness-conscious users
* Busy individuals looking to eat healthier

## 🌟 What Makes It GenAI?

The project goes beyond simple text generation by combining:

**LLM + RAG + Personalization + Constraint Handling + Nutrition Data + Grocery Automation**

The LLM handles reasoning and natural-language interaction, while the backend performs deterministic calculations such as ingredient aggregation, nutrition calculations, and budget validation.

## 🔮 Future Enhancements

* 📷 Refrigerator image recognition
* 🛍️ Online grocery integration
* 📈 Nutrition & meal history
* 🔔 Meal reminders
* 🎙️ Voice-based meal planning
* 🧠 Personalized recommendations based on past choices

## 👥 Team

| Member   | Responsibility             |
| -------- | -------------------------- |
| Member 1 | Frontend & UI/UX           |
| Member 2 | Backend & Database         |
| Member 3 | GenAI & RAG                |
| Member 4 | Nutrition & Grocery Engine |

## 📜 License

This project is developed for educational and demonstration purposes.
