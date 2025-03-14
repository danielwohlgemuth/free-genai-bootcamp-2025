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
    if (audio) {
      audio.pause();
      setIsPlaying(false);
    }
    const newAudio = new Audio(audioLink);
    newAudio.play();
    setAudio(newAudio);
    setIsPlaying(true);
  };

  return (
    <button onClick={handlePlay}>
      {isPlaying ? '⏸️' : '▶️'}
    </button>
  );
};

export default AudioPlayer;