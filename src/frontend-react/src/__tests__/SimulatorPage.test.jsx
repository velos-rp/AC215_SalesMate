import { render, screen, waitFor } from '@testing-library/react';
import SimulatorPage from '@/app/simulator/page';
import DataService from '@/services/DataService';
import { useRouter } from 'next/navigation';

// Mock the useRouter function from Next.js
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

// Mock the DataService
jest.mock('@/services/DataService', () => ({
  GetChat: jest.fn(),
}));

// Mock the React `use` function
jest.mock('react', () => {
  const originalReact = jest.requireActual('react');
  return {
    ...originalReact,
    use: jest.fn(),
  };
});

// Mock react-markdown, remark-grm, rehype-raw used in ChatContent.jsx
jest.mock('react-markdown', () => (props) => <div>{props.children}</div>);
jest.mock('remark-gfm', () => jest.fn());
jest.mock('rehype-raw', () => jest.fn());

describe('SimulatorPage', () => {
  beforeEach(() => {
    // Mock useRouter
    useRouter.mockReturnValue({
      push: jest.fn(),
    });

    // Mock DataService.GetChat
    DataService.GetChat.mockResolvedValue({
      data: {
        chat_id: '1',
        messages: [{ role: 'user', content: 'Hello!' }],
      },
    });

    // Mock the `use` function to simulate resolved server props
    jest.mocked(require('react').use).mockImplementation((searchParams) => searchParams);
  });

  afterEach(() => {
    jest.clearAllMocks(); // Clear mocks after each test
  });

  it('renders the chat messages when chat data exists', async () => {
    // Mock GetChat to return valid chat data
    DataService.GetChat.mockResolvedValueOnce({
      data: {
        chat_id: '1',
        messages: [{ role: 'user', content: 'Hello!' }],
      },
    });
  
    render(<SimulatorPage searchParams={{ id: 'test-chat-id' }} />);
  
    // Wait for the chat message to appear
    await waitFor(() => {
      const chatMessage = screen.getByText(/Hello!/i);
      expect(chatMessage).toBeInTheDocument();
    });
  });  
});
