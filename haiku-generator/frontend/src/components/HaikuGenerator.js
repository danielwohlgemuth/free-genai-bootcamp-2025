import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router';
import { fetchHaiku, sendMessage, generateMedia } from '../api/haikuApi';
import SummaryDisplay from './SummaryDisplay';
import LoadingIndicator from './LoadingIndicator';
import ErrorMessage from './ErrorMessage';
import { generateUUID } from '../utils/uuid';
import { Container, Paper, Button, Box, Typography, Breadcrumbs, Link, TextField, List, ListItem, ListItemText, ListItemIcon, Divider } from '@mui/material';

const HaikuGenerator = () => {
  const { haiku_id } = useParams();
  const [message, setMessage] = useState('');
  const [haiku, setHaiku] = useState({});
  const [chats, setChats] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingPage, setLoadingPage] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const getHaiku = async () => {
      try {
        const fetchedHaiku = await fetchHaiku(haiku_id);
        setHaiku(fetchedHaiku.haiku);
        setChats(fetchedHaiku.chats);
      } catch (error) {
        setError('Error fetching haiku');
        console.error('Error fetching haiku:', error);
      } finally {
        setLoadingPage(false);
      }
    };

    getHaiku();
  }, [haiku_id]);

  const handleSendMessage = async () => {
    setLoading(true);
    setError(null);
    try {
      const updatedHaiku = await sendMessage(haiku_id, message);
      setHaiku(updatedHaiku.haiku);
      setMessage('');
      setChats([...chats, { chat_id: generateUUID(), role: 'human', message }, updatedHaiku.chat]);
    } catch (error) {
      setError('Error sending message');
      console.error('Error sending message:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateMedia = async () => {
    setLoading(true);
    setError(null);
    try {
      const updatedHaiku = await generateMedia(haiku_id);
      setHaiku(updatedHaiku.haiku);
    } catch (error) {
      setError('Error generating media');
      console.error('Error generating media:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loadingPage) return <LoadingIndicator />;

  return (
    <Container maxWidth="sm">
      <Breadcrumbs aria-label="breadcrumb" sx={{ my: 2 }}>
        <Link underline="hover" color="inherit" href="/">
          Overview
        </Link>
        <Typography variant="h3" component="h2">
          Haiku Generator
        </Typography>
      </Breadcrumbs>

      <SummaryDisplay haiku={haiku} loading={loading} generateMedia={handleGenerateMedia} />

      {error && <ErrorMessage message={error} />}

      <Paper sx={{ my: 2 }}>
        <List dense={true}>
          {chats.map(chat => (
            <div key={chat.chat_id}>
              <ListItem>
                {chat.role === 'ai' && <ListItemIcon>🤖</ListItemIcon>}
                <ListItemText
                  sx={{ textAlign: chat.role === 'human' ? 'right' : 'left' }}
                  primary={chat.message}
                />
              </ListItem>
              <Divider variant="inset" component="li" />
            </div>
          ))}
        </List>

        {haiku.status === 'new' && (
          <Box sx={{ mx: 2, pb: 2, pt: 1, display: 'flex', gap: 2 }}>
            <TextField
              id="outlined-basic"
              label="Message"
              variant="outlined"
              size="small"
              fullWidth
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Type your message here..."
            />

            <Button onClick={handleSendMessage} variant="contained" loading={loading}>
              Send
            </Button>
          </Box>
        )}
        {haiku.status !== 'new' && (
          <Box sx={{ mx: 2, pb: 2, pt: 1, display: 'flex', gap: 2, justifyContent: 'center' }}>
            <Link underline="hover" color="inherit" href="/" sx={{ textAlign: 'center' }}>
              Go to overview
            </Link>
          </Box>
        )}
      </Paper>
    </Container>
  );
};

export default HaikuGenerator;