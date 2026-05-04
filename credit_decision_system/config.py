# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///credit_system.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis for caching
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # LLM API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    
    # Model paths
    MODEL_PATH = os.getenv('MODEL_PATH', 'models/xgboost_model.pkl')
    
    # Application limits
    MAX_DOCUMENT_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
    
    # Decision thresholds
    APPROVAL_THRESHOLD = 650
    REJECTION_THRESHOLD = 500
    
    # Compliance
    ECOA_DISPARATE_IMPACT_THRESHOLD = 0.8
    AUDIT_LOG_RETENTION_DAYS = 2555  # 7 years
    
    # Performance
    REQUEST_TIMEOUT = 1.2  # seconds
    MAX_CONCURRENT_REQUESTS = 100