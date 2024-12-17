import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ShowStock from '../components/ShowStock_combined.jsx';
import axios from 'axios';

// Mock Axios and Fetch
vi.mock('axios');
global.fetch = vi.fn();

// Mock Data for Stock and Tweets
// MOCK DATA WIP
const mockStockData = {
  'Time Series (Daily)': "..."
};

// MOCK DATA WIP
const mockTweets = [
  { "Tweets...": '...' },
];

describe('ShowStock Component', () => {
  beforeEach(() => {
    // Mock Axios Response for stock data
    axios.get.mockResolvedValue({
      data: mockStockData,
    });

    // Mock Fetch Response for tweets
    fetch.mockResolvedValue({
      json: vi.fn().mockResolvedValue(mockTweets),
    });

    global.URL.createObjectURL = vi.fn(() => 'mock-url');
    global.URL.revokeObjectURL = vi.fn();
  });

  test('renders the component and displays stock data', async () => {
    render(<ShowStock />);

    // Wait for the async data to be fetched and rendered
    // await waitFor(() => expect(axios.get).toHaveBeenCalledTimes(1));

    // Check if the stock data is displayed
    expect(screen.getByText('Stock Data Visualization')).toBeInTheDocument();
  });

  afterAll(() => {
    delete global.URL.createObjectURL;
  });
});
