# 🎨 Andalus Downloader Frontend Development Prompt

## 🎯 **Project Overview**

Create a modern, responsive frontend for **Andalus Downloader** - a universal media downloader that supports YouTube, Vimeo, SoundCloud, and other platforms. The frontend should be deployed on **Vercel** and connect to the backend API.

## 🌐 **Backend API Details**

### **API Base URL:**
```
Production: https://andalus-downloader.ngrok.io
Development: http://localhost:8000
```

### **Key Features to Implement:**
- ✅ URL validation and platform detection
- ✅ Quality/format selection (1080p, 720p, 480p, audio-only)
- ✅ Real-time download progress tracking
- ✅ Download queue management
- ✅ Batch downloads and playlist support
- ✅ Modern, responsive UI with dark/light theme
- ✅ WebSocket integration for live updates

## 🎨 **Design Requirements**

### **UI/UX Guidelines:**
- **Modern Design**: Clean, minimalist interface with smooth animations
- **Responsive**: Mobile-first design, works on all devices
- **Dark/Light Theme**: Toggle between themes with system preference detection
- **Accessibility**: WCAG 2.1 compliant, keyboard navigation, screen reader support
- **Performance**: Fast loading, optimized images, lazy loading

### **Color Scheme:**
```css
/* Primary Colors */
--primary: #3B82F6;      /* Blue */
--primary-dark: #1E40AF;
--secondary: #10B981;    /* Green */
--accent: #F59E0B;       /* Amber */

/* Dark Theme */
--bg-dark: #0F172A;      /* Slate 900 */
--surface-dark: #1E293B; /* Slate 800 */
--text-dark: #F8FAFC;    /* Slate 50 */

/* Light Theme */
--bg-light: #FFFFFF;
--surface-light: #F8FAFC; /* Slate 50 */
--text-light: #0F172A;   /* Slate 900 */
```

## 📱 **Page Structure**

### **1. Home Page (`/`)**
- **Hero Section**: App title, description, main download input
- **Features Grid**: Supported platforms, quality options, batch downloads
- **Recent Downloads**: Quick access to recent downloads
- **Statistics**: Total downloads, supported platforms count

### **2. Download Page (`/download`)**
- **URL Input**: Large input field with validation
- **Platform Detection**: Auto-detect and show platform icon
- **Quality Selection**: Dropdown with available qualities
- **Format Selection**: Video (MP4, WebM, AVI) or Audio (MP3, WAV, FLAC)
- **Advanced Options**: Custom filename, output folder selection

### **3. Queue Page (`/queue`)**
- **Active Downloads**: Progress bars, speed, ETA
- **Queued Downloads**: Pending downloads list
- **Completed Downloads**: Download history with file links
- **Batch Operations**: Pause all, resume all, clear completed

### **4. Settings Page (`/settings`)**
- **Theme Toggle**: Dark/light mode
- **Default Quality**: Set preferred download quality
- **Default Format**: Set preferred format
- **API Configuration**: Backend URL settings
- **Download Location**: Default download folder

## 🔧 **Technical Stack**

### **Recommended Technologies:**
- **Framework**: Next.js 14+ (App Router) or React 18+ with Vite
- **Styling**: Tailwind CSS + Headless UI or Shadcn/ui
- **State Management**: Zustand or React Query (TanStack Query)
- **Icons**: Lucide React or Heroicons
- **Animations**: Framer Motion
- **Forms**: React Hook Form + Zod validation
- **WebSocket**: Native WebSocket API or Socket.io-client

### **Project Structure:**
```
src/
├── app/                 # Next.js App Router pages
│   ├── page.tsx        # Home page
│   ├── download/       # Download page
│   ├── queue/          # Queue management
│   └── settings/       # Settings page
├── components/         # Reusable components
│   ├── ui/            # Base UI components
│   ├── download/      # Download-related components
│   └── layout/        # Layout components
├── lib/               # Utilities and configurations
│   ├── api.ts         # API client
│   ├── websocket.ts   # WebSocket manager
│   └── utils.ts       # Helper functions
├── hooks/             # Custom React hooks
├── stores/            # State management
└── types/             # TypeScript definitions
```

## 🔌 **API Integration**

### **API Client Configuration:**
```typescript
// lib/api.ts
const API_CONFIG = {
  BASE_URL: process.env.NODE_ENV === 'development' 
    ? 'http://localhost:8000' 
    : 'https://andalus-downloader.ngrok.io',
  WS_URL: process.env.NODE_ENV === 'development'
    ? 'ws://localhost:8000'
    : 'wss://andalus-downloader.ngrok.io'
};

class ApiClient {
  private baseURL = API_CONFIG.BASE_URL;

  async health() {
    const response = await fetch(`${this.baseURL}/health`);
    return response.json();
  }

  async validateUrl(url: string) {
    const response = await fetch(`${this.baseURL}/api/v1/validate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });
    return response.json();
  }

  async createDownload(url: string, quality: string, format: string) {
    const response = await fetch(`${this.baseURL}/api/v1/downloads`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, quality, format })
    });
    return response.json();
  }

  async getDownloads(status?: string, page = 1) {
    const params = new URLSearchParams({ page: page.toString() });
    if (status) params.append('status', status);
    
    const response = await fetch(`${this.baseURL}/api/v1/downloads?${params}`);
    return response.json();
  }

  connectWebSocket() {
    return new WebSocket(`${API_CONFIG.WS_URL}/ws/downloads`);
  }
}

export const api = new ApiClient();
```

### **WebSocket Integration:**
```typescript
// hooks/useWebSocket.ts
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

export function useWebSocket() {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const ws = api.connectWebSocket();
    
    ws.onopen = () => {
      setIsConnected(true);
      setSocket(ws);
    };
    
    ws.onclose = () => {
      setIsConnected(false);
      setSocket(null);
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      // Handle real-time updates
      handleWebSocketMessage(data);
    };

    return () => {
      ws.close();
    };
  }, []);

  return { socket, isConnected };
}
```

## 🎯 **Key Components to Build**

### **1. DownloadForm Component**
```typescript
interface DownloadFormProps {
  onSubmit: (data: DownloadRequest) => void;
  isLoading?: boolean;
}

// Features:
// - URL input with validation
// - Platform auto-detection
// - Quality/format selection
// - Advanced options toggle
```

### **2. DownloadCard Component**
```typescript
interface DownloadCardProps {
  download: Download;
  onPause: () => void;
  onResume: () => void;
  onCancel: () => void;
}

// Features:
// - Progress bar with percentage
// - Download speed and ETA
// - Thumbnail preview
// - Control buttons (pause/resume/cancel)
```

### **3. QueueManager Component**
```typescript
// Features:
// - Real-time download list
// - Filter by status (active, completed, failed)
// - Batch operations
// - Search and sort functionality
```

### **4. PlatformIcon Component**
```typescript
interface PlatformIconProps {
  platform: 'youtube' | 'vimeo' | 'soundcloud' | 'dailymotion' | 'generic';
  size?: 'sm' | 'md' | 'lg';
}

// Features:
// - Platform-specific icons
// - Consistent sizing
// - Accessibility labels
```

## 📊 **State Management**

### **Download Store (Zustand):**
```typescript
interface DownloadStore {
  downloads: Download[];
  activeDownloads: Download[];
  completedDownloads: Download[];
  
  // Actions
  addDownload: (download: Download) => void;
  updateDownload: (id: string, updates: Partial<Download>) => void;
  removeDownload: (id: string) => void;
  clearCompleted: () => void;
  
  // WebSocket handlers
  handleProgressUpdate: (data: ProgressUpdate) => void;
  handleStatusUpdate: (data: StatusUpdate) => void;
}
```

## 🎨 **UI Components Examples**

### **Download Progress Bar:**
```tsx
function ProgressBar({ progress, status }: { progress: number; status: string }) {
  return (
    <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
      <div 
        className={`h-2.5 rounded-full transition-all duration-300 ${
          status === 'active' ? 'bg-blue-600' : 
          status === 'completed' ? 'bg-green-600' : 
          'bg-gray-400'
        }`}
        style={{ width: `${progress}%` }}
      />
    </div>
  );
}
```

### **Platform Badge:**
```tsx
function PlatformBadge({ platform }: { platform: string }) {
  const colors = {
    youtube: 'bg-red-100 text-red-800',
    vimeo: 'bg-blue-100 text-blue-800',
    soundcloud: 'bg-orange-100 text-orange-800',
  };

  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[platform]}`}>
      {platform}
    </span>
  );
}
```

## 🚀 **Deployment Configuration**

### **Vercel Environment Variables:**
```bash
NEXT_PUBLIC_API_URL=https://andalus-downloader.ngrok.io
NEXT_PUBLIC_WS_URL=wss://andalus-downloader.ngrok.io
```

### **vercel.json:**
```json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "functions": {
    "app/api/**/*.ts": {
      "maxDuration": 30
    }
  }
}
```

## 📱 **Mobile Responsiveness**

### **Breakpoints:**
- **Mobile**: 320px - 768px
- **Tablet**: 768px - 1024px  
- **Desktop**: 1024px+

### **Mobile-First Features:**
- Touch-friendly buttons (min 44px)
- Swipe gestures for download cards
- Bottom sheet for mobile options
- Optimized keyboard input
- Reduced motion for accessibility

## 🔒 **Error Handling**

### **Error Boundaries:**
```tsx
function DownloadErrorBoundary({ children }: { children: React.ReactNode }) {
  return (
    <ErrorBoundary
      fallback={<ErrorFallback />}
      onError={(error) => console.error('Download error:', error)}
    >
      {children}
    </ErrorBoundary>
  );
}
```

### **API Error Handling:**
```typescript
async function handleApiError(response: Response) {
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'API request failed');
  }
  return response.json();
}
```

## 🎯 **Performance Optimization**

- **Code Splitting**: Lazy load pages and components
- **Image Optimization**: Next.js Image component with WebP
- **Bundle Analysis**: Regular bundle size monitoring
- **Caching**: Implement proper caching strategies
- **Virtualization**: For large download lists

## 🧪 **Testing Strategy**

- **Unit Tests**: Jest + React Testing Library
- **Integration Tests**: API integration tests
- **E2E Tests**: Playwright for critical user flows
- **Accessibility Tests**: axe-core integration

## 📚 **Documentation**

Create comprehensive documentation including:
- **Setup Instructions**: Local development setup
- **API Integration**: How to connect to backend
- **Component Library**: Storybook documentation
- **Deployment Guide**: Vercel deployment steps

---

## 🎉 **Success Criteria**

The frontend should successfully:
1. ✅ Connect to the backend API at `https://andalus-downloader.ngrok.io`
2. ✅ Validate URLs and detect platforms
3. ✅ Create downloads with quality/format selection
4. ✅ Display real-time progress updates via WebSocket
5. ✅ Manage download queue (pause, resume, cancel)
6. ✅ Work seamlessly on mobile and desktop
7. ✅ Deploy successfully to Vercel
8. ✅ Handle errors gracefully
9. ✅ Provide excellent user experience

**Your Andalus Downloader frontend will be a modern, feature-rich application that provides an excellent user experience for downloading media from various platforms! 🚀**
