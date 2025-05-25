import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Switch,
  FormControlLabel,
  Slider,
  Button,
  Divider,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Alert,
  Snackbar,
} from '@mui/material';

interface MLSettings {
  modelType: 'lstm' | 'xgboost' | 'random_forest';
  predictionHorizon: number;
  confidenceThreshold: number;
  featureImportance: boolean;
  autoRetrain: boolean;
  retrainInterval: number;
  dataSource: 'alpha_vantage' | 'yahoo_finance' | 'custom';
  apiKey?: string;
}

const Settings: React.FC = () => {
  const [settings, setSettings] = useState<MLSettings>({
    modelType: 'lstm',
    predictionHorizon: 5,
    confidenceThreshold: 0.7,
    featureImportance: true,
    autoRetrain: false,
    retrainInterval: 7,
    dataSource: 'alpha_vantage',
  });

  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSettings = async () => {
    try {
      // TODO: Replace with actual API call
      const response = await fetch('/api/settings');
      const data = await response.json();
      setSettings(data);
    } catch (error) {
      console.error('Error fetching settings:', error);
      setError('Failed to load settings');
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const handleSave = async () => {
    try {
      // TODO: Replace with actual API call
      await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings),
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (error) {
      console.error('Error saving settings:', error);
      setError('Failed to save settings');
    }
  };

  const handleSelectChange = (field: keyof MLSettings) => (
    event: React.ChangeEvent<{ value: unknown }> | any
  ) => {
    const value = event.target.value;
    setSettings((prev) => ({ ...prev, [field]: value }));
  };

  const handleChange = (field: keyof MLSettings) => (
    event: React.ChangeEvent<HTMLInputElement | { value: unknown }>
  ) => {
    const value = event.target.type === 'checkbox'
      ? (event.target as HTMLInputElement).checked
      : event.target.value;
    setSettings((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        ML Model Settings
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Model Configuration
              </Typography>

              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Model Type</InputLabel>
                <Select
                  value={settings.modelType}
                  label="Model Type"
                  onChange={handleSelectChange('modelType')}
                >
                  <MenuItem value="lstm">LSTM</MenuItem>
                  <MenuItem value="xgboost">XGBoost</MenuItem>
                  <MenuItem value="random_forest">Random Forest</MenuItem>
                </Select>
              </FormControl>

              <Typography gutterBottom>
                Prediction Horizon (days)
              </Typography>
              <Slider
                value={settings.predictionHorizon}
                onChange={(_, value) =>
                  setSettings((prev) => ({
                    ...prev,
                    predictionHorizon: value as number,
                  }))
                }
                min={1}
                max={30}
                marks
                valueLabelDisplay="auto"
                sx={{ mb: 2 }}
              />

              <Typography gutterBottom>
                Confidence Threshold
              </Typography>
              <Slider
                value={settings.confidenceThreshold}
                onChange={(_, value) =>
                  setSettings((prev) => ({
                    ...prev,
                    confidenceThreshold: value as number,
                  }))
                }
                min={0.5}
                max={0.95}
                step={0.05}
                marks
                valueLabelDisplay="auto"
                sx={{ mb: 2 }}
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={settings.featureImportance}
                    onChange={handleChange('featureImportance')}
                  />
                }
                label="Show Feature Importance"
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Training Configuration
              </Typography>

              <FormControlLabel
                control={
                  <Switch
                    checked={settings.autoRetrain}
                    onChange={handleChange('autoRetrain')}
                  />
                }
                label="Auto Retrain Model"
                sx={{ mb: 2 }}
              />

              {settings.autoRetrain && (
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Retrain Interval</InputLabel>
                  <Select
                    value={settings.retrainInterval}
                    label="Retrain Interval"
                    onChange={handleSelectChange('retrainInterval')}
                  >
                    <MenuItem value={1}>Daily</MenuItem>
                    <MenuItem value={7}>Weekly</MenuItem>
                    <MenuItem value={30}>Monthly</MenuItem>
                  </Select>
                </FormControl>
              )}

              <Divider sx={{ my: 2 }} />

              <Typography variant="h6" gutterBottom>
                Data Source
              </Typography>

              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Data Source</InputLabel>
                <Select
                  value={settings.dataSource}
                  label="Data Source"
                  onChange={handleSelectChange('dataSource')}
                >
                  <MenuItem value="alpha_vantage">Alpha Vantage</MenuItem>
                  <MenuItem value="yahoo_finance">Yahoo Finance</MenuItem>
                  <MenuItem value="custom">Custom API</MenuItem>
                </Select>
              </FormControl>

              {settings.dataSource === 'alpha_vantage' && (
                <TextField
                  fullWidth
                  label="Alpha Vantage API Key"
                  type="password"
                  value={settings.apiKey || ''}
                  onChange={handleChange('apiKey')}
                  sx={{ mb: 2 }}
                />
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
        <Button
          variant="contained"
          color="primary"
          onClick={handleSave}
          size="large"
        >
          Save Settings
        </Button>
      </Box>

      <Snackbar
        open={saved}
        autoHideDuration={3000}
        onClose={() => setSaved(false)}
      >
        <Alert severity="success" onClose={() => setSaved(false)}>
          Settings saved successfully
        </Alert>
      </Snackbar>

      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
      >
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Settings; 