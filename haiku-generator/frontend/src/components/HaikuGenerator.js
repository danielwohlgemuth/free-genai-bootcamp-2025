import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router';
import { fetchHaiku, sendMessage } from '../api/haikuApi';
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
    const getHaiku = async () => {
      try {
        const fetchedHaiku = await fetchHaiku(haiku_id);
        setHaiku(fetchedHaiku);
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
      setHaiku(updatedHaiku);
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