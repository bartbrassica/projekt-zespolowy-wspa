# Digital Lockbox - Frontend

A secure password management application frontend built with React, TypeScript, and TailwindCSS.

## Tech Stack

- **Framework**: React 19
- **Language**: TypeScript
- **Build Tool**: Vite 6
- **Styling**: TailwindCSS 4
- **Routing**: React Router 7
- **Icons**: Lucide React
- **Linting**: ESLint with TypeScript support

## Prerequisites

- Node.js 20+
- npm

## Development Setup

### 1. Install dependencies

```bash
npm install
```

### 2. Configure environment (optional)

The development server is pre-configured to proxy API requests to `http://localhost:8000`. If your API runs on a different port, update `vite.config.ts`:

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:YOUR_PORT',
      changeOrigin: true,
      secure: false,
    }
  }
}
```

### 3. Start development server

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint

## Building for Production

### Standard build

```bash
npm run build
```

The build output will be in the `dist/` directory.

### Docker build

See the main project README for Docker deployment instructions.

## Project Structure

```
src/
├── components/          # Reusable UI components
├── contexts/           # React contexts (auth, theme, etc.)
├── hooks/              # Custom React hooks
│   ├── useAuth.ts
│   ├── usePasswordManager.ts
│   └── ...
├── pages/              # Page components
│   ├── Login.tsx
│   ├── Register.tsx
│   ├── Dashboard.tsx
│   └── ...
├── services/           # API services
│   └── authApi.ts
├── types/              # TypeScript type definitions
│   └── auth.ts
├── App.tsx             # Main app component
├── main.tsx           # Application entry point
└── index.css          # Global styles
```

## Features

- User authentication (login, register, password reset)
- Email verification
- Secure password storage and management
- Password generation
- Responsive design
- Form validation

## API Integration

All API calls are made to `/api/*` endpoints, which are:
- Proxied to the backend in development (via Vite)
- Proxied via Nginx in production (Docker)

API service example:

```typescript
// src/services/authApi.ts
export const authApi = {
  async login(credentials: LoginCredentials): Promise<AuthTokens> {
    const response = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
    });
    return response.json();
  }
};
```

## Environment Variables

For build-time configuration, create a `.env` file:

```env
VITE_API_URL=http://localhost:8000
```

Access in code:

```typescript
const apiUrl = import.meta.env.VITE_API_URL;
```

## Docker Deployment

The application uses a multi-stage Docker build:

1. **Builder stage**: Builds the React app with Node 20
2. **Production stage**: Serves static files with Nginx

### Build and run

```bash
docker build -t digitalockbox-gui .
docker run -p 3000:80 digitalockbox-gui
```

### Nginx configuration

The included `nginx.conf` handles:
- Serving static files
- SPA routing (all routes → index.html)
- API proxying to backend
- Asset caching
- Gzip compression

## Contributing

1. Follow the existing code style
2. Run `npm run lint` before committing
3. Ensure all TypeScript types are properly defined
4. Test on both development and production builds

## License

MIT
