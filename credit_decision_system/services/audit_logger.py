# services/audit_logger.py
import json
import sqlite3
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class AuditLogger:
    def __init__(self, db_path='credit_audit.db'):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database for audit logging"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                application_data TEXT,
                decision TEXT,
                compliance_result TEXT,
                processing_time_ms INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL,
                timestamp TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_decision(self, app_id: str, application_data: Dict, 
                     decision: Dict, compliance_result: Dict):
        """Log credit decision for audit"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO audit_log 
            (application_id, timestamp, application_data, decision, compliance_result, processing_time_ms)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            app_id,
            datetime.now().isoformat(),
            json.dumps(application_data),
            json.dumps(decision),
            json.dumps(compliance_result),
            decision.get('processing_time_ms', 0)
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Audit log created for application {app_id}")
    
    def get_decision(self, app_id: str) -> Optional[Dict]:
        """Retrieve decision by application ID"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT application_id, timestamp, decision, compliance_result, processing_time_ms
            FROM audit_log
            WHERE application_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (app_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'application_id': row[0],
                'timestamp': row[1],
                'decision': json.loads(row[2]),
                'compliance': json.loads(row[3]),
                'processing_time_ms': row[4]
            }
        
        return None
    
    def get_total_count(self) -> int:
        """Get total number of applications"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM audit_log')
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
    
    def get_approval_rate(self) -> float:
        """Calculate approval rate"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(CASE WHEN json_extract(decision, '$.recommendation') = 'approve' THEN 1 END) * 1.0 / COUNT(*)
            FROM audit_log
        ''')
        
        rate = cursor.fetchone()[0] or 0
        conn.close()
        
        return rate
    
    def get_avg_processing_time(self) -> float:
        """Calculate average processing time"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT AVG(processing_time_ms) FROM audit_log')
        avg_time = cursor.fetchone()[0] or 0
        conn.close()
        
        return avg_time