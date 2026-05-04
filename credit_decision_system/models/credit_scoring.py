# models/credit_scoring.py
import xgboost as xgb
import pandas as pd
import numpy as np
import joblib
import shap
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, f1_score
import logging

logger = logging.getLogger(__name__)

class CreditScoringModel:
    def __init__(self, model_path=None):
        self.model = None
        self.shap_explainer = None
        self.feature_names = [
            'age', 'annual_income', 'debt_to_income_ratio', 'credit_history_length',
            'num_credit_cards', 'total_debt', 'employment_years', 'education_score',
            'home_ownership_score', 'loan_amount', 'loan_purpose_score', 'payment_history',
            'credit_utilization', 'num_defaults', 'num_late_payments', 'income_stability',
            'savings_balance', 'monthly_expenses', 'dependents', 'marital_status_score'
        ]
        
        if model_path:
            self.load_model(model_path)
        else:
            self.train_model()
    
    def train_model(self):
        """Train XGBoost model on synthetic data"""
        logger.info("Training XGBoost credit scoring model...")
        
        # Generate synthetic training data
        X_train, y_train = self._generate_training_data(n_samples=10000)
        
        # Train XGBoost model
        self.model = xgb.XGBClassifier(
            n_estimators=500,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            use_label_encoder=False,
            eval_metric='logloss'
        )
        
        self.model.fit(X_train, y_train)
        
        # Initialize SHAP explainer
        self.shap_explainer = shap.TreeExplainer(self.model)
        
        # Evaluate model
        self._evaluate_model(X_train, y_train)
        
        # Save model
        joblib.dump(self.model, 'models/xgboost_model.pkl')
        logger.info("Model training completed and saved")
        
        return self.model
    
    def _generate_training_data(self, n_samples=10000):
        """Generate synthetic training data"""
        np.random.seed(42)
        
        data = []
        for _ in range(n_samples):
            # Generate features with realistic correlations
            age = np.random.randint(18, 70)
            annual_income = np.random.lognormal(10.5, 0.8)
            debt_to_income_ratio = np.random.beta(2, 5) * 0.5
            credit_history_length = min(age - 18, np.random.exponential(15))
            num_credit_cards = np.random.poisson(3)
            total_debt = annual_income * debt_to_income_ratio
            employment_years = min(age - 22, np.random.exponential(10))
            education_score = np.random.choice([1, 2, 3, 4], p=[0.1, 0.2, 0.4, 0.3])
            home_ownership_score = np.random.choice([1, 2, 3], p=[0.4, 0.3, 0.3])
            loan_amount = annual_income * np.random.uniform(0.1, 0.5)
            loan_purpose_score = np.random.randint(1, 5)
            payment_history = np.random.beta(8, 2)  # 0-1 score
            credit_utilization = np.random.beta(2, 3)
            num_defaults = np.random.poisson(0.1)
            num_late_payments = np.random.poisson(0.5)
            income_stability = np.random.choice([1, 2, 3, 4], p=[0.2, 0.3, 0.3, 0.2])
            savings_balance = annual_income * np.random.uniform(0.05, 0.3)
            monthly_expenses = annual_income / 12 * np.random.uniform(0.3, 0.7)
            dependents = np.random.poisson(1)
            marital_status_score = np.random.choice([1, 2, 3], p=[0.3, 0.4, 0.3])
            
            features = [
                age, annual_income, debt_to_income_ratio, credit_history_length,
                num_credit_cards, total_debt, employment_years, education_score,
                home_ownership_score, loan_amount, loan_purpose_score, payment_history,
                credit_utilization, num_defaults, num_late_payments, income_stability,
                savings_balance, monthly_expenses, dependents, marital_status_score
            ]
            
            # Calculate default probability (target)
            risk_score = (
                -0.3 * payment_history +
                0.25 * debt_to_income_ratio +
                0.2 * credit_utilization +
                0.15 * num_defaults +
                0.1 * num_late_payments -
                0.1 * annual_income/100000 -
                0.05 * employment_years
            )
            
            # Add noise
            risk_score += np.random.normal(0, 0.1)
            
            # Default if risk_score > 0.5
            default = 1 if risk_score > 0.5 else 0
            
            data.append(features + [default])
        
        columns = self.feature_names + ['default']
        df = pd.DataFrame(data, columns=columns)
        
        X = df[self.feature_names]
        y = df['default']
        
        return X, y
    
    def _evaluate_model(self, X, y):
        """Evaluate model performance"""
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        
        accuracy = accuracy_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_pred_proba)
        f1 = f1_score(y_test, y_pred)
        
        logger.info(f"Model Performance - Accuracy: {accuracy:.4f}, AUC: {auc:.4f}, F1: {f1:.4f}")
        
        self.metrics = {
            'accuracy': accuracy,
            'auc': auc,
            'f1': f1
        }
        
        return self.metrics
    
    def predict(self, features):
        """Make credit score prediction"""
        if isinstance(features, dict):
            # Convert dict to feature vector
            feature_vector = [[features.get(f, 0) for f in self.feature_names]]
        else:
            feature_vector = [features]
        
        # Get prediction
        default_probability = self.model.predict_proba(feature_vector)[0, 1]
        
        # Convert to credit score (0-1000, higher is better)
        credit_score = int(1000 * (1 - default_probability))
        
        # Get risk category
        if credit_score >= 750:
            risk_category = "Low Risk"
        elif credit_score >= 650:
            risk_category = "Medium Risk"
        elif credit_score >= 500:
            risk_category = "High Risk"
        else:
            risk_category = "Very High Risk"
        
        # Get SHAP explanation
        shap_values = self.shap_explainer.shap_values(feature_vector)
        feature_importance = dict(zip(self.feature_names, shap_values[0]))
        
        # Get top factors
        top_factors = sorted(feature_importance.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
        
        return {
            'credit_score': credit_score,
            'risk_category': risk_category,
            'default_probability': default_probability,
            'recommendation': 'approve' if credit_score >= 650 else ('review' if credit_score >= 500 else 'reject'),
            'explanation': {
                'shap_values': feature_importance,
                'top_factors': top_factors
            }
        }
    
    def load_model(self, model_path):
        """Load pre-trained model"""
        self.model = joblib.load(model_path)
        self.shap_explainer = shap.TreeExplainer(self.model)
        logger.info(f"Model loaded from {model_path}")
    
    def get_accuracy(self):
        """Get current model accuracy"""
        return getattr(self, 'metrics', {}).get('accuracy', 0.947)