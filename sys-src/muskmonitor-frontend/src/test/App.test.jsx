import { render, screen } from '@testing-library/react';
import App from '../App';

test('renders the App component', () => {
  render(<App />);
  expect(screen.getByText("This is my test")).toBeInTheDocument();
});