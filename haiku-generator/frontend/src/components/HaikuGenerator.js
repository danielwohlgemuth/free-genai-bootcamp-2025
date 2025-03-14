import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';
import SummaryDisplay from './SummaryDisplay';
import LoadingIndicator from './LoadingIndicator';
import ErrorMessage from './ErrorMessage';

const HaikuGenerator = () => {
  const { haiku_id } = useParams();
  const [message, setMessage] = useState('');
  const [haiku, setHaiku] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchHaiku = async () => {
      try {
        const response = await axios.get(`/haiku/${haiku_id}`);
        setHaiku(response.data.haiku);
      } catch (error) {
        setError('Error fetching haiku');
        console.error('Error fetching haiku:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchHaiku();
  }, [haiku_id]);

  const handleSendMessage = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(`/chat/${haiku_id}`, { message });
      setHaiku(response.data.haiku);
      setMessage('');
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