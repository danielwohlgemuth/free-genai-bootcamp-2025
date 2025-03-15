import React from 'react';
import AudioPlayer from './AudioPlayer';

const STORAGE_URL = process.env.REACT_APP_STORAGE_URL || 'http://localhost:9000';

const SummaryDisplay = ({ haiku }) => {
  return (
    <div className="summary-display">
      <div className="english-haiku">
        {haiku.haiku_line_en_1 && haiku.haiku_line_en_2 && haiku.haiku_line_en_3 && (
          <>
            <h3>Haiku:</h3>
            <p>{haiku.haiku_line_en_1}</p>
            <p>{haiku.haiku_line_en_2}</p>
            <p>{haiku.haiku_line_en_3}</p>
          </>
        )}
        <p>Status: {haiku.status}</p>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="japanese-haiku">
          {haiku.haiku_line_ja_1 && <p>{haiku.haiku_line_ja_1} {haiku.audio_link_1 && <AudioPlayer audioLink={`${STORAGE_URL}/haiku/${haiku.audio_link_1}`} />}</p>}
          {haiku.haiku_line_ja_2 && <p>{haiku.haiku_line_ja_2} {haiku.audio_link_2 && <AudioPlayer audioLink={`${STORAGE_URL}/haiku/${haiku.audio_link_2}`} />}</p>}
          {haiku.haiku_line_ja_3 && <p>{haiku.haiku_line_ja_3} {haiku.audio_link_3 && <AudioPlayer audioLink={`${STORAGE_URL}/haiku/${haiku.audio_link_3}`} />}</p>}
        </div>
        <div className="image-display">
          {haiku.image_link_1 && <img src={`${STORAGE_URL}/haiku/${haiku.image_link_1}`} alt={haiku.image_description_1} />}
        </div>
        <div className="image-display">
          {haiku.image_link_2 && <img src={`${STORAGE_URL}/haiku/${haiku.image_link_2}`} alt={haiku.image_description_2} />}
        </div>
        <div className="image-display">
          {haiku.image_link_3 && <img src={`${STORAGE_URL}/haiku/${haiku.image_link_3}`} alt={haiku.image_description_3} />}
        </div>
      </div>
    </div>
  );
};

export default SummaryDisplay;