# models/llm_analyzer.py
import openai
import anthropic
import json
import logging
from typing import Dict, Any
import os

logger = logging.getLogger(__name__)

class LLMAnalyzer:
    def __init__(self):
        # Initialize API clients
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY', ''))
        self.anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY', ''))
        
        # Use mock responses if no API keys
        self.use_mock = not (os.getenv('OPENAI_API_KEY') or os.getenv('ANTHROPIC_API_KEY'))
    
    def analyze_creditworthiness(self, application_data: Dict, document_insights: Dict = None) -> Dict[str, Any]:
        """Analyze creditworthiness using LLM"""
        
        if self.use_mock:
            return self._mock_analysis(application_data, document_insights)
        
        # Prepare prompt
        prompt = self._build_prompt(application_data, document_insights)
        
        try:
            # Try OpenAI first
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a credit risk analyst. Analyze the applicant's financial information and provide a credit assessment."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            analysis = response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            # Fallback to mock
            analysis = self._mock_analysis(application_data, document_insights)['qualitative_assessment']
        
        return {
            'qualitative_assessment': analysis,
            'confidence': 0.85,
            'model_used': 'gpt-3.5-turbo' if not self.use_mock else 'mock'
        }
    
    def generate_explanation(self, credit_score: int, risk_category: str, 
                             top_factors: list, document_insights: Dict = None) -> str:
        """Generate human-readable explanation for credit decision"""
        
        explanation_prompt = f"""
        Generate a clear, professional explanation for this credit decision:
        
        Credit Score: {credit_score}/1000
        Risk Category: {risk_category}
        Key Factors: {json.dumps(top_factors)}
        Document Insights: {json.dumps(document_insights) if document_insights else 'None'}
        
        Provide a concise explanation (3-4 sentences) that an applicant can understand.
        Include specific reasons for the decision and constructive advice if applicable.
        """
        
        if self.use_mock:
            return self._mock_explanation(credit_score, risk_category, top_factors)
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a credit analyst providing clear, fair explanations for loan decisions."},
                    {"role": "user", "content": explanation_prompt}
                ],
                temperature=0.5,
                max_tokens=250
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Explanation generation error: {str(e)}")
            return self._mock_explanation(credit_score, risk_category, top_factors)
    
    def _build_prompt(self, application_data: Dict, document_insights: Dict) -> str:
        """Build prompt for LLM analysis"""
        
        prompt = f"""
        Applicant Information:
        - Age: {application_data.get('age', 'Not provided')}
        - Annual Income: ${application_data.get('annual_income', 'Not provided')}
        - Employment Years: {application_data.get('employment_years', 'Not provided')}
        - Loan Amount: ${application_data.get('loan_amount', 'Not provided')}
        - Debt-to-Income Ratio: {application_data.get('debt_to_income_ratio', 'Not provided')}
        - Credit History: {application_data.get('credit_history_length', 'Not provided')} years
        
        """
        
        if document_insights and document_insights.get('extracted_data'):
            prompt += f"""
            Document Extracted Information:
            {json.dumps(document_insights.get('extracted_data', {}), indent=2)}
            """
        
        prompt += """
        Based on this information, provide:
        1. Assessment of creditworthiness
        2. Key risk factors identified
        3. Recommendations for the loan decision
        4. Any red flags or concerns
        
        Be specific and professional.
        """
        
        return prompt
    
    def _mock_analysis(self, application_data: Dict, document_insights: Dict) -> Dict:
        """Generate mock analysis for testing"""
        
        income = float(application_data.get('annual_income', 50000))
        dti = float(application_data.get('debt_to_income_ratio', 0.3))
        loan_amount = float(application_data.get('loan_amount', 25000))
        
        if income < 30000 or dti > 0.4:
            assessment = "High risk applicant with low income or high debt burden."
        elif loan_amount > income * 0.5:
            assessment = "Moderate risk - loan amount is significant relative to income."
        else:
            assessment = "Acceptable risk - applicant appears financially stable."
        
        return {
            'qualitative_assessment': assessment,
            'confidence': 0.75,
            'model_used': 'mock'
        }
    
    def _mock_explanation(self, credit_score: int, risk_category: str, top_factors: list) -> str:
        """Generate mock explanation"""
        
        factors_text = ', '.join([f"{factor[0]}: {factor[1]:.2f}" for factor in top_factors[:3]])
        
        if credit_score >= 650:
            return f"Your application has been approved with a credit score of {credit_score}. The main factors contributing to this decision are {factors_text}. Based on your financial profile, you present {risk_category.lower()}."
        else:
            return f"Your application could not be approved at this time. Your credit score of {credit_score} indicates {risk_category.lower()}. The primary factors affecting this decision are {factors_text}. We recommend focusing on improving these areas before reapplying."