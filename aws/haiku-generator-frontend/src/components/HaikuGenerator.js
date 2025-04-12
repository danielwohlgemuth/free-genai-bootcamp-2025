import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router';
import { fetchHaiku, sendMessage, generateMedia } from '../api/haikuApi';
import SummaryDisplay from './SummaryDisplay';
import LoadingIndicator from './LoadingIndicator';
import ErrorMessage from './ErrorMessage';
import { generateUUID } from '../utils/uuid';
import { Container, Paper, Button, Box, Typography, Breadcrumbs, Link, TextField, List, ListItem, ListItemText, ListItemIcon, Divider } from '@mui/material';
import { useAuth } from 'react-oidc-context';

const HaikuGenerator = () => {
  const { haiku_id } = useParams();
  const [message, setMessage] = useState('');
  const [haiku, setHaiku] = useState({});
  const [chats, setChats] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingPage, setLoadingPage] = useState(true);
  const [error, setError] = useState(null);
  const auth = useAuth();

  useEffect(() => {
    const getHaiku = async () => {
      try {
        const token = auth.user?.access_token || '';
        const fetchedHaiku = await fetchHaiku(token, haiku_id);
        setHaiku(fetchedHaiku.haiku);
        setChats(fetchedHaiku.chats);
      } catch (error) {
        setError('Error fetching haiku');
        console.error('Error fetching haiku:', error);
      } finally {
        setLoadingPage(false);
      }
    };

    if (auth.isAuthenticated) {
      getHaiku();
    }
  }, [haiku_id, auth.isAuthenticated, auth.user?.access_token]);

  useEffect(() => {
    if (!auth.isAuthenticated && !auth.isLoading) {
      auth.signinRedirect();
    }
  }, [auth.isAuthenticated, auth.isLoading]);

  if (auth.isLoading) {
    return <div>Loading...</div>;
  }

  if (auth.error) {
    return (
      <div>
        Authentication error: {auth.error.message}.
        <button onClick={() => window.location.reload()} className="text-primary">
          Reload page
        </button>
      </div>
    );
  }

  if (!auth.isAuthenticated) {
    return null;
  }

  const handleSendMessage = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = auth.user?.access_token || '';
      const updatedHaiku = await sendMessage(token, haiku_id, message);
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
      const token = auth.user?.access_token || '';
      const updatedHaiku = await generateMedia(token, haiku_id);
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