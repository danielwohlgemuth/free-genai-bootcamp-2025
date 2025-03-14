import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router';
import { fetchHaiku, sendMessage } from '../api/haikuApi';
import SummaryDisplay from './SummaryDisplay';
import LoadingIndicator from './LoadingIndicator';
import ErrorMessage from './ErrorMessage';
import { generateUUID } from '../utils/uuid';

const HaikuGenerator = () => {
  const { haiku_id } = useParams();
  const [message, setMessage] = useState('');
  const [haiku, setHaiku] = useState({});
  const [chats, setChats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const getHaiku = async () => {
      try {
        const fetchedHaiku = await fetchHaiku(haiku_id);
        setHaiku(fetchedHaiku.haiku);
        setChats(fetchedHaiku.chats);
      } catch (error) {
        setError('Error fetching haiku');
        console.error('Error fetching haiku:', error);
      } finally {
        setLoading(false);
      }
    };

    getHaiku();
  }, [haiku_id]);

  const handleSendMessage = async () => {
    setLoading(true);
    setError(null);
    try {
      const updatedHaiku = await sendMessage(haiku_id, message);
      setHaiku(updatedHaiku.haiku);
      setMessage('');
      setChats([...chats, { chat_id: generateUUID(), role: 'user', message }, updatedHaiku.chat]);
    } catch (error) {
      setError('Error sending message');
      console.error('Error sending message:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingIndicator />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div>
      <h1>Haiku Generator</h1>
      <SummaryDisplay haiku={haiku} />
      <ul>
        {chats.map(chat => (
          <li key={chat.chat_id}>
            <strong>{chat.role}</strong>: {chat.message}
          </li>
        ))}
      </ul>
      <textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Type your message here..."
      />
      <button onClick={handleSendMessage} disabled={loading}>
        {loading ? 'Sending...' : 'Send'}
      </button>
    </div>
  );
};

export default HaikuGenerator;