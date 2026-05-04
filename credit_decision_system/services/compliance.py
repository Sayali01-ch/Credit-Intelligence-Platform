# services/compliance.py
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class ComplianceChecker:
    def __init__(self):
        self.disparate_impact_threshold = 0.8
        
    def check_decision(self, decision: Dict) -> Dict[str, Any]:
        """Check decision for regulatory compliance"""
        
        compliance_result = {
            'ecoa_compliant': True,
            'fcra_compliant': True,
            'gdpr_compliant': True,
            'violations': [],
            'warnings': []
        }
        
        # Check ECOA disparate impact
        disparate_impact = self._check_disparate_impact(decision)
        if not disparate_impact['compliant']:
            compliance_result['ecoa_compliant'] = False
            compliance_result['violations'].append({
                'regulation': 'ECOA',
                'issue': disparate_impact['issue'],
                'severity': 'high'
            })
        
        # Check FCRA adverse action notice requirements
        fcra_check = self._check_fcra_requirements(decision)
        if not fcra_check['compliant']:
            compliance_result['fcra_compliant'] = False
            compliance_result['violations'].append({
                'regulation': 'FCRA',
                'issue': fcra_check['issue'],
                'severity': 'medium'
            })
        
        # Check GDPR data handling
        gdpr_check = self._check_gdpr_compliance(decision)
        if not gdpr_check['compliant']:
            compliance_result['gdpr_compliant'] = False
            compliance_result['violations'].append({
                'regulation': 'GDPR',
                'issue': gdpr_check['issue'],
                'severity': 'high'
            })
        
        compliance_result['overall_compliant'] = (
            compliance_result['ecoa_compliant'] and
            compliance_result['fcra_compliant'] and
            compliance_result['gdpr_compliant']
        )
        
        compliance_result['checked_at'] = datetime.now().isoformat()
        
        return compliance_result
    
    def _check_disparate_impact(self, decision: Dict) -> Dict:
        """Check for disparate impact under ECOA"""
        # In production, this would analyze demographic distributions
        # For demo, return compliant by default
        return {'compliant': True, 'issue': None}
    
    def _check_fcra_requirements(self, decision: Dict) -> Dict:
        """Check FCRA adverse action notice requirements"""
        
        if decision.get('recommendation') == 'reject':
            if not decision.get('explanation_text'):
                return {
                    'compliant': False,
                    'issue': 'Adverse action notice required but no explanation provided'
                }
            
            if not decision.get('explanation', {}).get('top_factors'):
                return {
                    'compliant': False,
                    'issue': 'Key factors for adverse action not specified'
                }
        
        return {'compliant': True, 'issue': None}
    
    def _check_gdpr_compliance(self, decision: Dict) -> Dict:
        """Check GDPR compliance for data handling"""
        # In production, this would check data minimization, retention policies, etc.
        return {'compliant': True, 'issue': None}