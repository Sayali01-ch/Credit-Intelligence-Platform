import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from typing import Dict, List

class FeatureEngineer:
    """Feature engineering utilities for credit decision system"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.minmax_scaler = MinMaxScaler()
    
    def create_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create interaction features"""
        df['income_to_debt_ratio'] = df['annual_income'] / (df['total_debt'] + 1)
        df['loan_to_income_ratio'] = df['loan_amount'] / df['annual_income']
        df['credit_age_income_ratio'] = df['credit_history_length'] * df['annual_income'] / 100000
        
        return df
    
    def normalize_features(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Normalize specified columns"""
        df_normalized = df.copy()
        df_normalized[columns] = self.scaler.fit_transform(df[columns])
        
        return df_normalized
    
    def create_risk_segments(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create risk segments based on features"""
        df['risk_segment'] = pd.cut(
            df['debt_to_income_ratio'],
            bins=[0, 0.2, 0.35, 0.5, 1.0],
            labels=['Low', 'Medium', 'High', 'Very High']
        )
        
        return df
    
    def extract_features(self, application_data: Dict) -> Dict:
        """Extract and engineer features from application data"""
        
        features = dict(application_data)
        
        # Create derived features
        if 'annual_income' in features and 'total_debt' in features:
            features['income_to_debt_ratio'] = float(features['annual_income']) / (float(features['total_debt']) + 1)
        
        if 'annual_income' in features and 'loan_amount' in features:
            features['loan_to_income_ratio'] = float(features['loan_amount']) / float(features['annual_income'])
        
        if 'credit_history_length' in features and 'age' in features:
            features['credit_to_age_ratio'] = float(features['credit_history_length']) / (float(features['age']) + 1)
        
        if 'payment_history' in features and 'num_late_payments' in features:
            features['payment_quality_score'] = float(features['payment_history']) * (1 - float(features['num_late_payments']) / 10)
        
        return features
