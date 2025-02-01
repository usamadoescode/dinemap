# DineMap

## Overview
**DineMap** is an intelligent food recommendation system that allows users to discover restaurants, share food reviews, and get personalized food suggestions using AI. Powered by **Google PaLM LLM** and **LangChain**, users can search for food-related queries, explore restaurant menus, and find the best places to eat based on their preferences.

The platform also includes a meal planning feature and enables users to read reviews about food items, making it easier to make dining decisions.

## Features
- **Food Reviews:** Users can share their own food experiences and read reviews from others.
- **Food AI Search:** AI-driven feature to search for food queries like:
    - "Best Zinger burger under 500 rupees"
    - "Suggest some places to eat pizza"
    - "Recipe of a biryani"
    - "Best shawarma I can eat under 500"
    - "What people are saying about KFC's newly launched K Zing Burger?"
- **Restaurant Discovery:** Search and explore 200+ restaurants and over 1000 menu items.
- **Meal Planning:** Plan meals based on dietary preferences, budget, and available options.
- **Google PaLM LLM Model:** Leveraging advanced AI for contextual food-related recommendations and queries.
- **LangChain:** Integrated for dynamic query handling, allowing users to interact with the system using natural language and receive context-aware responses.

## Tech Stack
- **Backend:** Django
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQL Database (storing restaurant data, menu items, reviews, etc.)
- **AI:** Google PaLM LLM model (for handling natural language queries)
- **Query Handling:** LangChain (for enhanced AI-driven query management)
- **Deployment:** Vercel

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Django 4.x or higher
- SQL Database for storing restaurant data and reviews
- `.env` file for sensitive data (e.g., Google API keys, AI model configurations)
- **LangChain** library for query processing and context management

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/dinemap.git
   cd dinemap
