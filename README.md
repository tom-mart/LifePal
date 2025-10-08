# LifePal - Your AI-Powered Wellbeing Companion

## 🚀 Overview
LifePal is an intelligent wellbeing companion powered by Ollama that provides personalized AI assistance through natural language conversations and structured wellbeing check-ins. The application combines the power of large language models with dynamic tool calling and user context to deliver empathetic, personalized support for daily life, mental wellness, task management, and personal development.

**Key Innovation:** Database-driven tool system with Tool_Retriever pattern (ReAct framework) - add new capabilities without code changes!

## ✨ Features

### Current Features
#### 🤖 AI Chat Assistant
- **Personalized Conversations**: Context-aware AI powered by Ollama (llama3.2, qwen2.5, etc.)
- **Real-time Streaming**: Live response streaming for natural interactions
- **Conversation History**: Save and manage multiple chat conversations (general chats separate from check-ins)
- **User Context Integration**: AI knows your preferences, goals, and background
- **Dynamic Tool System**: Database-driven tools with Tool_Retriever pattern (ReAct framework)
- **Flexible Tool Execution**: Python scripts, AWS Lambda functions, or external webhooks
- **Zero-Code Tool Deployment**: Add new tools via Django admin without restarting services
- **Tool Discovery**: LLM automatically discovers and uses available tools based on user needs

#### 🧘 Wellbeing Check-ins
- **Scheduled Check-ins**: Morning catch-ups, midday check-ins, and evening reflections
- **Push Notifications**: Receive timely reminders for scheduled check-ins
- **Auto-Initiated Conversations**: Check-ins start automatically with personalized context
- **Tool-Powered Context**: Uses `start_checkin` tool to gather tasks, previous check-ins, and suggestions
- **Dynamic Reminders**: LLM can create midday check-ins based on morning conversations
- **Context-Aware Conversations**: Each check-in includes relevant user data (tasks, previous check-ins)
- **Insight Extraction**: Structured insights saved from each check-in for analytics
- **Action Tracking**: Track actions taken during check-ins (reminders created, tasks added)
- **Daily Summaries**: Aggregate insights from all check-ins into daily wellbeing logs
- **Emotion Tracking**: Assign and track emotions with intensity throughout the day
- **Completion Detection**: Automatic detection when check-in conversation is complete

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

#### 🔔 Push Notifications
- **Web Push Notifications**: Browser-based push notifications (PWA)
- **Scheduled Notifications**: Automatic check-in reminders based on user schedule
- **Snooze Support**: Snooze notifications up to 3 times (30-minute intervals)
- **Smart Scheduling**: Notifications sent 5 minutes before scheduled check-ins
- **Celery Integration**: Background task processing for reliable delivery

#### 🔒 Security & Privacy
- **End-to-End Encryption**: Sensitive user data encrypted in database
- **JWT Authentication**: Secure token-based authentication
- **Privacy Controls**: User-controlled data sharing and privacy settings
- **Secure API**: Protected endpoints with authentication middleware
- **Field-Level Encryption**: Health data, mental health history, and personal info encrypted at rest

### Upcoming Features
- **Additional Tools**: Task creation, reminder management, moment capture via tool system
- **Diary/Moments**: Journal entries with AI-powered insights
- **Advanced Analytics**: Wellbeing trends, emotion patterns, and insights visualization
- **Goal Progress Tracking**: Track progress toward personal and professional goals
- **Relationship Management**: Manage connections and support network
- **Voice Interface**: Voice-based interactions with the AI
- **Mobile Apps**: Native iOS and Android applications
- **ChromaDB Integration**: Semantic search for better tool discovery
- **Custom Check-in Schedules**: User-defined check-in times and frequencies per day type

## 🛠️ Tech Stack

### Backend
- **Python 3.12** - Modern Python with type hints
- **Django 5.1** - Robust web framework
- **Django Ninja 1.4.3** - Fast API framework with automatic OpenAPI docs
- **PostgreSQL 15** - Relational database with full-text search
- **Redis** - Message broker for Celery and caching
- **Celery** - Distributed task queue for background jobs
- **Celery Beat** - Periodic task scheduler for check-in notifications
- **JWT Authentication** - Secure token-based auth with django-ninja-jwt 5.3.7
- **Pydantic 2.11.9** - Data validation and settings management
- **Cryptography** - Field-level encryption for sensitive data
- **PyWebPush** - Web push notification support
- **CORS Middleware** - Secure cross-origin resource sharing

### Frontend
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **DaisyUI** - Beautiful component library (32 themes)
- **React Context API** - State management for auth and themes
- **Server-Sent Events** - Real-time streaming responses

### AI/ML
- **Ollama** - Local LLM inference (supports llama3.2, qwen2.5, mistral, etc.)
- **Tool_Retriever Pattern** - ReAct framework for dynamic tool discovery
- **Custom Prompt Manager** - Context-aware system prompts with tool instructions
- **Streaming Responses** - Real-time AI response generation via SSE
- **User Context Integration** - Personalized AI interactions with encrypted user data
- **Tool Calling** - Native Ollama function calling support
- **ChromaDB Ready** - Optional semantic search for tool discovery (not yet enabled)

### Database Schema
- **User Profiles** - Basic user information and preferences
- **AI Identity Profiles** - Customizable AI personality and model selection
- **LLM Context Profiles** - Detailed user context for AI personalization (encrypted)
- **User Settings** - App preferences, privacy controls, and check-in schedules
- **Conversations** - Chat history and message storage (separated by type: general/checkin)
- **Messages** - Individual chat messages with role and content
- **Tasks** - Todo items with priorities, due dates, and categories
- **Daily Logs** - Daily wellbeing summaries with emotions and completion status
- **Check-ins** - Scheduled and ad-hoc wellbeing check-ins with insights and actions
- **Emotions** - Reference data for emotion tracking
- **Tool Definitions** - Dynamic tool configurations (name, category, execution type, parameters)
- **Tool Executions** - Audit log for all tool calls with performance metrics
- **Tool Categories** - Organization and grouping of tools
- **Scheduled Notifications** - Push notification queue with snooze support
- **Push Subscriptions** - User device registrations for web push
- **Moments** - User journal entries (future)
- **Encrypted Fields** - Sensitive data protection with field-level encryption

## 🚀 Getting Started

### Prerequisites
- **Docker & Docker Compose** (recommended for production)
- **Python 3.12+** (for local development)
- **Node.js 18+** (for frontend development)
- **Ollama** installed and running (local or remote)
- **PostgreSQL 15** (included in Docker setup)
- **Redis** (included in Docker setup)

### Quick Start (Docker - Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/lifepal.git
   cd lifepal
   ```

2. **Configure environment**
   Create `.env` file in the root directory:
   ```bash
   # Database
   DB_PASSWORD=your_secure_password
   
   # Django
   SECRET_KEY=your-secret-key-here
   FIELD_ENCRYPTION_KEY=your-32-char-encryption-key
   
   # Ollama (adjust to your Ollama server)
   OLLAMA_BASE_URL=http://192.168.1.21:11434
   OLLAMA_DEFAULT_MODEL=llama3.2:latest
   
   # Push Notifications (generate with: python -c "from pywebpush import webpush; print(webpush.generate_vapid_keys())")
   VAPID_PRIVATE_KEY=your_vapid_private_key
   VAPID_PUBLIC_KEY=your_vapid_public_key
   NEXT_PUBLIC_VAPID_PUBLIC_KEY=your_vapid_public_key
   ```

3. **Deploy with Docker**
   ```bash
   ./deploy.sh
   ```
   
   This will:
   - Build Docker images for backend, frontend, and workers
   - Start PostgreSQL, Redis, and ChromaDB
   - Run database migrations
   - Start Celery workers and beat scheduler
   - Start Nginx reverse proxy

4. **Seed initial tools**
   ```bash
   sudo docker exec lifepal-backend python manage.py seed_tools
   ```

5. **Access the application**
   - **Frontend**: http://your-server-ip:8082
   - **Frontend (HTTPS)**: https://your-server-ip:8443
   - **Backend API**: http://your-server-ip:8082/api
   - **Django Admin**: http://your-server-ip:8082/admin
   - **API Docs**: http://your-server-ip:8082/api/docs

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/lifepal.git
   cd lifepal
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv .env
   source .env/bin/activate  # On Windows: .env\Scripts\activate
   cd src
   pip install -r requirements.txt
   ```

3. **Configure local database**
   - Install PostgreSQL 15 and Redis locally
   - Create database: `createdb lifepal`
   - Update `backend/src/core/settings.py` with local DB credentials

4. **Run migrations and seed tools**
   ```bash
   python manage.py migrate
   python manage.py seed_tools
   ```

5. **Create a superuser**
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
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_VAPID_PUBLIC_KEY=your_vapid_public_key
   ```

8. **Start Ollama**
   ```bash
   ollama serve
   # In another terminal:
   ollama pull llama3.2:latest
   ```

9. **Start the development servers**
   ```bash
   # Terminal 1: Backend
   cd backend/src
   python manage.py runserver
   
   # Terminal 2: Celery Worker
   cd backend/src
   celery -A core worker --loglevel=info
   
   # Terminal 3: Celery Beat
   cd backend/src
   celery -A core beat --loglevel=info
   
   # Terminal 4: Frontend
   cd frontend
   npm run dev
   ```

10. **Access the application**
    - Frontend: http://localhost:3000
    - Backend API: http://localhost:8000
    - API Docs: http://localhost:8000/api/docs
    - Admin Panel: http://localhost:8000/admin

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
├── llm_chat/          # Chat functionality, conversations, and messages
├── llm_service/       # Ollama integration and prompt management
├── llm_tools/         # Dynamic tool system (Tool_Retriever, registry, executors)
├── wellbeing/         # Check-ins, daily logs, emotions, scheduler, tasks
├── todo/              # Task management with priorities and categories
├── notifications/     # Push notifications, scheduled notifications, subscriptions
└── tools/             # Tool scripts directory
    └── scripts/       # Python scripts for tool execution
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
- **UserSettings**: App preferences (theme, timezone, notifications, check-in schedule)
- **AIIdentityProfile**: Customizable AI personality and model
- **LLMContextProfile**: Detailed user context for AI (encrypted)
- **Conversation**: Chat conversation metadata with type (general/checkin)
- **Message**: Individual chat messages with role and content
- **Task**: Todo items with priorities, categories, and due dates
- **DailyLog**: Daily wellbeing summaries with emotions and completion status
- **CheckIn**: Scheduled/ad-hoc check-ins with status, insights, and actions
- **Emotion**: Reference data for emotion tracking
- **DailyLogEmotion**: Links emotions to daily logs with intensity
- **ToolDefinition**: Dynamic tool configurations (database-driven)
- **ToolExecution**: Audit log for all tool calls
- **ToolCategory**: Tool organization and grouping
- **ScheduledNotification**: Push notification queue with snooze support
- **PushSubscription**: User device registrations for web push
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

### Docker Production Deployment

The project includes a complete Docker setup with:
- **Backend**: Django with Gunicorn
- **Frontend**: Next.js production build
- **PostgreSQL 15**: Database
- **Redis**: Message broker and cache
- **ChromaDB**: Vector database (ready for semantic search)
- **Celery Worker**: Background task processing
- **Celery Beat**: Periodic task scheduler
- **Nginx**: Reverse proxy with SSL support

**Deploy command:**
```bash
./deploy.sh
```

**Manage services:**
```bash
# View logs
sudo docker-compose logs -f backend
sudo docker-compose logs -f celery_worker

# Restart services
sudo docker-compose restart backend
sudo docker-compose restart celery_worker

# Execute commands
sudo docker exec lifepal-backend python manage.py migrate
sudo docker exec lifepal-backend python manage.py seed_tools
sudo docker exec lifepal-backend python manage.py createsuperuser

# Stop all services
sudo docker-compose down

# Stop and remove volumes (⚠️ deletes data)
sudo docker-compose down -v
```

### Production Checklist
- [x] Docker Compose setup with all services
- [x] Nginx reverse proxy with SSL support
- [x] PostgreSQL with persistent volumes
- [x] Redis for Celery and caching
- [x] Celery worker and beat scheduler
- [x] Environment variable configuration
- [x] Static file serving via Nginx
- [x] Database migrations automated
- [ ] Set proper `SECRET_KEY` and `FIELD_ENCRYPTION_KEY` in `.env`
- [ ] Configure Ollama server URL
- [ ] Generate VAPID keys for push notifications
- [ ] Set up SSL certificates for HTTPS
- [ ] Configure proper CORS origins
- [ ] Set up monitoring and logging
- [ ] Enable database backups
- [ ] Seed initial tools: `docker exec lifepal-backend python manage.py seed_tools`
- [ ] Create superuser: `docker exec lifepal-backend python manage.py createsuperuser`

## 📚 Additional Documentation

### Core Documentation
- **[Tool System Guide](TOOL_SYSTEM_GUIDE.md)** - Complete guide for the dynamic tool system with Tool_Retriever pattern
- **[Documentation Index](DOCUMENTATION_INDEX.md)** - Central hub for all documentation
- **[ChromaDB Enhancement](CHROMADB_TOOL_ENHANCEMENT.md)** - Optional semantic search integration

### Backend Documentation
- **[Check-in Usage Guide](backend/docs/checkin_usage_guide.md)** - Check-in flow implementation
- **[Check-in Migration Guide](backend/docs/checkin_migration_guide.md)** - Setup and migration
- **[Check-in Quick Reference](backend/docs/checkin_quick_reference.md)** - API examples

### Key Concepts

#### Dynamic Tool System
- **Database-Driven**: All tools stored in PostgreSQL, no hardcoded tools
- **Tool_Retriever Pattern**: ReAct framework for dynamic tool discovery
- **Zero-Code Deployment**: Add tools via Django admin without restarting
- **Three Execution Types**: 
  - **Script**: Python scripts with Django integration
  - **Lambda**: AWS Lambda functions for scalability
  - **Webhook**: External API endpoints
- **Full Audit Trail**: Every tool execution logged with performance metrics
- **Semantic Search Ready**: ChromaDB integration for better tool discovery (optional)

#### Check-in System
- **Scheduled Check-ins**: Celery Beat schedules daily check-ins based on user preferences
- **Push Notifications**: Web push notifications sent 5 minutes before scheduled time
- **Auto-Initiated Conversations**: Frontend auto-sends trigger message to start conversation
- **Tool-Powered Context**: `start_checkin` tool gathers tasks, previous check-ins, and suggestions
- **Completion Detection**: Automatic detection when check-in is complete
- **Insight Extraction**: Structured data extracted from conversations for analytics

#### Architecture Patterns
- **ReAct Pattern**: Reason → Act → Execute → Respond
- **Tool Discovery**: LLM calls `tool_retriever()` to discover available tools
- **Streaming Responses**: Server-Sent Events for real-time AI responses
- **Separation of Concerns**: General chats separate from check-in conversations
- **Background Processing**: Celery for notifications, scheduling, and summaries

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
