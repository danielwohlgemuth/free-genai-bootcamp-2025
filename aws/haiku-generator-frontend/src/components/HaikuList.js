import React, { useEffect, useState } from 'react';
import { fetchHaikus, deleteHaiku } from '../api/haikuApi';
import LoadingIndicator from './LoadingIndicator';
import ErrorMessage from './ErrorMessage';
import { generateUUID } from '../utils/uuid';
import { Button, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Link, Container, Chip } from '@mui/material';
import { useAuth } from 'react-oidc-context';

const HaikuList = () => {
  const [haikus, setHaikus] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const auth = useAuth();

  useEffect(() => {
    const fetchHaikusData = async () => {
      setLoading(true);
      setError(null);
      try {
        const token = auth.user?.access_token || '';
        const fetchedHaikus = await fetchHaikus(token);
        setHaikus(fetchedHaikus.haikus);
      } catch (error) {
        setError('Error fetching haikus');
        console.error('Error fetching haikus:', error);
      } finally {
        setLoading(false);
      }
    };

    if (auth.isAuthenticated) {
      fetchHaikusData();
    }
  }, [auth.isAuthenticated, auth.user?.access_token]);

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

  const handleDelete = async (haiku_id) => {
    try {
      const token = auth.user?.access_token || '';
      await deleteHaiku(token, haiku_id);
      setHaikus(haikus.filter(haiku => haiku.haiku_id !== haiku_id));
    } catch (error) {
      setError('Error deleting haiku');
      console.error('Error deleting haiku:', error);
    }
  };

  const handleCreateNewHaiku = () => {
    const newHaikuId = generateUUID();
    window.location.href = `/haiku/${newHaikuId}`;
  };

  if (loading && !error) {
    return <LoadingIndicator />;
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }

  return (
    <Container maxWidth="sm">
      <Typography variant="h3" component="h2" sx={{ my: 2 }}>
        Haiku Overview
      </Typography>

      <Button variant="contained" onClick={handleCreateNewHaiku} sx={{ my: 1 }}>New Haiku</Button>

      <TableContainer component={Paper} sx={{ my: 2 }}>
        <Table aria-label="haiku table">
          <TableHead>
            <TableRow>
              <TableCell>Haiku</TableCell>
              <TableCell align="center">Status</TableCell>
              <TableCell align="center">Delete</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {haikus.map((haiku) => (
              <TableRow
                key={haiku.haiku_id}
                sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
              >
                <TableCell component="th" scope="row">
                  <Link href={`/haiku/${haiku.haiku_id}`} underline="hover">
                    {haiku.haiku_line_en_1 && haiku.haiku_line_en_2 && haiku.haiku_line_en_3 && (
                      <>
                        <div>{haiku.haiku_line_en_1}</div>
                        <div>{haiku.haiku_line_en_2}</div>
                        <div>{haiku.haiku_line_en_3}</div>
                      </>
                    ) || haiku.haiku_id}
                  </Link>
                </TableCell>
                <TableCell align="center">
                  <Chip label={haiku.status} variant="outlined" color={haiku.status === 'new' ? 'primary' : haiku.status === 'failed' ? 'error' : 'success'} />
                </TableCell>
                <TableCell align="center">
                  <Button onClick={() => handleDelete(haiku.haiku_id)}>🗑️</Button>
                </TableCell>
              </TableRow>
            ))}
            {haikus.length === 0 && (
              <TableRow>
                <TableCell colSpan={3} align="center">
                  No haikus found
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
};

export default HaikuList;