import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

export interface Haiku {
  haiku_id: string;
  status: string;
  error_message: string;
  haiku_line_en_1: string;
  haiku_line_en_2: string;
  haiku_line_en_3: string;
  image_description_1: string;
  image_description_2: string;
  image_description_3: string;
  image_link_1: string;
  image_link_2: string;
  image_link_3: string;
  haiku_line_ja_1: string;
  haiku_line_ja_2: string;
  haiku_line_ja_3: string;
  audio_link_1: string;
  audio_link_2: string;
  audio_link_3: string;
}

export interface FetchHaikusResponse {
  haikus: Haiku[];
}

export interface FetchHaikuResponse {
  haiku: Haiku;
}

export interface SendMessageResponse {
  chat: {
    chat_id: number;
    haiku_id: string;
    role: string;
    message: string;
  };
  haiku: Haiku;
}

export interface DeleteHaikuResponse {
  message: string;
}

export const fetchHaikus = async (): Promise<FetchHaikusResponse> => {
  const response = await axios.get(`${API_URL}/haiku`);
  return response.data;
};

export const fetchHaiku = async (haiku_id: string): Promise<FetchHaikuResponse> => {
  const response = await axios.get(`${API_URL}/haiku/${haiku_id}`);
  return response.data;
};

export const sendMessage = async (haiku_id: string, message: string): Promise<SendMessageResponse> => {
  const response = await axios.post(`${API_URL}/chat/${haiku_id}`, { message });
  return response.data;
};

export const deleteHaiku = async (haiku_id: string): Promise<DeleteHaikuResponse> => {
  const response = await axios.delete(`${API_URL}/haiku/${haiku_id}`);
  return response.data;
};