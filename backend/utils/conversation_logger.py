"""
Conversation Logger for WorldWeaver

This module provides comprehensive logging functionality for user conversations,
including chat interactions and tutorial sessions.
"""
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class ConversationLogger:
    """
    Handles logging of user conversations with detailed formatting and structure.
    """
    
    def __init__(self, log_dir: str = None):
        """Initialize the conversation logger.
        
        Args:
            log_dir: Directory to store log files. Defaults to backend/logs
        """
        if log_dir is None:
            # Get project root and create logs directory path
            project_root = Path(__file__).resolve().parents[2]
            log_dir = project_root / "backend" / "logs"
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.current_log_file = None
        self.session_start_time = None
        
    def start_new_conversation(self, username: str) -> str:
        """
        Start a new conversation log file.
        
        Args:
            username: The username of the current user
            
        Returns:
            The path to the created log file
        """
        print("creating logging file...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{username}_conversation.log"
        self.current_log_file = self.log_dir / filename
        self.session_start_time = datetime.now()
        
        # Create the log file with header
        with open(self.current_log_file, 'w', encoding='utf-8') as f:
            f.write(self._get_session_header(username))
        
        return str(self.current_log_file)
    
    def _get_session_header(self, username: str) -> str:
        """Generate the session header for log files."""
        header = f"""
{'='*80}
                        WORLDWEAVER CONVERSATION LOG
{'='*80}
User: {username}
Session Start: {self.session_start_time.strftime('%Y-%m-%d %H:%M:%S')}
Log File: {self.current_log_file.name}
{'='*80}

"""
        return header
    
    def _write_separator(self, title: str = "", char: str = "-", width: int = 80):
        """Write a formatted separator to the log file."""
        if not self.current_log_file:
            return
            
        with open(self.current_log_file, 'a', encoding='utf-8') as f:
            if title:
                f.write(f"\n{char * width}\n")
                f.write(f" {title.upper()} ".center(width, char))
                f.write(f"\n{char * width}\n")
            else:
                f.write(f"\n{char * width}\n")
    
    def _write_timestamp(self):
        """Write current timestamp to log file."""
        if not self.current_log_file:
            return
            
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.current_log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n[{timestamp}] ")
    
    def log_llm_request(self, user_message: str, chat_history: str,
                       document_context: str, frontend_stage: int):
        """
        Log an LLM request from the /llm route.
        
        Args:
            user_message: The user's input message
            chat_history: Full chat history context
            document_context: Current document content
            frontend_stage: Frontend reported stage
        """
        if not self.current_log_file:
            return
            
        self._write_separator("LLM REQUEST")
        self._write_timestamp()
        
        with open(self.current_log_file, 'a', encoding='utf-8') as f:
            f.write("LLM REQUEST RECEIVED\n")
            f.write(f"Stage: {frontend_stage}\n")

            f.write("USER MESSAGE:\n")
            f.write("-" * 40 + "\n")
            f.write(f"{user_message}\n")
            f.write("-" * 40 + "\n\n")
            
            if document_context:
                f.write("DOCUMENT CONTEXT:\n")
                f.write("-" * 40 + "\n")
                try:
                    # Try to pretty print if it's JSON
                    doc_data = json.loads(document_context) if isinstance(document_context, str) else document_context
                    f.write(json.dumps(doc_data, indent=2))
                except:
                    f.write(str(document_context))
                f.write("\n" + "-" * 40 + "\n\n")
            
            if chat_history:
                f.write("CHAT HISTORY:\n")
                f.write("-" * 40 + "\n")
                try:
                    # Try to pretty print if it's JSON
                    chat_data = json.loads(chat_history) if isinstance(chat_history, str) else chat_history
                    f.write(json.dumps(chat_data, indent=2))
                except:
                    f.write(str(chat_history))
                f.write("\n" + "-" * 40 + "\n\n")
    
    def log_llm_response(self, raw_output: str, processed_output: Dict[str, Any], 
                        processing_type: str = "success", metadata: Optional[Dict[str, Any]] = None):
        """
        Log an LLM response from the /llm route.
        
        Args:
            raw_output: Raw output from the LLM
            processed_output: Final processed JSON response
            processing_type: Type of processing ('success', 'json_parse', 'string_parse', 'error')
            metadata: Additional metadata (prompt_name, model, stage, etc.)
        """
        if not self.current_log_file:
            return
            
        self._write_separator("LLM RESPONSE")
        self._write_timestamp()
        
        with open(self.current_log_file, 'a', encoding='utf-8') as f:
            f.write(f"LLM RESPONSE PROCESSED ({processing_type.upper()})\n")
            
            # Add metadata section if provided
            if metadata:
                f.write(f"Model: {metadata.get('model', 'unknown')}\n")
                f.write(f"Prompt Name: {metadata.get('prompt_name', 'unknown')}\n")
                f.write(f"Stage: {metadata.get('stage', 'unknown')}\n")
                if 'stage_title' in metadata:
                    f.write(f"Stage Title: {metadata.get('stage_title')}\n")
            f.write("\n")
            
            f.write("RAW LLM OUTPUT:\n")
            f.write("=" * 50 + "\n")
            f.write(f"{raw_output}\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("PROCESSED JSON OUTPUT:\n")
            f.write("=" * 50 + "\n")
            f.write(json.dumps(processed_output, indent=2))
            f.write("\n" + "=" * 50 + "\n\n")
    
    def log_tutorial_request(self, stage: int, chat_context: str, document_context: str):
        """
        Log a tutorial request from the /tutorial route.
        
        Args:
            stage: Tutorial stage requested
            chat_context: Chat context provided
            document_context: Document context provided
        """
        if not self.current_log_file:
            return
            
        self._write_separator("TUTORIAL REQUEST")
        self._write_timestamp()
        
        with open(self.current_log_file, 'a', encoding='utf-8') as f:
            f.write("TUTORIAL REQUEST RECEIVED\n")
            f.write(f"Stage: {stage}\n\n")
            
            if chat_context:
                f.write("CHAT CONTEXT:\n")
                f.write("-" * 40 + "\n")
                try:
                    chat_data = json.loads(chat_context) if isinstance(chat_context, str) else chat_context
                    f.write(json.dumps(chat_data, indent=2))
                except:
                    f.write(str(chat_context))
                f.write("\n" + "-" * 40 + "\n\n")
            
            if document_context:
                f.write("DOCUMENT CONTEXT:\n")
                f.write("-" * 40 + "\n")
                try:
                    doc_data = json.loads(document_context) if isinstance(document_context, str) else document_context
                    f.write(json.dumps(doc_data, indent=2))
                except:
                    f.write(str(document_context))
                f.write("\n" + "-" * 40 + "\n\n")
    
    def log_tutorial_response(self, raw_output: str, processed_output: Dict[str, Any], 
                             metadata: Optional[Dict[str, Any]] = None):
        """
        Log a tutorial response from the /tutorial route.
        
        Args:
            raw_output: Raw output from the tutorial processor
            processed_output: Final JSON response
            metadata: Additional metadata (prompt_name, model, stage, etc.)
        """
        if not self.current_log_file:
            return
            
        self._write_separator("TUTORIAL RESPONSE")
        self._write_timestamp()
        
        with open(self.current_log_file, 'a', encoding='utf-8') as f:
            f.write("TUTORIAL RESPONSE GENERATED\n")
            
            # Add metadata section if provided
            if metadata:
                f.write(f"Model: {metadata.get('model', 'unknown')}\n")
                f.write(f"Prompt Name: {metadata.get('prompt_name', 'unknown')}\n")
                f.write(f"Stage: {metadata.get('stage', 'unknown')}\n")
                if 'stage_title' in metadata:
                    f.write(f"Stage Title: {metadata.get('stage_title')}\n")
            f.write("\n")
            
            f.write("RAW TUTORIAL OUTPUT:\n")
            f.write("=" * 50 + "\n")
            f.write(f"{raw_output}\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("PROCESSED JSON OUTPUT:\n")
            f.write("=" * 50 + "\n")
            f.write(json.dumps(processed_output, indent=2))
            f.write("\n" + "=" * 50 + "\n\n")
    
    def log_error(self, error_type: str, error_message: str, context: Optional[Dict[str, Any]] = None):
        """
        Log an error that occurred during processing.
        
        Args:
            error_type: Type of error (e.g., 'LLM_ERROR', 'TUTORIAL_ERROR', 'JSON_PARSE_ERROR')
            error_message: The error message
            context: Additional context about the error
        """
        if not self.current_log_file:
            return
            
        self._write_separator("ERROR", char="!")
        self._write_timestamp()
        
        with open(self.current_log_file, 'a', encoding='utf-8') as f:
            f.write(f"ERROR OCCURRED: {error_type}\n")
            f.write(f"Error Message: {error_message}\n\n")
            
            if context:
                f.write("ERROR CONTEXT:\n")
                f.write("-" * 40 + "\n")
                f.write(json.dumps(context, indent=2, default=str))
                f.write("\n" + "-" * 40 + "\n\n")
    
    def log_session_end(self):
        """Log the end of a conversation session."""
        if not self.current_log_file:
            return
            
        self._write_separator("SESSION END")
        
        with open(self.current_log_file, 'a', encoding='utf-8') as f:
            end_time = datetime.now()
            duration = end_time - self.session_start_time if self.session_start_time else None
            
            f.write(f"Session End: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            if duration:
                f.write(f"Session Duration: {duration}\n")
            f.write("\n" + "=" * 80 + "\n")
            f.write("END OF LOG")
            f.write("\n" + "=" * 80 + "\n")

    def log_message(self, message: str):
        if not self.current_log_file:
            return
        char = "*"
        width = 80
        with open(self.current_log_file, 'a', encoding='utf-8') as f:
            if message:
                f.write(f" \n{message.upper()} \n".center(width, char))
            else:
                f.write(f"\n{char * width}\n")


# Global logger instance
conversation_logger = ConversationLogger()