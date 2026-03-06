import axios from 'axios';

const API_BASE = 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE,
    timeout: 300000, // 5 min timeout for AI pipeline
});

// === Upload ===
export const uploadFiles = async (files) => {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    const res = await api.post('/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
};

export const listFiles = async () => {
    const res = await api.get('/api/files');
    return res.data;
};

export const deleteFile = async (filename) => {
    const res = await api.delete(`/api/files/${filename}`);
    return res.data;
};

// === Pipeline ===
export const runPipeline = async (topic, questions) => {
    const res = await api.post('/api/pipeline/run', { topic, questions });
    return res.data;
};

export const getPipelineStatus = async (runId) => {
    const res = await api.get(`/api/pipeline/status/${runId}`);
    return res.data;
};

export const getPipelineResult = async (runId) => {
    const res = await api.get(`/api/pipeline/result/${runId}`);
    return res.data;
};

export const listPipelineRuns = async () => {
    const res = await api.get('/api/pipeline/runs');
    return res.data;
};

// === Reports ===
export const listReports = async () => {
    const res = await api.get('/api/reports/');
    return res.data;
};

export const getReport = async (filename) => {
    const res = await api.get(`/api/reports/${filename}`);
    return res.data;
};

export const deleteReport = async (filename) => {
    const res = await api.delete(`/api/reports/${filename}`);
    return res.data;
};

export const downloadReportUrl = (filename) => {
    return `${API_BASE}/api/reports/${filename}/download`;
};

// === Config ===
export const getConfig = async () => {
    const res = await api.get('/api/config');
    return res.data;
};

export const getHealth = async () => {
    const res = await api.get('/api/health');
    return res.data;
};

// === WebSocket ===
export const createProgressWebSocket = (onMessage, onError) => {
    const ws = new WebSocket('ws://localhost:8000/ws/progress');

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        onMessage(data);
    };

    ws.onerror = (error) => {
        if (onError) onError(error);
    };

    // Keep alive
    const keepAlive = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
            ws.send('ping');
        }
    }, 30000);

    ws.onclose = () => {
        clearInterval(keepAlive);
    };

    return ws;
};

export default api;
