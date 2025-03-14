import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { generateUUID } from '../utils/uuid';

const HaikuList = () => {
  const [haikus, setHaikus] = useState([]);

  useEffect(() => {
    const fetchHaikus = async () => {
      try {
        const response = await axios.get('/haiku');
        setHaikus(response.data.haikus);
      } catch (error) {
        console.error('Error fetching haikus:', error);
      }
    };

    fetchHaikus();
  }, []);

  const handleDelete = async (haiku_id) => {
    try {
      await axios.delete(`/haiku/${haiku_id}`);
      setHaikus(haikus.filter(haiku => haiku.haiku_id !== haiku_id));
    } catch (error) {
      console.error('Error deleting haiku:', error);
    }
  };

  const handleCreateNewHaiku = () => {
    const newHaikuId = generateUUID();
    window.location.href = `/haiku/${newHaikuId}`;
  };

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