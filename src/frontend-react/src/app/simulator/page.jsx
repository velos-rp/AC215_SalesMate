'use client';

import { useState, use, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import ChatInput from '@/components/chat/ChatInput';
import { Markdown, TypingIndicator } from '@/components/chat/ChatContent';
import DataService from "../../services/DataService";
import { uuid } from "../../services/Common";

// Import the styles
import styles from "./styles.module.css";

export default function SimulatorPage({ searchParams }) {
    const params = use(searchParams);
    const chat_id = params.id;

    // Component States
    const [chatId, setChatId] = useState(params.id);
    const [chat, setChat] = useState(null);
    const [ragMessages, setRagMessages] = useState([]);
    const [refreshKey, setRefreshKey] = useState(0);
    const [chatIsTyping, setChatIsTyping] = useState(false);
    const [ragIsLoading, setRagIsLoading] = useState(false);
    const router = useRouter();

    const fetchChat = useCallback(async (id) => {
        try {
            setChat(null);
            const response = await DataService.GetChat(id);
            setChat(response.data);
        } catch (error) {
            console.error('Error fetching chat:', error);
            setChat(null);
        }
    }, [setChat]);

    // Setup Component
    useEffect(() => {
        if (chat_id) {
            fetchChat(chat_id);
        } else {
            setChat(null);
        }
    }, [chat_id, fetchChat]);

    function tempChatMessage(message) {
        // Set temp values
        message["message_id"] = uuid();
        message["role"] = 'user';
        if (chat) {
            // Append message
            var temp_chat = { ...chat };
            temp_chat["messages"].push(message);
        } else {
            var temp_chat = {
                "messages": [message]
            }
            return temp_chat;
        }
    }

    // Handlers
    const newChat = (message) => {
        console.log(message);
        // Start a new chat and submit to LLM
        const startChat = async (message) => {
            try {
                // Show typing indicator
                setChatIsTyping(true);
                setChat(tempChatMessage(message)); // Show the user input message while LLM is invoked

                // Submit chat
                const response = await DataService.StartChatWithLLM(message);
                console.log(response.data);

                // Hide typing indicator and add response
                setChatIsTyping(false);

                setChat(response.data);
                setChatId(response.data["chat_id"]);
                router.push('/simulator?id=' + response.data["chat_id"]);
            } catch (error) {
                console.error('Error fetching chat:', error);
                setChatIsTyping(false);
                setChat(null);
                setChatId(null);
                router.push('/simulator');
            }
        };
        startChat(message);

    };
    const appendChat = (message) => {
        console.log(message);
        // Append message and submit to LLM

        const continueChat = async (id, message) => {
            try {
                // Show typing indicator
                setChatIsTyping(true);
                tempChatMessage(message);

                // Submit chat
                const response = await DataService.ContinueChatWithLLM(id, message);
                console.log(response.data);

                // Hide typing indicator and add response
                setChatIsTyping(false);

                setChat(response.data);
                forceRefresh();
            } catch (error) {
                console.error('Error fetching chat:', error);
                setChatIsTyping(false);
                setChat(null);
            }
        };
        continueChat(chat_id, message);
    };
    // Force re-render by updating the key
    const forceRefresh = () => {
        setRefreshKey(prevKey => prevKey + 1);
    };
    const askRag = (message) => {
        console.log(message);
        // Start a new chat and submit to LLM
        const queryRag = async (message) => {
            try {
                const messages = [...ragMessages, { ...message, role: 'user' }];
                // Show typing indicator
                setRagIsLoading(true);
                setRagMessages(messages);

                // Submit chat
                const response = await DataService.AskRagCopilot(message.content);
                console.log(response.data);

                const copilotMessage = {
                    role: 'assistant',
                    content: response.data.message?.copilot_response?.[0],
                };

                // Hide typing indicator and add response
                setRagIsLoading(false);

                setRagMessages([...messages, copilotMessage]);
            } catch (error) {
                console.error('Error asking rag:', error);
                setRagIsLoading(false);
                setRagMessages([]);
            }
        };
        queryRag(message);
    };

    return (
        <div className={styles.container}>
            <div className={styles.chatPanel}>
                <div className={styles.chatHeader}>
                    <div className={styles.logo} onClick={() => router.push('/')}>
                        SalesMate
                    </div>
                </div>
                <div className={styles.chatContent}>
                    {!chat && (
                        <h1 className={styles.promptHeader}>Initiate a conversation with your customer!</h1>
                    )}
                    {chat && chat.messages.map((message, i) => (
                        <div
                            key={i}
                            className={message.role === "assistant" ? styles.chatBotMessage : styles.chatUserMessage}
                        >
                            <Markdown>{message.content}</Markdown>
                        </div>
                    ))}
                    {chatIsTyping && <div className={styles.chatBotMessage}><TypingIndicator /></div>}
                </div>
                <div className={styles.chatInputWrapper}>
                    <ChatInput
                        onSendMessage={(message) => {
                            if (!chatId) {
                                newChat(message);
                            } else {
                                appendChat(message);
                            }
                        }}
                        chat={chat}
                        placeholder="Engage your customer..."
                    />
                </div>
            </div>
            <div className={styles.ragPanel}>
                <div className={styles.ragHeader}>
                    Knowledge Helper
                </div>
                <div className={styles.ragSubHeader}>
                    What would you like to know?
                </div>
                <div className={styles.ragContent}>
                    {ragMessages.map((message, i) => (
                        <div
                            key={i}
                            className={message.role === "assistant" ? styles.ragBotMessage : styles.ragUserMessage}
                        >
                            <Markdown>{message.content}</Markdown>
                        </div>
                    ))}
                    {ragIsLoading && <div className={styles.ragBotMessage}><TypingIndicator /></div>}
                    <div className={styles.ragInputWrapper}>
                        <ChatInput
                            onSendMessage={askRag}
                            chat={chat}
                            placeholder="Ask SalesMate..."
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}