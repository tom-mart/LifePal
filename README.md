# LifePal - Your AI-Powered Personal Assistant

## 🚀 Overview
LifePal is an intelligent wellness companion powered by Ollama that provides personalized AI assistance through natural language conversations. The application combines the power of large language models with user context to deliver empathetic, personalized support for daily life, mental wellness, and personal development.

## ✨ Features

### Current Features

#### 🤖 AI Chat Assistant
- **Personalized Conversations**: Context-aware AI powered by Ollama
- **Real-time Streaming**: Live response streaming for natural interactions
- **Conversation History**: Save and manage multiple chat conversations
- **User Context Integration**: AI knows your preferences, goals, and background

#### 👤 User Management
- **Secure Authentication**: JWT-based authentication system
- **User Registration & Login**: Email-based account creation
- **Profile Management**: Customize your preferred name and bio
- **Settings Dashboard**: Control notifications, theme, timezone, and privacy

#### 🧠 AI Context Profile
- **Personal Information**: Age, gender, occupation, relationship status
- **Wellbeing Context**: Health conditions, mental health history, current challenges
- **Goals & Values**: Personal and professional goals, core values, interests
- **Daily Routine**: Typical schedule, sleep patterns
- **Support System**: Support network, professional support
- **Communication Preferences**: Preferred communication style, learning style
- **Encrypted Storage**: All sensitive data encrypted at rest

#### 🎨 Modern UI/UX
- **32 Theme Options**: Full DaisyUI theme support with automatic logo contrast
- **Mobile-First Design**: Responsive layout optimized for all devices
- **PWA Ready**: Progressive Web App capabilities with offline support
- **Clean Navigation**: Sidebar navigation with conversation management
- **Dark Mode Support**: Automatic logo inversion for dark themes

#### 🔒 Security & Privacy
- **End-to-End Encryption**: Sensitive user data encrypted in database
- **JWT Authentication**: Secure token-based authentication
- **Privacy Controls**: User-controlled data sharing and privacy settings
- **Secure API**: Protected endpoints with authentication middleware

### Upcoming Features
- **Diary Integration**: Journal entries with AI-powered insights
- **Todo List Management**: AI-assisted task management
- **Mood Tracking**: Track and analyze emotional wellbeing
- **Goal Progress**: Track progress toward personal and professional goals
- **Relationship Management**: Manage connections and support network
- **Voice Interface**: Voice-based interactions with the AI
- **Mobile Apps**: Native iOS and Android applications

## 🛠️ Tech Stack

### Backend
- **Python 3.12** - Modern Python with type hints
- **Django 5.1** - Robust web framework
- **Django Ninja** - Fast API framework with automatic OpenAPI docs
- **PostgreSQL** - Relational database with full-text search
- **JWT Authentication** - Secure token-based auth with django-ninja-jwt
- **Encrypted Model Fields** - Sensitive data encryption at rest
- **CORS Middleware** - Secure cross-origin resource sharing

### Frontend
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **DaisyUI** - Beautiful component library (32 themes)
- **React Context API** - State management for auth and themes
- **Server-Sent Events** - Real-time streaming responses

### AI/ML
- **Ollama** - Local LLM for natural language processing
- **Custom Prompt Manager** - Context-aware system prompts
- **Streaming Responses** - Real-time AI response generation
- **User Context Integration** - Personalized AI interactions

### Database Schema
- **User Profiles** - Basic user information and preferences
- **LLM Context Profiles** - Detailed user context for AI personalization
- **User Settings** - App preferences and privacy controls
- **Conversations** - Chat history and message storage
- **Encrypted Fields** - Sensitive data protection

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

3. **Configure backend environment**
   Create `backend/src/core/settings_local.py`:
   ```python
   from .settings import *
   
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'lifepal',
           'USER': 'your_db_user',
           'PASSWORD': 'your_db_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   
   SECRET_KEY = 'your-secret-key-here'
   FIELD_ENCRYPTION_KEY = 'your-encryption-key-here'  # For encrypted fields
   DEBUG = True
   
   OLLAMA_BASE_URL = 'http://localhost:11434'
   OLLAMA_MODEL = 'llama3.2:latest'
   ```

4. **Run database migrations**
   ```bash
   cd backend/src
   python manage.py migrate
   ```

5. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Set up the frontend**
   ```bash
   cd ../../frontend
   npm install
   ```

7. **Configure frontend environment**
   Create `frontend/.env.local`:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8080
   ```

8. **Start Ollama**
   ```bash
   ollama serve
   # In another terminal:
   ollama pull llama3.2:latest
   ```

9. **Start the development servers**
   In separate terminals:
   ```bash
   # Terminal 1: Backend
   cd backend/src
   python manage.py runserver 8080
   
   # Terminal 2: Frontend
   cd frontend
   npm run dev
   ```

10. **Access the application**
    - Frontend: http://localhost:3000
    - Backend API: http://localhost:8080
    - API Docs: http://localhost:8080/api/docs
    - Admin Panel: http://localhost:8080/admin

## 🤖 Using LifePal

### Getting Started
1. **Register an account** at http://localhost:3000
2. **Complete your AI Context Profile** (optional but recommended)
   - Navigate to Settings → AI Context
   - Fill in personal information, goals, preferences
   - This helps the AI provide personalized responses
3. **Start chatting** with your AI assistant

### AI Conversations
The AI assistant (Frankie) can help with:
- **Emotional Support**: Discuss feelings, challenges, and concerns
- **Goal Setting**: Define and track personal/professional goals
- **Daily Planning**: Organize your day and priorities
- **Wellness Advice**: Get tips for mental health and wellbeing
- **General Conversation**: Chat about interests, ideas, and more

### Example Interactions
- "What do you know about me?"
- "I'm feeling stressed about work, can you help?"
- "What are some good coping mechanisms for anxiety?"
- "Help me set some personal goals for this year"
- "Tell me about my support network"

### Personalization
The AI uses your context profile to:
- Address you by your preferred name
- Remember your goals and values
- Understand your communication style
- Provide relevant, personalized advice
- Respect topics you want to avoid

## 📱 User Interface

### Chat Interface
- **Sidebar Navigation**: Access conversations, create new chats
- **Real-time Streaming**: See AI responses as they're generated
- **Conversation History**: Save and revisit past conversations
- **Mobile-Friendly**: Responsive design for all devices

### Settings & Profile
- **Profile**: Set preferred name and bio
- **Settings**: Configure theme, timezone, notifications, privacy
- **AI Context**: Comprehensive profile for AI personalization
  - Personal Information
  - Wellbeing Context
  - Goals & Values
  - Daily Routine
  - Support System
  - Communication Preferences

### Theme Customization
- 32 beautiful themes from DaisyUI
- Automatic logo contrast adjustment
- Dark mode support
- Persistent theme selection

## 🔐 Security Features

### Data Protection
- **Encrypted Storage**: Sensitive user data encrypted at rest
- **Secure Authentication**: JWT-based token system
- **HTTPS Ready**: Production-ready security configuration
- **CORS Protection**: Controlled cross-origin access

### Privacy Controls
- **Data Sharing Consent**: User-controlled data sharing
- **Privacy Settings**: Granular privacy controls
- **Encrypted Fields**: Health, mental health, and personal data encrypted
- **Admin Access Logging**: Track who accesses sensitive data

## 🏗️ Architecture

### Backend Structure
```
backend/src/
├── core/              # Django settings and configuration
├── users/             # User management, profiles, authentication
├── llm_chat/          # Chat functionality and conversation management
├── llm_service/       # Ollama integration and prompt management
├── diary/             # Diary entries (future)
└── todo/              # Todo list management (future)
```

### Frontend Structure
```
frontend/src/
├── app/               # Next.js App Router pages
│   ├── chat/         # Chat interface
│   ├── login/        # Authentication
│   ├── profile/      # User profile
│   ├── settings/     # App settings
│   └── context/      # AI context profile
├── components/        # Reusable React components
├── contexts/          # React Context providers (Auth, Theme)
└── lib/              # Utilities and API client
```

## 📊 Database Schema

### Key Models
- **User**: Django auth user model
- **UserProfile**: Basic user information (preferred_name, bio)
- **UserSettings**: App preferences (theme, timezone, notifications)
- **LLMContextProfile**: Detailed user context for AI (encrypted)
- **Conversation**: Chat conversation metadata
- **Message**: Individual chat messages

## 🧪 Development

### Running Tests
```bash
# Backend tests
cd backend/src
python manage.py test

# Frontend tests
cd frontend
npm test
```

### Code Quality
```bash
# Backend linting
cd backend
flake8 src/

# Frontend linting
cd frontend
npm run lint
```

### Database Management
```bash
# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Access Django shell
python manage.py shell
```

## 🚀 Deployment

### Production Checklist
- [ ] Set `DEBUG = False` in settings
- [ ] Configure proper `SECRET_KEY` and `FIELD_ENCRYPTION_KEY`
- [ ] Set up PostgreSQL database
- [ ] Configure HTTPS/SSL
- [ ] Set up proper CORS origins
- [ ] Configure static file serving
- [ ] Set up Ollama on production server
- [ ] Configure environment variables
- [ ] Set up monitoring and logging
- [ ] Enable database backups

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments
- Built with ❤️ and the power of open source
- Inspired by the need for more intuitive productivity tools
- Made possible by the Ollama and Django communities
