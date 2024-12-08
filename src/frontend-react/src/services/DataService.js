import { BASE_API_URL, uuid } from "./Common";
import axios from 'axios';

// Create an axios instance with base configuration
const api = axios.create({
    baseURL: BASE_API_URL
});
// Add request interceptor to include session ID in headers
api.interceptors.request.use((config) => {
    const sessionId = localStorage.getItem('userSessionId');
    if (sessionId) {
        config.headers['X-Session-ID'] = sessionId;
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
        return await api.get("direct-chat/chats?limit=" + limit);
    },
    GetChat: async function (chat_id) {
        return await api.get("direct-chat/chats/" + chat_id);
    },
    StartChatWithLLM: async function (message) {
        return await api.post((process.env.NODE_ENV === 'production' ? BASE_API_URL : "") + "direct-chat/chats/", message);
    },
    ContinueChatWithLLM: async function (chat_id, message) {
        return await api.post((process.env.NODE_ENV === 'production' ? BASE_API_URL : "") + "direct-chat/chats/" + chat_id, message);
    },
    AskRagCopilot: async function (query) {
        return await api.get("rag-copilot/insights", { params: { input: query } });
    },
}

export default DataService;