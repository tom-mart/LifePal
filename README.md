# LifePal - Your AI-Powered Personal Assistant

## 🚀 Overview
LifePal is an intelligent personal assistant powered by Ollama that helps you manage your tasks and more through natural language interactions. The application combines the power of large language models with practical applications, starting with a todo list management system.

## ✨ Features

### Current Features
- **AI-Powered Task Management**: Interact with your todo list using natural language
- **RESTful API**: Built with Django and Ninja for robust backend functionality
- **Modern Web Interface**: Clean and responsive UI for seamless user experience
- **Ollama Integration**: Leverages local LLM for natural language understanding

### Upcoming Features
- **Multi-Application Support**: Expand beyond todo lists to other productivity tools
- **Natural Language Understanding**: More intuitive commands and conversations
- **User Authentication**: Secure user accounts and data privacy
- **Progressive Web App**: Near-native mobile experience for on-the-go access

## 🛠️ Tech Stack

### Backend
- **Python 3.12**
- **Django** - Modern, fast web framework
- **PostgreSQL** - Relational database
- **ChromaDB** - Vector database
- **Ninja** - Data validation and API framework

### Frontend
- **React** - Frontend library
- **Tailwind CSS** - Utility-first CSS framework
- **Vite** - Fast development tool
- **DaisyUI** - Tailwind CSS component library

### AI/ML
- **Ollama** - Local LLM for natural language processing
- **LangChain** - Framework for developing applications with LLMs

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 16+
- Ollama installed and running locally
- PostgreSQL (or your preferred database)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/lifepal.git
   cd lifepal
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up the frontend**
   ```bash
   cd ../frontend
   npm install
   ```

4. **Configure environment variables**
   Create a `.env` file in the backend directory with the following:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/lifepal
   SECRET_KEY=your-secret-key
   DEBUG=True
   ```

5. **Run database migrations**
   ```bash
   cd ../backend
   alembic upgrade head
   ```

6. **Start the development servers**
   In separate terminals:
   ```bash
   # Terminal 1: Backend
   cd backend
   uvicorn src.main:app --reload
   
   # Terminal 2: Frontend
   cd frontend
   npm run dev
   ```

## 🤖 Using the AI Assistant

Interact with your todo list using natural language commands like:
- "Add a task to buy groceries tomorrow at 5 PM"
- "Show me all my pending tasks"
- "Mark task 3 as complete"
- "What do I have scheduled for today?"

The AI will understand your intent and perform the appropriate actions through the application's API.

## 📝 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments
- Built with ❤️ and the power of open source
- Inspired by the need for more intuitive productivity tools
- Made possible by the Ollama and Django communities
