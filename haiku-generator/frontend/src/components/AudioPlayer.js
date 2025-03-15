import React, { useState, useEffect } from 'react';

const AudioPlayer = ({ audioLink }) => {
  const [audio, setAudio] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    if (audio) {
      audio.onended = () => setIsPlaying(false);
    }
  }, [audio]);

  const handlePlay = () => {
    if (isPlaying) {
      audio.pause();
      setIsPlaying(false);
    } else {
      let currentAudio = audio;
      if (!currentAudio) {
        currentAudio = new Audio(audioLink);
        setAudio(currentAudio);
      }
      currentAudio.play();
      setIsPlaying(true);
    }
  };

  return (
    <button onClick={handlePlay}>
      {isPlaying ? '⏸️' : '▶️'}
    </button>
  );
};

export default AudioPlayer;