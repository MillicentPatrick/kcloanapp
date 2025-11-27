import streamlit as st
import hashlib

class Authentication:
    def __init__(self):
        self.users = {
            'loan_officer': {
                'password': self._hash_password('officer123'),
                'role': 'Loan Officer',
                'branch': 'Nairobi Main'
            },
            'branch_manager': {
                'password': self._hash_password('manager123'),
                'role': 'Branch Manager', 
                'branch': 'Nairobi Main'
            },
            'risk_manager': {
                'password': self._hash_password('risk123'),
                'role': 'Risk Manager',
                'branch': 'Head Office'
            },
            'admin': {
                'password': self._hash_password('admin123'),
                'role': 'Admin',
                'branch': 'Head Office'
            }
        }
    
    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username, password):
        if username in self.users:
            hashed_password = self._hash_password(password)
            if self.users[username]['password'] == hashed_password:
                return True, self.users[username]
        return False, None
    
    def check_permission(self, user_role, required_role):
        role_hierarchy = {
            'Loan Officer': 1,
            'Branch Manager': 2,
            'Risk Manager': 3,
            'Admin': 4
        }
        
        return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)