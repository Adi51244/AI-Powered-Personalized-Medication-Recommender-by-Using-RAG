# MediRAG - AI-Powered Personalized Medication Recommender

An intelligent clinical decision support system that combines Retrieval-Augmented Generation (RAG) with machine learning to provide personalized medication recommendations based on patient symptoms, medical history, and safety profiles.

## 🎯 Features

### Core Functionality
- **Intelligent Diagnosis**: AI-powered symptom analysis and differential diagnosis
- **Safe Medication Recommendations**: Evidence-based medication suggestions with contraindication checking
- **Patient Safety Validation**: Real-time drug interaction detection and safety alerts
- **Explainable AI**: Simplified medical explanations without jargon
- **Evidence Retrieval**: PDF/document citations for recommendation justification

### Technical Highlights
- **RAG Pipeline**: FAISS vector search + Claude AI for accurate context
- **Full-Stack**: Next.js frontend + FastAPI backend
- **Authentication**: Supabase email/OAuth integration
- **Database**: Secure row-level security (RLS) with Supabase PostgreSQL
- **Performance**: Optimized safety validation (34s → <0.1s per request)

## 🏗️ Architecture

```
MediRAG/
├── frontend/              # Next.js + React + TypeScript
│   ├── app/              # Pages (auth, dashboard, diagnosis)
│   ├── components/       # Reusable UI components
│   ├── lib/             # Auth, API client, utilities
│   └── styles/          # Tailwind CSS
│
└── backend/              # FastAPI + Python
    ├── app/
    │   ├── api/         # REST endpoints
    │   ├── core/        # RAG, ML, explainability
    │   ├── db/          # Database layer
    │   ├── ml/          # Feature engineering
    │   └── main.py      # Application entry
    └── tests/           # Unit/integration tests
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Supabase account
- Claude API key

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your Supabase & Claude API credentials

# Run server
uvicorn app.main:app --reload
```

Server runs at: `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment
cp .env.local.example .env.local
# Edit .env.local with your Supabase credentials

# Run development server
npm run dev
```

App runs at: `http://localhost:3000`

## 🔐 Environment Setup

### Backend (.env)
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
ANTHROPIC_API_KEY=your_claude_api_key
DATABASE_URL=your_database_url
```

### Frontend (.env.local)
```
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

## 📊 Key Components

### Frontend Pages
- **Login/Signup** - Email/Google authentication
- **Dashboard** - Patient diagnosis history & statistics
- **New Diagnosis** - Symptom input & AI analysis
- **Profile** - Account settings & logout
- **Admin Dashboard** - User management (admin only)

### Backend APIs
- **Auth** - User registration & session management
- **Diagnoses** - Create, retrieve, list patient diagnoses
- **Recommendations** - Get medication suggestions & safety info
- **Explainability** - Simplified medical explanations
- **Safety** - Drug interaction & contraindication checks

## 🧠 How It Works

1. **Patient Input** → User submits symptoms and medical history
2. **RAG Pipeline** → System searches medical knowledge base
3. **AI Analysis** → Claude generates personalized diagnosis
4. **Safety Check** → Validates for drug interactions & contraindications
5. **Explanations** → Provides simplified medical explanations
6. **Results** → Display with evidence sources and safety alerts

## 📈 Performance

- **Request Latency**: 3-5 seconds (including API calls)
- **FAISS Search**: ~1s for vector similarity
- **Safety Validation**: <0.1s (pre-loaded data)
- **LLM Generation**: ~8s (Claude API)

## 🛡️ Security Features

- **Row-Level Security (RLS)**: Database access based on user roles
- **Authenticated APIs**: All endpoints require authentication
- **Audit Logging**: Track all diagnoses and recommendations
- **No PHI Storage**: System doesn't store sensitive patient data
- **Secure Sessions**: Supabase auth tokens managed securely

## 🧪 Testing

```bash
# Run backend tests
cd backend
pytest

# Run frontend tests
cd frontend
npm test
```

## 📝 API Documentation

Visit `http://localhost:8000/docs` (Swagger UI) for interactive API documentation.

## 🤝 Contributing

1. Create a feature branch (`git checkout -b feature/amazing-feature`)
2. Commit changes (`git commit -m 'Add amazing feature'`)
3. Push to branch (`git push origin feature/amazing-feature`)
4. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## ⚠️ Medical Disclaimer

**IMPORTANT**: This system is designed for educational and research purposes only. It should NOT be used for actual medical advice or clinical decision-making without professional medical review. Always consult with qualified healthcare professionals for medical guidance.

## 🆘 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation in the project
- Review API documentation at `/docs`

---

**Built with ❤️ for better healthcare AI**
