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
    GetChats: async function (model, limit) {
        return await api.get(BASE_API_URL + "/direct-chat/chats?limit=" + limit);
    },
    GetChat: async function (model, chat_id) {
        return await api.get(BASE_API_URL + "/direct-chat/chats/" + chat_id);
    },
    StartChatWithLLM: async function (model, message) {
        return await api.post(BASE_API_URL + "/direct-chat/chats/", message);
    },
    ContinueChatWithLLM: async function (model, chat_id, message) {
        return await api.post(BASE_API_URL + "/direct-chat/chats/" + chat_id, message);
    },
    AskRagCopilot: async function (query) {
        return await api.get(BASE_API_URL + "/rag-copilot", { params: { input: query } });
    },
}

export default DataService;