# LifePal - Your AI-Powered Personal Assistant

## 🚀 Overview
LifePal is an intelligent wellbeing companion powered by Ollama that provides personalized AI assistance through natural language conversations and structured wellbeing check-ins. The application combines the power of large language models with user context to deliver empathetic, personalized support for daily life, mental wellness, task management, and personal development.

## ✨ Features

### Current Features
#### 🤖 AI Chat Assistant
- **Personalized Conversations**: Context-aware AI powered by Ollama
- **Real-time Streaming**: Live response streaming for natural interactions
- **Conversation History**: Save and manage multiple chat conversations (general chats separate from check-ins)
- **User Context Integration**: AI knows your preferences, goals, and background
- **Intent Detection**: Automatic detection and handling of user intents (tasks, events, etc.)

#### 🧘 Wellbeing Check-ins
- **Scheduled Check-ins**: Morning catch-ups, midday check-ins, and evening reflections
- **Dynamic Reminders**: LLM can create midday check-ins based on morning conversations
- **Context-Aware Conversations**: Each check-in includes relevant user data (tasks, previous check-ins)
- **Insight Extraction**: Structured insights saved from each check-in for analytics
- **Action Tracking**: Track actions taken during check-ins (reminders created, tasks added)
- **Daily Summaries**: Aggregate insights from all check-ins into daily wellbeing logs
- **Emotion Tracking**: Assign and track emotions with intensity throughout the day

#### ✅ Task Management
- **Smart Todo Lists**: Create and manage tasks with priorities and due dates
- **AI Integration**: LLM can create tasks during conversations
- **Task Context**: Tasks appear in check-in contexts for better planning

#### 👤 User Management
- **Secure Authentication**: JWT-based authentication system
- **User Registration & Login**: Email-based account creation
- **Profile Management**: Customize your preferred name and bio
- **Settings Dashboard**: Control notifications, theme, timezone, and privacy

#### 🧠 AI Identity & Context
- **Customizable AI Identity**: Define AI name, role, personality, and communication style
- **Model Selection**: Choose preferred Ollama model for conversations
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
- **Diary/Moments**: Journal entries with AI-powered insights
- **Advanced Analytics**: Wellbeing trends, emotion patterns, and insights visualization
- **Goal Progress Tracking**: Track progress toward personal and professional goals
- **Relationship Management**: Manage connections and support network
- **Voice Interface**: Voice-based interactions with the AI
- **Mobile Apps**: Native iOS and Android applications
- **Tool Calling**: LLM can call external tools (create tasks, set reminders, save moments)
- **Custom Check-in Schedules**: User-defined check-in times and frequencies

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
- **AI Identity Profiles** - Customizable AI personality and model selection
- **LLM Context Profiles** - Detailed user context for AI personalization
- **User Settings** - App preferences and privacy controls
- **Conversations** - Chat history and message storage (separated by type: general/checkin)
- **Messages** - Individual chat messages with role and content
- **Intents** - Detected user intents with parameters
- **Tasks** - Todo items with priorities, due dates, and categories
- **Daily Logs** - Daily wellbeing summaries with emotions
- **Check-ins** - Scheduled and ad-hoc wellbeing check-ins with insights
- **Emotions** - Reference data for emotion tracking
- **Moments** - User journal entries (future)
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
2. **Customize your AI Identity** (optional)
   - Navigate to Settings → AI Identity
   - Define AI name, role, personality, and communication style
   - Select your preferred Ollama model
3. **Complete your AI Context Profile** (optional but recommended)
   - Navigate to Settings → AI Context
   - Fill in personal information, goals, preferences
   - This helps the AI provide personalized responses
4. **Start chatting** with your AI assistant

### AI Conversations
The AI assistant can help with:
- **Emotional Support**: Discuss feelings, challenges, and concerns
- **Goal Setting**: Define and track personal/professional goals
- **Daily Planning**: Organize your day and priorities
- **Task Management**: Create and manage todos during conversations
- **Wellness Advice**: Get tips for mental health and wellbeing
- **General Conversation**: Chat about interests, ideas, and more

### Wellbeing Check-ins
LifePal includes a structured wellbeing system with three types of check-ins:

#### Morning Catch-Up (8:00 AM default)
- How you're feeling physically and mentally
- What's on your schedule today
- Any concerns or upcoming challenges
- LLM can create dynamic midday reminders for stressful events

#### Midday Check-In (Dynamic)
- Created by LLM during morning check-in if needed
- Follow-up before stressful events
- Quick emotional check-in
- Offer support and preparation tips

#### Evening Reflection (8:00 PM default)
- Reflect on the day's events
- Identify highlights and challenges
- Assign emotions to the day
- Plan for tomorrow
- Generate daily summary

**Check-in Features:**
- Conversations are separate from general chat history
- Each check-in includes context from previous check-ins
- Your tasks for today/week are included in the context
- LLM extracts structured insights for analytics
- Actions taken (reminders, tasks) are tracked

### Example Interactions
- "What do you know about me?"
- "I'm feeling stressed about work, can you help?"
- "What are some good coping mechanisms for anxiety?"
- "Help me set some personal goals for this year"
- "Add a task to prepare for tomorrow's meeting"
- "Tell me about my support network"

### Personalization
The AI uses your context profile to:
- Address you by your preferred name
- Remember your goals and values
- Understand your communication style
- Provide relevant, personalized advice
- Respect topics you want to avoid
- Include your tasks in check-in conversations

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
├── llm_chat/          # Chat functionality, conversations, and intent detection
├── llm_service/       # Ollama integration and prompt management
├── wellbeing/         # Check-ins, daily logs, emotions, and moments
├── todo/              # Task management with priorities and categories
└── notifications/     # Push notifications and reminders
```

### Frontend Structure
```
frontend/src/
├── app/               # Next.js App Router pages
│   ├── chat/         # Chat interface
│   ├── login/        # Authentication
│   ├── profile/      # User profile
│   ├── settings/     # App settings and notifications
│   ├── context/      # AI context profile
│   └── ai-identity/  # AI identity customization
├── components/        # Reusable React components
├── contexts/          # React Context providers (Auth, Theme)
└── lib/              # Utilities and API client
```

## 📊 Database Schema

### Key Models
- **User**: Django auth user model
- **UserProfile**: Basic user information (preferred_name, bio)
- **UserSettings**: App preferences (theme, timezone, notifications)
- **AIIdentityProfile**: Customizable AI personality and model
- **LLMContextProfile**: Detailed user context for AI (encrypted)
- **Conversation**: Chat conversation metadata with type (general/checkin)
- **Message**: Individual chat messages with role and content
- **Intent**: Detected user intents with confidence and parameters
- **Task**: Todo items with priorities, categories, and due dates
- **DailyLog**: Daily wellbeing summaries with emotions and completion status
- **CheckIn**: Scheduled/ad-hoc check-ins with status, insights, and actions
- **Emotion**: Reference data for emotion tracking
- **DailyLogEmotion**: Links emotions to daily logs with intensity
- **Moment**: User journal entries (future)

## 📡 API Documentation

### Main API Endpoints

#### Authentication
- `POST /api/token/pair` - Get access and refresh tokens
- `POST /api/token/refresh` - Refresh access token
- `POST /api/token/verify` - Verify token validity

#### Chat
- `GET /api/chat/conversations` - List general conversations (excludes check-ins)
- `GET /api/chat/conversations/{id}` - Get conversation with messages
- `POST /api/chat/send` - Send message (non-streaming)
- `POST /api/chat/send/stream` - Send message (streaming)
- `DELETE /api/chat/conversations/{id}` - Delete conversation

#### Wellbeing
- `GET /api/wellbeing/checkins/today` - Get today's check-ins
- `GET /api/wellbeing/checkins/{id}` - Get specific check-in
- `POST /api/wellbeing/checkins/{id}/start` - Start check-in conversation
- `POST /api/wellbeing/checkins/{id}/complete` - Complete check-in with insights
- `POST /api/wellbeing/checkins/{id}/skip` - Skip check-in
- `POST /api/wellbeing/checkins/adhoc` - Create ad-hoc check-in
- `GET /api/wellbeing/daily-log/today` - Get today's daily log
- `GET /api/wellbeing/daily-log/{date}` - Get daily log by date

#### Tasks
- `GET /api/todo/tasks` - List tasks
- `POST /api/todo/tasks` - Create task
- `PUT /api/todo/tasks/{id}` - Update task
- `DELETE /api/todo/tasks/{id}` - Delete task

#### Users
- `POST /api/users/register` - Register new user
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update profile
- `GET /api/users/settings` - Get user settings
- `PUT /api/users/settings` - Update settings
- `GET /api/users/ai-identity` - Get AI identity profile
- `PUT /api/users/ai-identity` - Update AI identity
- `GET /api/users/context` - Get LLM context profile
- `PUT /api/users/context` - Update context profile

#### Notifications
- `GET /api/notifications/` - List notifications
- `POST /api/notifications/register-device` - Register push notification device
- `POST /api/notifications/test` - Send test notification

**Interactive API Docs**: Visit `http://localhost:8080/api/docs` for full Swagger documentation

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
cd backend/src
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Access Django shell
python manage.py shell
```

### Scheduling Check-ins
```bash
# Schedule check-ins for all users (run daily at midnight)
python manage.py schedule_checkins

# Or use the scheduler programmatically
python manage.py shell
>>> from wellbeing.scheduler import CheckInScheduler
>>> from django.contrib.auth.models import User
>>> user = User.objects.first()
>>> CheckInScheduler.schedule_daily_checkins(user)
```

### Populate Initial Data
```bash
# Create emotion reference data
python manage.py shell
>>> from wellbeing.models import Emotion
>>> emotions = [
...     {'name': 'Happy', 'emoji': '😊'},
...     {'name': 'Sad', 'emoji': '😢'},
...     {'name': 'Anxious', 'emoji': '😰'},
...     {'name': 'Calm', 'emoji': '😌'},
...     {'name': 'Excited', 'emoji': '🤩'},
...     {'name': 'Stressed', 'emoji': '😫'},
... ]
>>> for e in emotions:
...     Emotion.objects.get_or_create(name=e['name'], defaults={'emoji': e['emoji']})
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
- [ ] Set up check-in scheduler (cron or Celery)
- [ ] Configure push notifications for check-ins
- [ ] Populate emotion reference data

## 📚 Additional Documentation

Detailed documentation is available in the `backend/docs/` directory:

- **[Check-in Usage Guide](backend/docs/checkin_usage_guide.md)** - Comprehensive examples for implementing check-in flows
- **[Check-in Migration Guide](backend/docs/checkin_migration_guide.md)** - Step-by-step setup and migration instructions
- **[Check-in Quick Reference](backend/docs/checkin_quick_reference.md)** - Quick code snippets and API examples

### Key Documentation Topics
- How to schedule check-ins (morning, midday, evening)
- Building context for check-in conversations
- Extracting and storing insights
- Implementing tool calling (create reminders, tasks, moments)
- Setting up notification scheduling
- Frontend integration examples

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
- Inspired by the need for personalized wellbeing tools
- Powered by Ollama, Django, and Next.js communities
