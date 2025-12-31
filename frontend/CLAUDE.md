# Frontend Development Rules

## Technology Stack
- **Framework**: Next.js 15+ (App Router)
- **Language**: TypeScript
- **Auth**: Better Auth with JWT plugin
- **Styling**: Tailwind CSS

## Environment Variables Required
- `DATABASE_URL`: Neon PostgreSQL connection string (for Better Auth)
- `BETTER_AUTH_SECRET`: JWT signing secret (must match backend)
- `NEXT_PUBLIC_API_URL`: Backend API URL (http://localhost:8000)

## Project Structure
```
frontend/
├── app/
│   ├── layout.tsx       # Root layout with AuthProvider
│   ├── page.tsx         # Landing page
│   ├── signin/page.tsx  # Sign-in form
│   ├── signup/page.tsx  # Sign-up form
│   ├── dashboard/page.tsx # Task management
│   └── api/auth/[...all]/route.ts # Better Auth API
├── components/
│   ├── auth-provider.tsx
│   ├── task-list.tsx
│   ├── task-item.tsx
│   ├── task-form.tsx
│   └── empty-state.tsx
├── lib/
│   ├── auth.ts          # Better Auth config
│   └── api.ts           # Centralized API client
├── package.json
└── .env.local           # Environment variables (not in git)
```

## Auth Rules
- Better Auth handles session management
- JWT token attached to all API requests via lib/api.ts
- 401 response triggers redirect to /signin
- User ID from session, never from URL

## API Client Rules
- All backend calls go through lib/api.ts
- Include Authorization: Bearer {token} on all requests
- Handle error responses (401, 403, 404, 500)
- Type-safe request/response interfaces

## Component Rules
- Use 'use client' for interactive components
- Server components for static content
- Mobile-first responsive design with Tailwind
- Minimum touch target size: 44px
