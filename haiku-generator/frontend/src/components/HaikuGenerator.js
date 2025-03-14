import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';

const HaikuGenerator = () => {
  const { haiku_id } = useParams();
  const [message, setMessage] = useState('');
  const [haiku, setHaiku] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchHaiku = async () => {
      try {
        const response = await axios.get(`/haiku/${haiku_id}`);
        setHaiku(response.data.haiku);
      } catch (error) {
        console.error('Error fetching haiku:', error);
      }
    };

    fetchHaiku();
  }, [haiku_id]);

  const handleSendMessage = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`/chat/${haiku_id}`, { message });
      setHaiku(response.data.haiku);
      setMessage('');
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Haiku Generator</h1>
      <div>
        <h2>Current Haiku:</h2>
        <p>{haiku.haiku_line_en_1} {haiku.haiku_line_en_2} {haiku.haiku_line_en_3}</p>
        <p>Status: {haiku.status}</p>
      </div>
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