import React, { useState } from 'react';

const SummaryDisplay = ({ haiku }) => {
  const [playingAudio, setPlayingAudio] = useState(null); // Track which audio is playing

  const handlePlayAudio = (audioLink) => {
    if (playingAudio) {
      playingAudio.pause(); // Pause currently playing audio
    }
    const audio = new Audio(audioLink);
    audio.play();
    setPlayingAudio(audio); // Set the current audio to playing
    audio.onended = () => setPlayingAudio(null); // Reset when audio ends
  };

  return (
    <div className="summary-display">
      <div className="english-haiku">
        <h3>English Haiku Lines:</h3>
        <p>{haiku.haiku_line_en_1}</p>
        <p>{haiku.haiku_line_en_2}</p>
        <p>{haiku.haiku_line_en_3}</p>
        <p>Status: {haiku.status}</p>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="japanese-haiku">
          <h3>Japanese Haiku Lines:</h3>
          <p>
            {haiku.haiku_line_ja_1} 
            {haiku.audio_link_1 && (
              <button onClick={() => handlePlayAudio(haiku.audio_link_1)}>
                {playingAudio ? '⏸️' : '▶️'}
              </button>
            )}
          </p>
          <p>
            {haiku.haiku_line_ja_2} 
            {haiku.audio_link_2 && (
              <button onClick={() => handlePlayAudio(haiku.audio_link_2)}>
                {playingAudio ? '⏸️' : '▶️'}
              </button>
            )}
          </p>
          <p>
            {haiku.haiku_line_ja_3} 
            {haiku.audio_link_3 && (
              <button onClick={() => handlePlayAudio(haiku.audio_link_3)}>
                {playingAudio ? '⏸️' : '▶️'}
              </button>
            )}
          </p>
        </div>
        <div className="image-display">
          {haiku.image_link_1 && <img src={haiku.image_link_1} alt={haiku.image_description_1} />}
        </div>
        <div className="image-display">
          {haiku.image_link_2 && <img src={haiku.image_link_2} alt={haiku.image_description_2} />}
        </div>
        <div className="image-display">
          {haiku.image_link_3 && <img src={haiku.image_link_3} alt={haiku.image_description_3} />}
        </div>
      </div>
    </div>
  );
};

export default SummaryDisplay;