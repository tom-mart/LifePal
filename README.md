# LifePal

An AI-powered personal wellness platform that provides personalized fitness coaching, health tracking, and lifestyle guidance through intelligent conversational agents.

## Overview

LifePal uses AI agents built with [pydantic-ai](https://ai.pydantic.dev/) to deliver personalized wellness coaching. The platform features a multi-agent architecture where specialized AI coaches handle different aspects of wellness, coordinated by an intelligent operator agent.

### How It Works

1. **User sends a message** → Operator Agent analyzes intent
2. **Operator routes to specialist** → Fitness, Wellbeing, or General agent
3. **Specialist processes request** → Uses domain-specific tools and knowledge
4. **Agent responds** → Streaming or complete response with memory retention
5. **Conversation continues** → Context maintained across sessions with semantic search

## Features

### 🤖 Multi-Agent Architecture

**Operator Agent** - Intelligent conversation router
- Analyzes user intent and routes to appropriate specialist
- Seamlessly switches between agents mid-conversation
- Maintains conversation context across agent transitions
- Handles agent hand-offs transparently

**Form Agent** - Structured data collection specialist
- Manages guided onboarding flows
- One-question-at-a-time interface for user-friendly data gathering
- Uses LLM to extract answers from natural language
- Validates inputs with domain-specific rules
- Returns control to original agent after completion

**Fitness Coach Agent** - Comprehensive fitness guidance
- **Onboarding**: Conversational profile creation with FormAgent integration
- **Planning**: Custom workout and running schedules
- **Tracking**: Body measurements with automatic trend analysis
- **Goals**: SMART goal framework with progress monitoring
- **Equipment**: Smart equipment management based on location
- **Motivation**: Progress monitoring and encouragement

**General Agent** - Casual conversation and general queries
- Handles non-fitness related questions
- Provides general wellness advice
- Maintains engaging conversation flow

### 💪 Fitness Module

**Onboarding Flow**
- Automatic trigger when new user starts fitness conversation
- FormAgent handles guided 7-question profile creation:
  1. Fitness level (inactive → very active)
  2. Exercises per week (0-7)
  3. Runs per week (0-7)
  4. Exercise days (if applicable)
  5. Run days (if applicable)
  6. Exercise location (home/gym/both)
  7. Injuries (tracked separately)
  8. Physical restrictions (tracked separately)
- Smart equipment auto-assignment:
  - **Gym**: All equipment available
  - **Home**: Body weight only (can add more)
  - **Both**: All equipment available
- Natural language processing extracts answers from conversational input
- Returns to FitnessAgent after completion

**Profile Management**
- View complete fitness profile with `get_fitness_profile()`
- Update entire profile or specific fields
- Add/remove home equipment via conversation
- Equipment persists across profile updates

**Goal Setting & Tracking**
- Create SMART fitness goals with target dates
- Track multiple concurrent goals
- Update goal status (in_progress/completed/abandoned)

**Body Measurement Tracking**
- Weight, body fat %, BMI, muscle mass
- Circumference measurements (waist, hip, bicep, chest, thigh)
- Automatic trend calculation
- Historical tracking with notes

### 🔧 Technical Features

**Conversation Management**
- Streaming responses via Server-Sent Events (SSE)
- Short-term memory with context pruning
- Long-term memory via semantic search
- Message embeddings for retrieval

**Agent Intelligence**
- Tool calling with pydantic-ai
- Multi-step reasoning
- Context-aware responses
- Profile validation with decorators

## Technology Stack

### Backend
- **Django 5.x** - Web framework
- **Django Ninja** - Modern REST API
- **pydantic-ai** - AI agent orchestration
- **PostgreSQL + pgvector** - Database with vector search
- **Ollama** - Local LLM (qwen3-32k, nomic-embed-text)
- **Django Q2** - Task queue
- **Firebase Admin SDK** - Push notifications

### Client
- **Android App** - Basic native mobile front end (in development)

## Project Structure

```
src/
├── agents/              # Core agent framework
│   ├── base.py         # BaseAgent class
│   ├── registry.py     # Agent registration
│   ├── models.py       # Agent, Conversation, Message models
│   ├── tools.py        # Common tools (RAG, preferences)
│   └── services/       # LLM, embedding, memory services
├── chat/               # Chat API and routing
│   ├── api.py         # REST endpoints
│   ├── agents/        # Operator, form, general agents
│   └── helpers.py     # Message utilities
├── fitness/            # Fitness domain
│   ├── models.py      # Profile, Goal, Measurement models
│   ├── agents/        # Fitness agent with tools
│   └── exercise_data/ # Exercise database (1300+)
├── notifications/      # Push notifications
└── core/              # Django settings and config
```

## Setup

### Prerequisites
- Python 3.11+
- Ollama server running with qwen3-32k model
- PostgreSQL with pgvector extension

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd lifepal/backend/src
```

2. **Configure environment**
```bash
# Create .env file with required variables
OLLAMA_BASE_URL=http://localhost:11434/v1/
DB_NAME=lifepal
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
```

3. **Install dependencies and setup**
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py sync_agents
python manage.py import_fitness_data
```

## API Endpoints

### Chat
- `POST /api/chat/stream` - Streaming chat with SSE
- `POST /api/chat/chat` - Non-streaming chat
- `GET /api/chat/agents` - List available agents

### Example Request
```json
{
  "message": "I want to start working out",
  "conversation_id": null,
  "agent_id": 1
}
```

## Tools Reference
| Tool | Purpose | Parameters |
|------|---------|------------|
| `get_fitness_profile()` | Check if user has completed profile | None |
| `create_or_update_fitness_profile()` | Create/update complete profile | fitness_level, exercises_per_week, runs_per_week, exercise_days, run_days, exercise_location, injuries, restrictions, equipment_names (optional) |
| `add_home_equipment()` | Add equipment for home workouts | equipment_names (list) |
| `create_fitness_goal()` | Set new SMART goals | goal, target_date, success_metrics |
| `get_fitness_goals()` | View goals by status | status (optional: in_progress/completed/abandoned) |
| `update_fitness_goal_status()` | Update goal progress | goal_description, new_status |
| `add_measurement()` | Record body measurements | measurement_type, value, date_recorded (optional), notes (optional) |
| `get_measurements()` | View measurement history | measurement_type (optional), limit (default 10) |
| `get_latest_measurement()` | Get recent measurement with trend | measurement_type |

### Common Tools (All Agents)
| Tool | Purpose |
|------|---------|
| `search_past_conversations()` | Search conversation summaries |
| `search_past_messages()` | Search specific messages |
| `update_agent_preferences()` | Customize agent behavior |
| `get_agent_preferences()` | View current preferences |

## Database Models

### Agents
- **Agent** - Agent configuration
- **Conversation** - User conversations with memory
- **Message** - Chat messages with embeddings
- **UserAgentPreference** - Agent customization

### Fitness
- **UserFitnessProfile** - User fitness profile
- **FitnessGoal** - Goals with tracking
- **UserMeasurement** - Body measurements
- **Exercise** - Exercise database (1300+)
- **Equipment, BodyPart, BodyArea** - Exercise metadata
- **WorkoutPlan** - Workout program structure
- **Workout** - Individual workout sessions
- **ExerciseSet** - Exercise sets within workouts
- **FitnessTest, FitnessTestExercise** - Fitness assessments
- **FavouriteExercise, ExcludedExercise** - User preferences

### Notifications
- **Device** - Push notification devices

## Planned Features

### 🏋️ Adaptive Workout Planning
The next major feature is intelligent, adaptive workout planning that evolves with the user:

**How it works:**
1. **Fitness Test Baseline** - User starts with a fitness test to establish baseline strength, endurance, and mobility
2. **AI Plans Next Workout** - After each workout, AI analyzes:
   - User's stated goals
   - Last workout performance and feedback
   - Progress trends
   - Recovery status
   - Available equipment and schedule
3. **Dynamic Adaptation** - No fixed 4-week or 8-week programs. Each workout is planned based on real-time data
4. **Calendar Integration** - Scheduling Agent manages the user's calendar:
   - Fitness Agent creates the workout
   - Scheduling Agent books it in the calendar
   - Sends reminders and manages rescheduling

**Benefits:**
- Truly personalized progression
- Responds to user feedback immediately
- Adapts to missed workouts or schedule changes
- Prevents plateaus with intelligent variation

### 📅 Scheduling Assistant Agent
- Calendar management and integration
- Smart workout scheduling based on availability
- Automatic rescheduling when plans change
- Reminder notifications
- Coordinates with Fitness Agent for optimal timing

### 🧘 Wellbeing & Mindfulness (Future)

**Personal Diary** - The core feature:
- Users can add diary entries with photos
- Wellness Agent analyzes entries to understand:
  - User's struggles and challenges
  - Emotional state and patterns
  - Mental health trends over time
- AI provides personalized support based on diary insights
- Mood tracking and stress management
- Sleep quality monitoring
- Holistic mental and physical health view

## DevelopmentMeal planning, calorie tracking, macro recommendations
- **Integration Hub**: Connect with fitness trackers, smart scales, wearables

### 🚀 Platform Improvements
- **Mobile Apps**: Native iOS and Android apps (currently web-based)
- **Multi-language Support**: Localization for global users

## Development Workflow

### Adding a New Agent

1. **Create agent file**: `<app>/agents/my_agent.py`
```python
from agents.base import BaseAgent
from agents import registry
from agents.services.deps import AgentDeps
from pydantic_ai import RunContext

class MyAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return "Your specialized system prompt"
    
    def get_tools(self) -> list:
        return [my_tool_function]

def my_tool_function(ctx: RunContext[AgentDeps], param: str) -> str:
    """Tool docstring for LLM"""
   Development

### Adding a New Agent

1. Create `<app>/agents/my_agent.py`
2. Inherit from `BaseAgent` and implement methods
3. Define tools with type hints and docstrings
4. Register: `registry.register('my_agent', MyAgent)`
5. Configure in `<app>/agents/agent_config.py`
6. Import in `<app>/apps.py`
7. Run: `python manage.py sync_agents`

### Best Practices
- Clear docstrings for LLM understanding
- Type hints for validation

## Monitoring

```bash
# Check agent activity in console output
# Look for [FITNESS], [AGENT], [LLM] prefixed messages
```

Debug data is stored in `Message.debug_data` with full LLM interaction history.

## License

MIT License

## Acknowledgments

- [pydantic-ai](https://ai.pydantic.dev/) - AI agent framework
- [Django](https://www.djangoproject.com/) - Web framework
- [Ollama](https://ollama.ai/) - Local LLM
- [pgvector](https://github.com/pgvector/pgvector) - Vector search