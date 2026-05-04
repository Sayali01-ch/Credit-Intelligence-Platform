# services/decision_engine.py
import time
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class DecisionEngine:
    def __init__(self, credit_model, llm_analyzer):
        self.credit_model = credit_model
        self.llm_analyzer = llm_analyzer
        
        # Decision weights
        self.ml_weight = 0.70
        self.llm_weight = 0.30
    
    def make_decision(self, application_data: Dict, document_insights: Dict = None) -> Dict[str, Any]:
        """Make credit decision"""
        
        start_time = time.time()
        
        # Step 1: Prepare features
        features = self._prepare_features(application_data, document_insights)
        
        # Step 2: Get ML score
        ml_result = self.credit_model.predict(features)
        
        # Step 3: Get LLM analysis if documents provided
        llm_result = None
        if document_insights:
            llm_result = self.llm_analyzer.analyze_creditworthiness(application_data, document_insights)
        
        # Step 4: Combine scores
        final_decision = self._combine_decisions(ml_result, llm_result)
        
        # Step 5: Generate explanation
        explanation = self.llm_analyzer.generate_explanation(
            final_decision['credit_score'],
            final_decision['risk_category'],
            final_decision.get('explanation', {}).get('top_factors', []),
            document_insights
        )
        
        final_decision['explanation_text'] = explanation
        final_decision['processing_time_ms'] = int((time.time() - start_time) * 1000)
        
        logger.info(f"Decision made in {final_decision['processing_time_ms']}ms")
        
        return final_decision
    
    def _prepare_features(self, application_data: Dict, document_insights: Dict = None) -> Dict:
        """Prepare feature vector for ML model"""
        
        # Extract base features
        features = {
            'age': int(application_data.get('age', 30)),
            'annual_income': float(application_data.get('annual_income', 50000)),
            'debt_to_income_ratio': float(application_data.get('debt_to_income_ratio', 0.3)),
            'credit_history_length': float(application_data.get('credit_history_length', 5)),
            'num_credit_cards': int(application_data.get('num_credit_cards', 2)),
            'total_debt': float(application_data.get('total_debt', 15000)),
            'employment_years': float(application_data.get('employment_years', 3)),
            'education_score': int(application_data.get('education_score', 3)),
            'home_ownership_score': int(application_data.get('home_ownership_score', 2)),
            'loan_amount': float(application_data.get('loan_amount', 25000)),
            'loan_purpose_score': int(application_data.get('loan_purpose_score', 3)),
            'payment_history': float(application_data.get('payment_history', 0.8)),
            'credit_utilization': float(application_data.get('credit_utilization', 0.3)),
            'num_defaults': int(application_data.get('num_defaults', 0)),
            'num_late_payments': int(application_data.get('num_late_payments', 0)),
            'income_stability': int(application_data.get('income_stability', 3)),
            'savings_balance': float(application_data.get('savings_balance', 10000)),
            'monthly_expenses': float(application_data.get('monthly_expenses', 3000)),
            'dependents': int(application_data.get('dependents', 0)),
            'marital_status_score': int(application_data.get('marital_status_score', 2))
        }
        
        # Enhance with document insights if available
        if document_insights and document_insights.get('extracted_data'):
            extracted = document_insights['extracted_data']
            if 'income' in extracted:
                features['annual_income'] = max(features['annual_income'], extracted['income'])
            if 'bank_balance' in extracted:
                features['savings_balance'] = max(features['savings_balance'], extracted['bank_balance'])
        
        return features
    
    def _combine_decisions(self, ml_result: Dict, llm_result: Dict = None) -> Dict:
        """Combine ML and LLM decisions"""
        
        if llm_result:
            # Adjust score based on LLM qualitative assessment
            llm_sentiment = self._extract_sentiment(llm_result.get('qualitative_assessment', ''))
            adjusted_score = ml_result['credit_score'] * (1 + llm_sentiment * 0.1)
            ml_result['credit_score'] = min(1000, max(0, int(adjusted_score)))
            
            # Update risk category
            if ml_result['credit_score'] >= 750:
                ml_result['risk_category'] = "Low Risk"
            elif ml_result['credit_score'] >= 650:
                ml_result['risk_category'] = "Medium Risk"
            elif ml_result['credit_score'] >= 500:
                ml_result['risk_category'] = "High Risk"
            else:
                ml_result['risk_category'] = "Very High Risk"
        
        ml_result['final_decision'] = ml_result['recommendation']
        
        return ml_result
    
    def _extract_sentiment(self, assessment: str) -> float:
        """Extract sentiment from LLM assessment (-1 to 1)"""
        positive_words = ['good', 'strong', 'stable', 'low risk', 'acceptable']
        negative_words = ['high risk', 'concern', 'issue', 'red flag', 'problem']
        
        assessment_lower = assessment.lower()
        
        positive_score = sum(1 for word in positive_words if word in assessment_lower)
        negative_score = sum(1 for word in negative_words if word in assessment_lower)
        
        total = positive_score + negative_score
        if total == 0:
            return 0
        
        return (positive_score - negative_score) / total