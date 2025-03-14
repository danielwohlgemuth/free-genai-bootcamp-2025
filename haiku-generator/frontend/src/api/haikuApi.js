import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

export const fetchHaikus = async () => {
  const response = await axios.get(`${API_URL}/haiku`);
  return response.data.haikus;
};

export const fetchHaiku = async (haiku_id) => {
  const response = await axios.get(`${API_URL}/haiku/${haiku_id}`);
  return response.data.haiku;
};

export const sendMessage = async (haiku_id, message) => {
  const response = await axios.post(`${API_URL}/chat/${haiku_id}`, { message });
  return response.data;
};

export const deleteHaiku = async (haiku_id) => {
  const response = await axios.delete(`${API_URL}/haiku/${haiku_id}`);
  return response.data;
};