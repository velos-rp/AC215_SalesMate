import { BASE_API_URL, uuid } from "./Common";
import axios from 'axios';

// Create an axios instance with base configuration
const api = axios.create();

// Add request interceptor to include session ID and handle API prefix
api.interceptors.request.use((config) => {
    const sessionId = localStorage.getItem('userSessionId');
    if (sessionId) {
        config.headers['X-Session-ID'] = sessionId;
    }

    console.log("Prelim URL: " + config.url);

    // In production, ensure the URL starts with /api
    if (process.env.NODE_ENV === 'production') {
        const path = config.url.replace(BASE_API_URL, '');
        console.log("Path with API prefix replace: ", path);
        config.url = `/api${path}`;
        console.log("Final URL: " + config.url);
    } else {
        // In development, use the full BASE_API_URL
        if (!config.url.startsWith(BASE_API_URL)) {
            config.url = BASE_API_URL + config.url;
        }
    }
    
    return config;
}, (error) => {
    return Promise.reject(error);
});

const DataService = {
    Init: function () {
        // Any application initialization logic comes here
    },
    GetChats: async function (limit) {
        return await api.get("/direct-chat/chats?limit=" + limit);
    },
    GetChat: async function (chat_id) {
        return await api.get("/direct-chat/chats/" + chat_id);
    },
    StartChatWithLLM: async function (message) {
        return await api.post("/direct-chat/chats/", message);
    },
    ContinueChatWithLLM: async function (chat_id, message) {
        return await api.post("/direct-chat/chats/" + chat_id, message);
    },
    AskRagCopilot: async function (query) {
        return await api.get("/rag-copilot/insights", { params: { input: query } });
    },
}

export default DataService;