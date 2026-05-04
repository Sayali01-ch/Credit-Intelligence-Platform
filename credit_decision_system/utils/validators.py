# utils/validators.py
import re
from typing import Tuple, List, Dict

def validate_application(application_data: Dict) -> Tuple[bool, List[str]]:
    """Validate application form data"""
    errors = []
    
    # Required fields
    required_fields = [
        'age', 'annual_income', 'employment_years', 'loan_amount',
        'debt_to_income_ratio', 'credit_history_length'
    ]
    
    for field in required_fields:
        if field not in application_data or not application_data[field]:
            errors.append(f"Missing required field: {field}")
    
    # Age validation
    if 'age' in application_data:
        try:
            age = int(application_data['age'])
            if age < 18 or age > 100:
                errors.append("Age must be between 18 and 100")
        except ValueError:
            errors.append("Age must be a valid number")
    
    # Income validation
    if 'annual_income' in application_data:
        try:
            income = float(application_data['annual_income'])
            if income < 0:
                errors.append("Annual income cannot be negative")
        except ValueError:
            errors.append("Annual income must be a valid number")
    
    # DTI validation
    if 'debt_to_income_ratio' in application_data:
        try:
            dti = float(application_data['debt_to_income_ratio'])
            if dti < 0 or dti > 1.0:
                errors.append("Debt-to-income ratio must be between 0 and 1")
        except ValueError:
            errors.append("Debt-to-income ratio must be a valid number")
    
    # Loan amount validation
    if 'loan_amount' in application_data:
        try:
            loan = float(application_data['loan_amount'])
            if loan <= 0:
                errors.append("Loan amount must be positive")
        except ValueError:
            errors.append("Loan amount must be a valid number")
    
    return len(errors) == 0, errors