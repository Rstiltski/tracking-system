"""
PII Tokenizer - Phase 7.1: Tokenization System

Replaces Personally Identifiable Information (PII) with tokens before
sending data to external AI providers. This ensures customer names,
phone numbers, emails, and addresses never leave the system.

Token Format:
- Customer Name: CUST_A, CUST_B, CUST_C, ...
- Phone: PHONE_1, PHONE_2, PHONE_3, ...
- Email: EMAIL_1, EMAIL_2, EMAIL_3, ...
- Address: ADDR_1, ADDR_2, ADDR_3, ...
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- AI_NATIVE_ARCHITECTURE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""

import re
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime


class TokenType(Enum):
    """Types of PII that can be tokenized"""
    CUSTOMER_NAME = "CUST"
    PHONE = "PHONE"
    EMAIL = "EMAIL"
    ADDRESS = "ADDR"
    POSTCODE = "POST"


@dataclass
class Token:
    """Represents a tokenized piece of PII"""
    token_id: str  # e.g., "CUST_A"
    token_type: TokenType
    original_value: str
    context: Optional[str] = None  # Additional context (e.g., "customer_id:123")
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class PIITokenizer:
    """
    Tokenizes PII in data structures before AI interaction.
    
    Example:
        tokenizer = PIITokenizer()
        
        # Tokenize data
        data = {
            'customers': [
                {'name': 'John Smith', 'phone': '555-1234'},
                {'name': 'Jane Doe', 'phone': '555-5678'}
            ]
        }
        
        tokenized, tokens = tokenizer.tokenize(data)
        # tokenized = {
        #     'customers': [
        #         {'name': 'CUST_A', 'phone': 'PHONE_1'},
        #         {'name': 'CUST_B', 'phone': 'PHONE_2'}
        #     ]
        # }
        
        # Later, detokenize AI response
        ai_response = "I found CUST_A and contacted them at PHONE_1"
        original = tokenizer.detokenize(ai_response, tokens)
        # "I found John Smith and contacted them at 555-1234"
    """
    
    def __init__(self):
        self._token_counter = {
            TokenType.CUSTOMER_NAME: 0,
            TokenType.PHONE: 0,
            TokenType.EMAIL: 0,
            TokenType.ADDRESS: 0,
            TokenType.POSTCODE: 0
        }
        self._letter_index = 0  # For customer names (A, B, C, ...)
        
        # Patterns for PII detection
        # Phone: at least 7 digits/spaces/dashes/parens, but NOT dates (YYYY-MM-DD format)
        self._phone_pattern = re.compile(r'(?<!\d)[\d\s\-\(\)]{7,}(?!\-\d{2}\b)')  # Phone numbers
        self._email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self._postcode_pattern = re.compile(r'[A-Z]{1,2}[0-9]{1,2}[A-Z]?\s?[0-9][A-Z]{2}', re.IGNORECASE)
    
    def tokenize(self, data: Any, preserve_structure: bool = True) -> Tuple[Any, List[Token]]:
        """
        Tokenize PII in a data structure.
        
        Args:
            data: Data to tokenize (dict, list, str, or primitive)
            preserve_structure: If True, maintains dict/list structure
            
        Returns:
            Tuple of (tokenized_data, list_of_tokens)
        """
        tokens = []
        
        if isinstance(data, dict):
            return self._tokenize_dict(data, tokens), tokens
        elif isinstance(data, list):
            return self._tokenize_list(data, tokens), tokens
        elif isinstance(data, str):
            return self._tokenize_string(data, tokens), tokens
        else:
            # Primitive type (int, float, bool, None)
            return data, tokens
    
    def _tokenize_dict(self, data: Dict, tokens: List[Token]) -> Dict:
        """Tokenize all PII in a dictionary"""
        result = {}
        
        for key, value in data.items():
            # Check if this is a known PII field
            if self._is_pii_field(key):
                if isinstance(value, str) and value:
                    token_type = self._get_token_type_for_field(key)
                    token = self._create_token(value, token_type, f"{key}:{value}")
                    tokens.append(token)
                    result[key] = token.token_id
                else:
                    result[key] = value
            elif isinstance(value, (dict, list, str)):
                # Recursively tokenize nested structures
                tokenized_value, nested_tokens = self.tokenize(value, preserve_structure=True)
                tokens.extend(nested_tokens)
                result[key] = tokenized_value
            else:
                result[key] = value
        
        return result
    
    def _tokenize_list(self, data: List, tokens: List[Token]) -> List:
        """Tokenize all PII in a list"""
        result = []
        
        for item in data:
            if isinstance(item, (dict, list, str)):
                tokenized_item, nested_tokens = self.tokenize(item, preserve_structure=True)
                tokens.extend(nested_tokens)
                result.append(tokenized_item)
            else:
                result.append(item)
        
        return result
    
    def _tokenize_string(self, text: str, tokens: List[Token]) -> str:
        """
        Tokenize PII found in free-form text.
        
        This is more aggressive and uses pattern matching to find:
        - Phone numbers
        - Email addresses
        - Postcodes
        
        Note: Customer names are NOT auto-detected in free text (too risky)
        """
        result = text
        
        # Tokenize emails first (most specific pattern)
        for match in self._email_pattern.finditer(text):
            email = match.group(0)
            token = self._create_token(email, TokenType.EMAIL)
            tokens.append(token)
            result = result.replace(email, token.token_id)
        
        # Tokenize postcodes (before phone numbers to avoid conflicts)
        for match in self._postcode_pattern.finditer(result):
            postcode = match.group(0)
            # Skip if it's a token we already created
            if not postcode.startswith(('CUST_', 'PHONE_', 'EMAIL_', 'ADDR_', 'POST_')):
                token = self._create_token(postcode, TokenType.POSTCODE)
                tokens.append(token)
                result = result.replace(postcode, token.token_id)
        
        # Tokenize phone numbers (last, as pattern is less specific)
        for match in self._phone_pattern.finditer(result):
            phone = match.group(0)
            # Skip if it's a token we already created or contains only spaces/dashes
            if (not phone.startswith(('CUST_', 'PHONE_', 'EMAIL_', 'ADDR_', 'POST_')) 
                and phone.strip().replace('-', '').replace(' ', '').replace('(', '').replace(')', '')):
                token = self._create_token(phone, TokenType.PHONE)
                tokens.append(token)
                result = result.replace(phone, token.token_id)
        
        return result
    
    def _is_pii_field(self, field_name: str) -> bool:
        """Check if a field name indicates PII"""
        pii_fields = {
            'name', 'customer_name', 'user_name', 'full_name', 'first_name', 'last_name',
            'phone', 'phone_number', 'mobile', 'tel', 'telephone',
            'email', 'email_address',
            'address', 'street', 'address_line1', 'address_line2',
            'postcode', 'postal_code', 'zip', 'zip_code'
        }
        return field_name.lower() in pii_fields
    
    def _get_token_type_for_field(self, field_name: str) -> TokenType:
        """Determine token type from field name"""
        field_lower = field_name.lower()
        
        if 'name' in field_lower:
            return TokenType.CUSTOMER_NAME
        elif 'phone' in field_lower or 'mobile' in field_lower or 'tel' in field_lower:
            return TokenType.PHONE
        elif 'email' in field_lower:
            return TokenType.EMAIL
        elif 'address' in field_lower or 'street' in field_lower:
            return TokenType.ADDRESS
        elif 'post' in field_lower or 'zip' in field_lower:
            return TokenType.POSTCODE
        else:
            return TokenType.CUSTOMER_NAME  # Default
    
    def _create_token(self, value: str, token_type: TokenType, context: Optional[str] = None) -> Token:
        """Create a new token for a PII value"""
        # Generate token ID
        if token_type == TokenType.CUSTOMER_NAME:
            # Use letters for customer names (A, B, C, ..., Z, AA, AB, ...)
            token_id = f"CUST_{self._index_to_letter(self._letter_index)}"
            self._letter_index += 1
        else:
            # Use numbers for other types
            self._token_counter[token_type] += 1
            token_id = f"{token_type.value}_{self._token_counter[token_type]}"
        
        return Token(
            token_id=token_id,
            token_type=token_type,
            original_value=value,
            context=context
        )
    
    def _index_to_letter(self, index: int) -> str:
        """Convert index to letter sequence (0->A, 1->B, ..., 26->AA, ...)"""
        result = ""
        while True:
            result = chr(65 + (index % 26)) + result
            index = index // 26
            if index == 0:
                break
            index -= 1
        return result
    
    def detokenize(self, text: str, tokens: List[Token]) -> str:
        """
        Replace tokens in text with original PII values.
        
        Args:
            text: Text containing tokens (e.g., AI response)
            tokens: List of tokens to replace
            
        Returns:
            Text with original PII restored
        """
        result = text
        
        # Sort tokens by token_id length (longest first) to avoid partial matches
        sorted_tokens = sorted(tokens, key=lambda t: len(t.token_id), reverse=True)
        
        for token in sorted_tokens:
            result = result.replace(token.token_id, token.original_value)
        
        return result
    
    def detokenize_dict(self, data: Dict, tokens: List[Token]) -> Dict:
        """
        Replace tokens in a dictionary with original PII values.
        
        Args:
            data: Dictionary containing tokens
            tokens: List of tokens to replace
            
        Returns:
            Dictionary with original PII restored
        """
        # Create token lookup map
        token_map = {token.token_id: token.original_value for token in tokens}
        
        result = {}
        for key, value in data.items():
            if isinstance(value, str) and value in token_map:
                result[key] = token_map[value]
            elif isinstance(value, dict):
                result[key] = self.detokenize_dict(value, tokens)
            elif isinstance(value, list):
                result[key] = [
                    self.detokenize_dict(item, tokens) if isinstance(item, dict)
                    else token_map.get(item, item) if isinstance(item, str)
                    else item
                    for item in value
                ]
            else:
                result[key] = value
        
        return result
    
    def reset(self):
        """Reset token counters (useful for testing)"""
        self._token_counter = {
            TokenType.CUSTOMER_NAME: 0,
            TokenType.PHONE: 0,
            TokenType.EMAIL: 0,
            TokenType.ADDRESS: 0,
            TokenType.POSTCODE: 0
        }
        self._letter_index = 0
