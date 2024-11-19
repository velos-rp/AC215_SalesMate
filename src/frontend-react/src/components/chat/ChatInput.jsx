'use client';

import { useState, useRef, useEffect } from 'react';
import { Send } from '@mui/icons-material';

// Styles
import styles from './ChatInput.module.css';

export default function ChatInput({
    onSendMessage,
    placeholder,
}) {
    // Component States
    const [message, setMessage] = useState('');
    const textAreaRef = useRef(null);
    const fileInputRef = useRef(null);

    const adjustTextAreaHeight = () => {
        const textarea = textAreaRef.current;
        if (textarea) {
            textarea.style.height = 'auto';
            textarea.style.height = `${textarea.scrollHeight}px`;
        }
    };

    // Setup Component
    useEffect(() => {
        adjustTextAreaHeight();
    }, [message]);

    // Handlers
    const handleSubmit = () => {
        if (message.trim()) {
            console.log('Submitting message:', message);
            const newMessage = {
                content: message.trim(),
                image: null
            };

            // Send the message
            onSendMessage(newMessage);

            // Reset
            setMessage('');
            if (textAreaRef.current) {
                textAreaRef.current.style.height = 'auto';
            }
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }
        }
    };

    return (
        <div className={styles.chatInputContainer}>
            <div className={styles.textareaWrapper}>
                <textarea
                    ref={textAreaRef}
                    className={styles.chatInput}
                    placeholder={placeholder}
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            handleSubmit();
                        }
                    }}
                    rows={1}
                />
                <button
                    className={`${styles.submitButton} ${message.trim() ? styles.active : ''}`}
                    onClick={handleSubmit}
                    disabled={!message.trim()}
                >
                    <Send />
                </button>
            </div>
        </div>
    )
}