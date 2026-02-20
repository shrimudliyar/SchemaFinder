from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'

app = FastAPI()
api_router = APIRouter(prefix="/api")
security = HTTPBearer()

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    email: str
    name: str
    created_at: str

class QuizSubmission(BaseModel):
    age: int
    gender: str
    state: str
    area: str
    income: str
    occupation: str
    education: str
    category: str
    has_land: str
    is_disabled: str

class SavedScheme(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    scheme_id: str
    saved_at: str

class SchemeResponse(BaseModel):
    id: str
    name: str
    category: str
    description: str
    benefits: List[str]
    documents: List[str]
    apply_link: str
    eligibility_match: Optional[str] = None

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id: str, email: str) -> str:
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.now(timezone.utc) + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

HARDCODED_SCHEMES = [
    {
        "id": "scheme_1",
        "name": "PM Scholarship Scheme",
        "category": "Education",
        "description": "Scholarship for students from defense background",
        "benefits": ["₹2,500/month for boys", "₹3,000/month for girls", "Valid for professional courses"],
        "documents": ["Aadhaar Card", "Income Certificate", "Previous Marksheet", "Bank Passbook"],
        "apply_link": "https://scholarships.gov.in",
        "eligibility": {"age_min": 18, "age_max": 25, "occupation": ["Student"], "income": ["Below ₹1,00,000", "₹1,00,000 – ₹3,00,000"]}
    },
    {
        "id": "scheme_2",
        "name": "Post Matric Scholarship (SC/ST/OBC)",
        "category": "Education",
        "description": "Post-matric scholarship for SC/ST/OBC students",
        "benefits": ["Full tuition fee reimbursement", "Monthly maintenance allowance", "Book allowance"],
        "documents": ["Caste Certificate", "Income Certificate", "Aadhaar", "Fee Receipt"],
        "apply_link": "https://scholarships.gov.in",
        "eligibility": {"age_min": 16, "age_max": 30, "occupation": ["Student"], "category": ["SC", "ST", "OBC"], "income": ["Below ₹1,00,000", "₹1,00,000 – ₹3,00,000", "₹3,00,000 – ₹8,00,000"]}
    },
    {
        "id": "scheme_3",
        "name": "PM-KISAN",
        "category": "Agriculture",
        "description": "Income support to all farmer families",
        "benefits": ["₹6,000 per year in three installments", "Direct benefit transfer to bank"],
        "documents": ["Aadhaar", "Land Records", "Bank Account Details"],
        "apply_link": "https://pmkisan.gov.in",
        "eligibility": {"occupation": ["Farmer"], "has_land": ["Yes"]}
    },
    {
        "id": "scheme_4",
        "name": "Ayushman Bharat (PM-JAY)",
        "category": "Health",
        "description": "Health insurance coverage up to ₹5 lakh per family per year",
        "benefits": ["Cashless treatment", "Coverage for secondary and tertiary care", "Free medicines"],
        "documents": ["Aadhaar", "Ration Card", "Income Proof"],
        "apply_link": "https://pmjay.gov.in",
        "eligibility": {"income": ["Below ₹1,00,000", "₹1,00,000 – ₹3,00,000"]}
    },
    {
        "id": "scheme_5",
        "name": "Indira Gandhi National Old Age Pension",
        "category": "Pension",
        "description": "Monthly pension for senior citizens",
        "benefits": ["₹200-500 per month based on age", "Direct bank transfer"],
        "documents": ["Age Proof", "Aadhaar", "Income Certificate"],
        "apply_link": "https://nsap.nic.in",
        "eligibility": {"age_min": 60, "income": ["Below ₹1,00,000"]}
    },
    {
        "id": "scheme_6",
        "name": "PM Matru Vandana Yojana",
        "category": "Women",
        "description": "Maternity benefit for pregnant and lactating mothers",
        "benefits": ["₹5,000 cash benefit", "Nutritional support", "Health check-ups"],
        "documents": ["Aadhaar", "Pregnancy Certificate", "Bank Details"],
        "apply_link": "https://pmmvy.wcd.gov.in",
        "eligibility": {"gender": ["Female"], "age_min": 18, "age_max": 45}
    },
    {
        "id": "scheme_7",
        "name": "MUDRA Loan Scheme",
        "category": "Employment",
        "description": "Loans up to ₹10 lakh for small businesses",
        "benefits": ["No collateral required", "Low interest rates", "Easy repayment terms"],
        "documents": ["Aadhaar", "Business Plan", "Bank Statement"],
        "apply_link": "https://mudra.org.in",
        "eligibility": {"occupation": ["Self-employed", "Unemployed"]}
    },
    {
        "id": "scheme_8",
        "name": "PM Awas Yojana (Urban)",
        "category": "Housing",
        "description": "Affordable housing for urban poor",
        "benefits": ["Interest subsidy on home loans", "Direct assistance for construction"],
        "documents": ["Aadhaar", "Income Certificate", "Property Documents"],
        "apply_link": "https://pmaymis.gov.in",
        "eligibility": {"area": ["Urban"], "income": ["Below ₹1,00,000", "₹1,00,000 – ₹3,00,000", "₹3,00,000 – ₹8,00,000"]}
    },
    {
        "id": "scheme_9",
        "name": "AICTE Pragati Scholarship (Girls)",
        "category": "Education",
        "description": "Scholarship for girl students in technical education",
        "benefits": ["₹50,000 per year", "For diploma/degree courses"],
        "documents": ["Aadhaar", "Admission Proof", "Income Certificate", "Bank Details"],
        "apply_link": "https://scholarships.gov.in",
        "eligibility": {"gender": ["Female"], "occupation": ["Student"], "age_min": 17, "age_max": 25, "income": ["Below ₹1,00,000", "₹1,00,000 – ₹3,00,000", "₹3,00,000 – ₹8,00,000"]}
    },
    {
        "id": "scheme_10",
        "name": "AICTE Saksham Scholarship (Divyang)",
        "category": "Education",
        "description": "Scholarship for differently-abled students",
        "benefits": ["₹50,000 per year", "For technical courses", "Special support"],
        "documents": ["Disability Certificate", "Aadhaar", "Income Certificate", "College Admission Proof"],
        "apply_link": "https://scholarships.gov.in",
        "eligibility": {"is_disabled": ["Yes"], "occupation": ["Student"], "age_min": 17, "age_max": 30}
    }
]

def check_eligibility(quiz: QuizSubmission, scheme: dict) -> bool:
    eligibility = scheme.get('eligibility', {})
    
    if 'age_min' in eligibility and quiz.age < eligibility['age_min']:
        return False
    if 'age_max' in eligibility and quiz.age > eligibility['age_max']:
        return False
    if 'gender' in eligibility and quiz.gender not in eligibility['gender']:
        return False
    if 'occupation' in eligibility and quiz.occupation not in eligibility['occupation']:
        return False
    if 'category' in eligibility and quiz.category not in eligibility['category']:
        return False
    if 'income' in eligibility and quiz.income not in eligibility['income']:
        return False
    if 'area' in eligibility and quiz.area not in eligibility['area']:
        return False
    if 'has_land' in eligibility and quiz.has_land not in eligibility['has_land']:
        return False
    if 'is_disabled' in eligibility and quiz.is_disabled not in eligibility['is_disabled']:
        return False
    
    return True

@api_router.post("/auth/signup")
async def signup(user_data: UserCreate):
    existing = await db.users.find_one({"email": user_data.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    user_doc = {
        "id": user_id,
        "email": user_data.email,
        "password": hash_password(user_data.password),
        "name": user_data.name,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(user_doc)
    token = create_token(user_id, user_data.email)
    
    return {"token": token, "user": {"id": user_id, "email": user_data.email, "name": user_data.name}}

@api_router.post("/auth/login")
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user or not verify_password(credentials.password, user['password']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user['id'], user['email'])
    return {"token": token, "user": {"id": user['id'], "email": user['email'], "name": user['name']}}

@api_router.post("/quiz/submit")
async def submit_quiz(quiz: QuizSubmission, user: dict = Depends(get_current_user)):
    eligible_schemes = []
    fallback_schemes = []
    
    for scheme in HARDCODED_SCHEMES:
        if check_eligibility(quiz, scheme):
            scheme_copy = scheme.copy()
            del scheme_copy['eligibility']
            scheme_copy['eligibility_match'] = 'Eligible'
            eligible_schemes.append(scheme_copy)
    
    if len(eligible_schemes) < 3:
        for scheme in HARDCODED_SCHEMES:
            if scheme['id'] not in [s['id'] for s in eligible_schemes]:
                scheme_copy = scheme.copy()
                del scheme_copy['eligibility']
                scheme_copy['eligibility_match'] = 'May be eligible - Check details'
                fallback_schemes.append(scheme_copy)
                if len(fallback_schemes) >= 3:
                    break
    
    quiz_doc = quiz.model_dump()
    quiz_doc['user_id'] = user['user_id']
    quiz_doc['submitted_at'] = datetime.now(timezone.utc).isoformat()
    await db.quiz_submissions.insert_one(quiz_doc)
    
    return {"eligible_schemes": eligible_schemes, "fallback_schemes": fallback_schemes}

@api_router.post("/schemes/save/{scheme_id}")
async def save_scheme(scheme_id: str, user: dict = Depends(get_current_user)):
    existing = await db.saved_schemes.find_one({
        "user_id": user['user_id'],
        "scheme_id": scheme_id
    }, {"_id": 0})
    
    if existing:
        return {"message": "Already saved"}
    
    saved_doc = {
        "user_id": user['user_id'],
        "scheme_id": scheme_id,
        "saved_at": datetime.now(timezone.utc).isoformat()
    }
    await db.saved_schemes.insert_one(saved_doc)
    return {"message": "Scheme saved successfully"}

@api_router.get("/schemes/saved")
async def get_saved_schemes(user: dict = Depends(get_current_user)):
    saved = await db.saved_schemes.find({"user_id": user['user_id']}, {"_id": 0}).to_list(100)
    saved_ids = [s['scheme_id'] for s in saved]
    
    schemes = [s for s in HARDCODED_SCHEMES if s['id'] in saved_ids]
    result = []
    for scheme in schemes:
        scheme_copy = scheme.copy()
        if 'eligibility' in scheme_copy:
            del scheme_copy['eligibility']
        result.append(scheme_copy)
    
    return {"schemes": result}

@api_router.delete("/schemes/unsave/{scheme_id}")
async def unsave_scheme(scheme_id: str, user: dict = Depends(get_current_user)):
    await db.saved_schemes.delete_one({
        "user_id": user['user_id'],
        "scheme_id": scheme_id
    })
    return {"message": "Scheme removed from saved"}

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port)