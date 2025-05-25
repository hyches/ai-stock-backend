import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CardActions,
  Typography,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Tooltip,
} from '@mui/material';
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { useApi } from '../hooks/useApi';

interface Strategy {
  id: number;
  name: string;
  description: string;
  type: string;
  parameters: Record<string, any>;
  status: string;
}

const StrategyList: React.FC = () => {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingStrategy, setEditingStrategy] = useState<Strategy | null>(null);
  const api = useApi();

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    type: '',
    parameters: {},
  });

  useEffect(() => {
    fetchStrategies();
  }, []);

  const fetchStrategies = async () => {
    try {
      setLoading(true);
      const response = await api.get('/strategies/');
      setStrategies(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to load strategies');
      setLoading(false);
    }
  };

  const handleOpenDialog = (strategy?: Strategy) => {
    if (strategy) {
      setEditingStrategy(strategy);
      setFormData({
        name: strategy.name,
        description: strategy.description,
        type: strategy.type,
        parameters: strategy.parameters,
      });
    } else {
      setEditingStrategy(null);
      setFormData({
        name: '',
        description: '',
        type: '',
        parameters: {},
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingStrategy(null);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async () => {
    try {
      if (editingStrategy) {
        await api.put(`/strategies/${editingStrategy.id}`, formData);
      } else {
        await api.post('/strategies/', formData);
      }
      handleCloseDialog();
      fetchStrategies();
    } catch (err) {
      setError('Failed to save strategy');
    }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this strategy?')) {
      try {
        await api.delete(`/strategies/${id}`);
        fetchStrategies();
      } catch (err) {
        setError('Failed to delete strategy');
      }
    }
  };

  if (loading) {
    return <Typography>Loading strategies...</Typography>;
  }

  if (error) {
    return <Typography color="error">{error}</Typography>;
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6">Trading Strategies</Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add Strategy
        </Button>
      </Box>

      <Grid container spacing={3}>
        {strategies.map((strategy) => (
          <Grid item xs={12} sm={6} md={4} key={strategy.id}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {strategy.name}
                </Typography>
                <Typography color="textSecondary" gutterBottom>
                  {strategy.type}
                </Typography>
                <Typography variant="body2">{strategy.description}</Typography>
                <Typography variant="body2" color="textSecondary" mt={1}>
                  Status: {strategy.status}
                </Typography>
              </CardContent>
              <CardActions>
                <Tooltip title="Edit">
                  <IconButton onClick={() => handleOpenDialog(strategy)}>
                    <EditIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Delete">
                  <IconButton onClick={() => handleDelete(strategy.id)}>
                    <DeleteIcon />
                  </IconButton>
                </Tooltip>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingStrategy ? 'Edit Strategy' : 'Add New Strategy'}
        </DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <TextField
              name="name"
              label="Strategy Name"
              value={formData.name}
              onChange={handleInputChange}
              fullWidth
            />
            <TextField
              name="description"
              label="Description"
              value={formData.description}
              onChange={handleInputChange}
              multiline
              rows={3}
              fullWidth
            />
            <FormControl fullWidth>
              <InputLabel>Strategy Type</InputLabel>
              <Select
                name="type"
                value={formData.type}
                onChange={handleInputChange}
                label="Strategy Type"
              >
                <MenuItem value="trend_following">Trend Following</MenuItem>
                <MenuItem value="mean_reversion">Mean Reversion</MenuItem>
                <MenuItem value="breakout">Breakout</MenuItem>
                <MenuItem value="custom">Custom</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" color="primary">
            {editingStrategy ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default StrategyList; 