import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import shutil
import glob
import base64
import traceback
import io

class ChatHistoryManager:
    def __init__(self, model, history_dir: str = "chat-history"):
        """Initialize the chat history manager with the specified directory"""
        self.model = model
        self.history_dir = os.path.join(history_dir, model)
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Ensure the chat history directory exists"""
        os.makedirs(self.history_dir, exist_ok=True)

    def _get_chat_filepath(self, chat_id: str, session_id: str) -> str:
        """Get the full file path for a chat JSON file"""
        return os.path.join(self.history_dir, session_id, f"{chat_id}.json")
    
    def save_chat(self, chat_to_save: Dict, session_id: str) -> None:
        """Save a chat to both memory and file, handling images separately"""
        chat_dir = os.path.join(self.history_dir,session_id)
        os.makedirs(chat_dir, exist_ok=True)
        
        # Save chat data
        filepath = self._get_chat_filepath(chat_to_save["chat_id"], session_id)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(chat_to_save, f, indent=2, ensure_ascii=False)    
        except Exception as e:
            print(f"Error saving chat {chat_to_save['chat_id']}: {str(e)}")
            traceback.print_exc()
            raise e

    def get_chat(self, chat_id: str, session_id: str) -> Optional[Dict]:
        """Get a specific chat by ID"""
        filepath = os.path.join(self.history_dir,session_id,f"{chat_id}.json")
        chat_data = {}
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                chat_data = json.load(f)        
        except Exception as e:
            print(f"Error loading chat history from {filepath}: {str(e)}")
            traceback.print_exc()
        return chat_data
    
    def get_recent_chats(self, session_id: str, limit: Optional[int] = None) -> List[Dict]:
        """Get recent chats, optionally limited to a specific number"""        
        chat_dir = os.path.join(self.history_dir,session_id)
        os.makedirs(chat_dir, exist_ok=True)
        recent_chats = []
        chat_files = glob.glob(os.path.join(chat_dir,"*.json"))
        for filepath in chat_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    chat_data = json.load(f)        
                    recent_chats.append(chat_data)
            except Exception as e:
                print(f"Error loading chat history from {filepath}: {str(e)}")
                traceback.print_exc()

        # Sort by dts
        recent_chats.sort(key=lambda x: x.get('dts', 0), reverse=True)
        if limit:
            return recent_chats[:limit]
            
        return recent_chats