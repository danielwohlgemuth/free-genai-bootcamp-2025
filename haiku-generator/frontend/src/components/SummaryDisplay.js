import React from 'react';
import AudioPlayer from './AudioPlayer';
import { Chip, Paper, Grid2, Box, Divider } from '@mui/material';

const STORAGE_URL = process.env.REACT_APP_STORAGE_URL || 'http://localhost:9000/haiku';

const SummaryDisplay = ({ haiku }) => {
  return (
    <Paper>
      <Box sx={{ p: 2 }}>
        <div>Status: <Chip label={haiku.status} variant="outlined" /></div>
        {haiku.error_message && (
          <>
            <p>Error: {haiku.error_message}</p>
            <Divider />
          </>
        )}

        {haiku.haiku_line_en_1 && haiku.haiku_line_en_2 && haiku.haiku_line_en_3 && (
          <>
            <p style={{ textAlign: 'center' }}>{haiku.haiku_line_en_1}</p>
            <p style={{ textAlign: 'center' }}>{haiku.haiku_line_en_2}</p>
            <p style={{ textAlign: 'center' }}>{haiku.haiku_line_en_3}</p>
          </>
        )}
      </Box>
      {(haiku.haiku_line_ja_1 || haiku.haiku_line_ja_2 || haiku.haiku_line_ja_3 || haiku.image_link_1 || haiku.image_link_2 || haiku.image_link_3) && (
        <>
          <Grid2 container spacing={2}>
            <Grid2 item size={{ xs: 12, sm: 6 }}>
              <Box sx={{ textAlign: 'center', display: 'flex', flexDirection: 'column', justifyContent: 'center', height: '100%' }}>
                {haiku.haiku_line_ja_1 && <p>{haiku.haiku_line_ja_1} {haiku.audio_link_1 && <AudioPlayer audioLink={`${STORAGE_URL}/${haiku.audio_link_1}`} />}</p>}
                {haiku.haiku_line_ja_2 && <p>{haiku.haiku_line_ja_2} {haiku.audio_link_2 && <AudioPlayer audioLink={`${STORAGE_URL}/${haiku.audio_link_2}`} />}</p>}
                {haiku.haiku_line_ja_3 && <p>{haiku.haiku_line_ja_3} {haiku.audio_link_3 && <AudioPlayer audioLink={`${STORAGE_URL}/${haiku.audio_link_3}`} />}</p>}
              </Box>
            </Grid2>
            <Grid2 item size={{ xs: 12, sm: 6 }}>
              {haiku.image_link_1 && <img src={`${STORAGE_URL}/${haiku.image_link_1}`} alt={haiku.image_description_1} width="100%" />}
            </Grid2>
            <Grid2 item size={{ xs: 12, sm: 6 }}>
              {haiku.image_link_2 && <img src={`${STORAGE_URL}/${haiku.image_link_2}`} alt={haiku.image_description_2} width="100%" />}
            </Grid2>
            <Grid2 item size={{ xs: 12, sm: 6 }}>
              {haiku.image_link_3 && <img src={`${STORAGE_URL}/${haiku.image_link_3}`} alt={haiku.image_description_3} width="100%" />}
            </Grid2>
          </Grid2>
        </>
      )}
    </Paper>
  );
};

export default SummaryDisplay;