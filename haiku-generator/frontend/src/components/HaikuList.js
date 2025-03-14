import React, { useEffect, useState } from 'react';
import axios from 'axios';

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

  return (
    <div>
      <h1>Haiku Overview</h1>
      <ul>
        {haikus.map(haiku => (
          <li key={haiku.haiku_id}>
            <h2>{haiku.haiku_line_en_1} {haiku.haiku_line_en_2} {haiku.haiku_line_en_3}</h2>
            <p>Status: {haiku.status}</p>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default HaikuList;