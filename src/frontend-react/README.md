
# SalesMate Frontend

The SalesMate frontend is a React-based application designed to provide an immersive sales training platform. The application features two primary pages: a home page and a simulator page, which work together to enhance the sales training experience. This README provides an overview of the application structure, setup instructions, and development workflows.

---

## Features

### **Home Page (`src/app/page.jsx`)**
The home page introduces **SalesMate** and provides an overview of the platform. Key features include:
- **About Section**: Learn about SalesMate's purpose and capabilities.
- **List of Prior Chats**: Displays a list of previous training sessions (chats). Users can select a chat to reenter the session.
- **"Start a New Run!" Button**: Allows users to initiate a new training session, redirecting them to the simulator page.

### **Simulator Page (`src/app/simulator/page.jsx`)**
The simulator page is the core of the sales training experience. It features:
- **Left Panel: Training Simulator Chat**
  - Users can engage in a simulated conversation with a "customer".
  - Conversations are persisted and available for review on the home page after leaving.
- **Right Panel: RAG-backed Knowledge Helper**
  - Users can ask questions to the Knowledge Helper, which is powered by a Retrieval-Augmented Generation (RAG) model.
  - **Note**: Conversations with the Knowledge Helper are **transient** and are not persisted after leaving the page.

---

## Getting Started

Follow these steps to set up and run the SalesMate frontend locally.

### **Initial Setup**
1. Navigate to the React frontend directory:
   ```bash
   cd AC215_SalesMate/src/frontend-react
   ```
2. Start the development container:
   ```bash
   sh docker-shell.sh
   ```

### **Dependencies Installation**
First-time setup only:
```bash
npm install
```

### **Launch Development Server**
1. Start the development server:
   ```bash
   npm run dev
   ```
2. View the application in your browser:
   [http://localhost:3000](http://localhost:3000)

---

## CI/CD Workflows

The project includes workflows for **linting** and **testing** to ensure code quality and stability. These are best run within the container to ensure the correct dependencies.

### **Linting**
Run the following command to lint the codebase:
```bash
npm run lint
```

### **Testing**
Run the following command to execute the test suite:
```bash
npm run test
```

The test suite verifies the mounting and rendering of both the **Home Page** (`HomePage.test.jsx`) and the **Simulator Page** (`SimulatorPage.test.jsx`). It ensures these components display their expected elements and handle mocked data correctly.

---

## Folder Structure

Here’s an overview of key folders and files:

```
AC215_SalesMate/src/frontend-react/src/
├── __tests__/               # Test files for pages
├── app/
│   ├── page.jsx              # Home page component
│   ├── simulator/
│   │   └── page.jsx          # Simulator page component
├── components/               # Shared UI components
├── services/                 # Shared utilities
├── package.json              # Project dependencies and scripts
└── README.md                 # Project documentation (this file)
```
