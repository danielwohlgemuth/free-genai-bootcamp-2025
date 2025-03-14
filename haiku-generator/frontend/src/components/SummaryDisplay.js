import React from 'react';

const SummaryDisplay = ({ haiku }) => {
  return (
    <div className="summary-display">
      <h2>Summary</h2>
      {haiku.haiku_line_ja_1 && (
        <div className="japanese-haiku">
          <h3>Japanese Haiku Lines:</h3>
          <p>{haiku.haiku_line_ja_1}</p>
          <p>{haiku.haiku_line_ja_2}</p>
          <p>{haiku.haiku_line_ja_3}</p>
        </div>
      )}
      <div className="images">
        {haiku.image_link_1 && <img src={haiku.image_link_1} alt={haiku.image_description_1} />}
        {haiku.image_link_2 && <img src={haiku.image_link_2} alt={haiku.image_description_2} />}
        {haiku.image_link_3 && <img src={haiku.image_link_3} alt={haiku.image_description_3} />}
      </div>
      <div className="audio">
        {haiku.audio_link_1 && <audio controls src={haiku.audio_link_1}>Audio 1</audio>}
        {haiku.audio_link_2 && <audio controls src={haiku.audio_link_2}>Audio 2</audio>}
        {haiku.audio_link_3 && <audio controls src={haiku.audio_link_3}>Audio 3</audio>}
      </div>
    </div>
  );
};

export default SummaryDisplay;