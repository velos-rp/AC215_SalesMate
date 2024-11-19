import { render, screen, waitFor } from '@testing-library/react';
import HomePage from '@/app/page';
import DataService from '@/services/DataService';
import { useRouter } from 'next/navigation';

// Mock the useRouter function from Next.js
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

// Mock the DataService
jest.mock('@/services/DataService', () => ({
  GetChats: jest.fn(),
}));

describe('HomePage', () => {
  beforeEach(() => {
    // Mock useRouter
    useRouter.mockReturnValue({
      push: jest.fn(), // Mock push method
    });

    // Mock GetChats
    DataService.GetChats.mockResolvedValue({
      data: [
        { chat_id: '1', title: 'Test Chat 1', dts: new Date().toISOString() },
        { chat_id: '2', title: 'Test Chat 2', dts: new Date().toISOString() },
      ],
    });
  });

  afterEach(() => {
    jest.clearAllMocks(); // Clear mocks after each test
  });

  it('renders without crashing', async () => {
    render(<HomePage />);

    // Wait for the state updates to complete
    await waitFor(() => {
      const chats = screen.getAllByText(/Test Chat/i);
      expect(chats).toHaveLength(2);
    });

    // Check if the specific hero heading (h1) is in the document
    const heroHeading = screen.getByRole('heading', { name: /salesmate/i, level: 1 });
    expect(heroHeading).toBeInTheDocument();
  });
});
