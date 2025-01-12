import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ShowStock from '../components/ShowStock_combined.jsx';
import axios from 'axios';
import { vi } from 'vitest';

// Mock Axios and Fetch
vi.mock('axios');
global.fetch = vi.fn();

describe('ShowStock Component', () => {
  beforeEach(() => {
    vi.clearAllMocks(); // Clear mocks before each test
  });

  it('fetches stock data, tweets, and predictions on mount', async () => {
    // Mock API responses
    fetch.mockImplementation((url) => {
      if (url === '/get_stock_data') {
        return Promise.resolve({
          json: () => Promise.resolve([{ Datum: '2023-01-01', close: 100 }]),
        });
      } else if (url === '/get_important_tweets') {
        return Promise.resolve({
          json: () => Promise.resolve([{ Date: '2023-01-01', Text: 'Important tweet' }]),
        });
      } else if (url === '/get_prediction_results') {
        return Promise.resolve({
          json: () =>
            Promise.resolve({
              predicted_values: [{ date: '2023-01-02', value: 110 }],
              future_predictions: [{ date: '2023-01-03', value: 120 }],
            }),
        });
      }
      return Promise.reject(new Error('Unknown endpoint'));
    });

    render(<ShowStock />);
    
    // Verify stock data is rendered
    const dataKeyLabel = await screen.findByLabelText('Select Data Key:');
    expect(dataKeyLabel).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledWith('/get_stock_data', expect.any(Object));
    expect(fetch).toHaveBeenCalledWith('/get_important_tweets');
    expect(fetch).toHaveBeenCalledWith('/get_prediction_results');
  });

  it('renders the LineChart with stock and prediction data', async () => {
    fetch.mockImplementation((url) => {
      if (url === '/get_stock_data') {
        return Promise.resolve({
          json: () => Promise.resolve([{ Datum: '2023-01-01', close: 100 }]),
        });
      } else if (url === '/get_important_tweets') {
        return Promise.resolve({
          json: () => Promise.resolve([{ Date: '2023-01-01', Text: 'Important tweet' }]),
        });
      } else if (url === '/get_prediction_results') {
        return Promise.resolve({
          json: () =>
            Promise.resolve({
              predicted_values: [{ date: '2023-01-02', value: 110 }],
              future_predictions: [{ date: '2023-01-03', value: 120 }],
            }),
        });
      }
      return Promise.reject(new Error('Unknown endpoint'));
    });

    render(<ShowStock />);

    // Wait for the chart to load
    const chartTitle = await screen.findByText('Stock Data Visualization');
    expect(chartTitle).toBeInTheDocument();

    // Verify the chart rendered data
    const selectElement = screen.getByLabelText('Select Data Key:');
    expect(selectElement).toBeInTheDocument();
  });

  it('updates state on date range input changes', async () => {
    render(<ShowStock />);

    // Simulate input change for start date
    const startDateInput = screen.getByLabelText('Start Date:');
    fireEvent.change(startDateInput, { target: { value: '2023-01-01' } });
    expect(startDateInput.value).toBe('2023-01-01');

    // Simulate input change for end date
    const endDateInput = screen.getByLabelText('End Date:');
    fireEvent.change(endDateInput, { target: { value: '2023-01-31' } });
    expect(endDateInput.value).toBe('2023-01-31');
  });

  it('toggles the second graph when checkbox is clicked', async () => {
    render(<ShowStock />);

    const checkbox = screen.getByLabelText('Show Predictions:');
    expect(checkbox.checked).toBe(false);

    fireEvent.click(checkbox);
    expect(checkbox.checked).toBe(true);
  });

  it('handles API errors gracefully', async () => {
    fetch.mockImplementation(() => Promise.reject(new Error('API error')));

    render(<ShowStock />);

    const loadingText = await screen.findByText('Loading data...');
    expect(loadingText).toBeInTheDocument();

    // Verify error logs
    expect(fetch).toHaveBeenCalledTimes(3);
  });
});
