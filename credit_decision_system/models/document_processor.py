# models/document_processor.py
import pdfplumber
import pytesseract
from PIL import Image
import re
import logging
from typing import List, Dict, Any
import io

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self.entity_patterns = {
            'income': r'(?:income|salary|wages?|earnings?)[:\s]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            'bank_balance': r'(?:balance|available balance|current balance)[:\s]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            'account_number': r'account\s*(?:#|number|no)[:\s]*(\d{4,16})',
            'employer': r'employer[:\s]*([A-Za-z\s]{2,50})',
            'payment': r'(?:payment|installment|emi)[:\s]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        }
    
    def process_documents(self, files: List) -> Dict[str, Any]:
        """Process uploaded documents"""
        insights = {
            'extracted_data': {},
            'confidence_scores': {},
            'document_count': len(files),
            'processed_at': None
        }
        
        for file in files:
            if file.filename.endswith('.pdf'):
                extracted = self._process_pdf(file)
            elif file.filename.endswith(('.png', '.jpg', '.jpeg')):
                extracted = self._process_image(file)
            else:
                continue
            
            # Merge extracted data
            for key, value in extracted.items():
                if key in insights['extracted_data']:
                    # Keep the most confident extraction
                    if extracted.get(f'{key}_confidence', 0) > insights['confidence_scores'].get(key, 0):
                        insights['extracted_data'][key] = value
                else:
                    insights['extracted_data'][key] = value
                    insights['confidence_scores'][key] = extracted.get(f'{key}_confidence', 0)
        
        return insights
    
    def _process_pdf(self, pdf_file) -> Dict[str, Any]:
        """Extract text from PDF"""
        extracted = {}
        
        try:
            with pdfplumber.open(pdf_file) as pdf:
                text = ''
                for page in pdf.pages:
                    text += page.extract_text() or ''
                
                extracted = self._extract_entities(text)
                
        except Exception as e:
            logger.error(f"PDF processing error: {str(e)}")
        
        return extracted
    
    def _process_image(self, image_file) -> Dict[str, Any]:
        """Extract text from image using OCR"""
        extracted = {}
        
        try:
            image = Image.open(image_file)
            text = pytesseract.image_to_string(image)
            extracted = self._extract_entities(text)
            
        except Exception as e:
            logger.error(f"Image processing error: {str(e)}")
        
        return extracted
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract financial entities from text"""
        extracted = {}
        
        for entity, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Clean the match (remove commas and convert to float)
                clean_value = re.sub(r'[^\d.]', '', matches[0])
                try:
                    extracted[entity] = float(clean_value) if '.' in clean_value else int(clean_value)
                    extracted[f'{entity}_confidence'] = 0.8  # Default confidence
                except ValueError:
                    extracted[entity] = matches[0]
                    extracted[f'{entity}_confidence'] = 0.6
        
        # Additional analysis
        extracted['document_summary'] = self._generate_summary(text)
        
        return extracted
    
    def _generate_summary(self, text: str) -> str:
        """Generate summary of document content"""
        # Truncate and clean text
        clean_text = ' '.join(text.split())[:500]
        
        # Basic sentiment/signal detection
        has_income = 'income' in text.lower()
        has_debt = 'debt' in text.lower() or 'loan' in text.lower()
        has_savings = 'savings' in text.lower() or 'balance' in text.lower()
        
        signals = []
        if has_income:
            signals.append("Income information present")
        if has_debt:
            signals.append("Debt information detected")
        if has_savings:
            signals.append("Savings/balance information present")
        
        summary = f"Document analysis: {', '.join(signals)}. Preview: {clean_text}"
        
        return summary