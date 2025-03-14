import React, { useEffect, useState } from 'react';
import axios from 'axios';
import LoadingIndicator from './LoadingIndicator';
import ErrorMessage from './ErrorMessage';
import { generateUUID } from '../utils/uuid';

const HaikuList = () => {
  const [haikus, setHaikus] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchHaikus = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await axios.get('/haiku');
        setHaikus(response.data.haikus);
      } catch (error) {
        setError('Error fetching haikus');
        console.error('Error fetching haikus:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchHaikus();
  }, []);

  const handleDelete = async (haiku_id) => {
    try {
      await axios.delete(`/haiku/${haiku_id}`);
      setHaikus(haikus.filter(haiku => haiku.haiku_id !== haiku_id));
    } catch (error) {
      setError('Error deleting haiku');
      console.error('Error deleting haiku:', error);
    }
  };

  const handleCreateNewHaiku = () => {
    const newHaikuId = generateUUID();
    window.location.href = `/haiku/${newHaikuId}`;
  };

  if (loading) return <LoadingIndicator />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div>
      <h1>Haiku Overview</h1>
      <button onClick={handleCreateNewHaiku}>Create New Haiku</button>
      <ul>
        {haikus.map(haiku => (
          <li key={haiku.haiku_id}>
            <h2>{haiku.haiku_line_en_1} {haiku.haiku_line_en_2} {haiku.haiku_line_en_3}</h2>
            <p>Status: {haiku.status}</p>
            <button onClick={() => handleDelete(haiku.haiku_id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default HaikuList;