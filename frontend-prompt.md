# Andalus Downloader - Frontend Prompt for Lovable.dev

## 🎯 Project Overview
Create a modern, intuitive Next.js frontend for **Andalus Downloader** - a universal media downloader that supports YouTube, Vimeo, SoundCloud, and more. The frontend should connect to our existing FastAPI backend and provide an exceptional user experience with a revolutionary "Paste" button onboarding flow.

## 🎨 Design Inspiration
**Primary Inspiration**: https://lovable.dev/projects/749331af-3ddb-406d-9f8e-d5514ba21c2f
- **Glossy, clean UI** with smooth animations
- **Modern glassmorphism** effects
- **Smooth transitions** and micro-interactions
- **Premium feel** with elegant typography
- **Smart use of gradients** and shadows

## 🚀 Revolutionary "Paste" Button Strategy

### 1. **Hero Section with Paste Button**
Instead of traditional input fields, create a **stunning hero section** with:
- **Large, prominent "Paste" button** as the main CTA
- **Animated background** with floating media icons
- **Elegant typography**: "Download from anywhere on the internet"
- **Subtle animations** that draw attention to the Paste button
- **Clean, minimal design** - no cluttered inputs visible initially

### 2. **Smart Onboarding Flow (Triggered by Paste Button)**
When user clicks "Paste" button, trigger this **smooth animated sequence**:

#### **Step 1: Paste Link**
- **Slide in elegant text area** with glassmorphism effect
- **Auto-focus** and **auto-paste** from clipboard if available
- **Real-time validation** with smooth color transitions
- **Platform detection** with animated platform icon appearing
- **Smooth "Next" button** slides in when valid URL detected

#### **Step 2: Processing & Analysis**
- **Beautiful loading animation** with progress indicators
- **"Analyzing your content..."** with animated dots
- **Platform-specific animations** (YouTube red, Vimeo blue, etc.)
- **Metadata preview** slides in smoothly when ready

#### **Step 3: Format Selection Branch**
**If Video Content Detected:**
- **"Video" card** slides in from left with video icon
- **Format options** (MP4, WebM, AVI) with animated previews
- **Quality selector** with smooth slider (4K → 1080p → 720p → 480p)
- **File size estimates** update in real-time

**If Audio Content Detected:**
- **"Audio" card** slides in from right with audio icon  
- **Format options** (MP3, WAV, FLAC, AAC) with waveform animations
- **Quality selector** with bitrate options (320kbps → 192kbps → 128kbps)

#### **Step 4: Ready to Download**
- **Download button** morphs and grows with satisfying animation
- **Progress preview** shows estimated download time
- **One-click download** with beautiful success animation

### 3. **Real-time Download Management**
- **Live Progress Cards**: Beautiful progress bars with:
  - Thumbnail, title, and platform icon
  - Download speed, ETA, and percentage
  - Pause/resume/cancel controls
- **Queue Management**: Drag-and-drop reordering of downloads
- **Batch Downloads**: Multi-URL input with playlist detection
- **Download History**: Recent downloads with re-download options

### 4. **Premium UI/UX Design System**
Inspired by the Lovable reference project, create a **glossy, premium interface**:

#### **Visual Design**
- **Glassmorphism effects** with backdrop blur and transparency
- **Smooth gradients** and subtle shadows for depth
- **Premium typography** with perfect spacing and hierarchy
- **Micro-interactions** on every element (hover, click, focus)
- **Smooth page transitions** with elegant easing curves

#### **Color Palette** (Inspired by reference)
- **Primary Gradient**: Deep purple to blue (#6366f1 → #3b82f6)
- **Secondary**: Emerald green (#10b981) for success states
- **Accent**: Warm orange (#f59e0b) for highlights
- **Background**: Clean whites with subtle gradients
- **Dark Mode**: Rich dark grays (#0f172a) with purple accents

#### **Animation Strategy**
- **Entrance animations**: Slide up with fade and scale
- **Loading states**: Smooth skeleton screens and spinners
- **Success animations**: Satisfying check marks and confetti
- **Hover effects**: Subtle lift and glow on interactive elements
- **Page transitions**: Smooth fade and slide combinations

## 🔌 Backend Integration

### API Endpoints to Connect:
```javascript
// Base URL: http://localhost:8000/api/v1
POST /downloads          // Create download
GET /downloads           // List downloads
PUT /downloads/{id}/pause // Pause download
DELETE /downloads/{id}   // Cancel download
POST /validate          // Validate URL
GET /metadata           // Get video info
WebSocket /ws/downloads // Real-time updates
```
### WebSocket Integration:
- Connect to `ws://localhost:8000/ws/downloads` for real-time progress
- Show live download progress, status changes, and completion notifications
- Handle connection errors gracefully with retry logic

## 🎭 Key Components to Build

### 1. **PasteButton Component**
```jsx
// Hero paste button with:
// - Magnetic hover effect
// - Gradient background animation
// - Pulse effect to draw attention
// - Smooth click animation
// - Clipboard auto-detection
```

### 2. **OnboardingModal Component**
```jsx
// Full-screen modal with steps:
// - Slide-in text area (Step 1)
// - Processing animation (Step 2)  
// - Format selection cards (Step 3)
// - Download ready state (Step 4)
// - Smooth step transitions
```

### 3. **FormatSelectionCards Component**
```jsx
// Animated format cards with:
// - Video/Audio branching logic
// - Smooth card animations
// - Quality sliders with real-time updates
// - File size estimates
// - Format preview animations
```

### 4. **ProcessingAnimation Component**
```jsx
// Beautiful loading states with:
// - Platform-specific colors
// - Smooth progress indicators
// - Metadata extraction feedback
// - Success state transitions
```

### 5. **DownloadProgress Component**
```jsx
// Premium progress tracking with:
// - Glassmorphism progress bars
// - Real-time speed/ETA updates
// - Smooth percentage animations
// - Success confetti animation
```

## 🌟 Innovative Features

### 1. **Magnetic Paste Button**
- **Hover magnetism**: Button slightly moves toward cursor
- **Clipboard detection**: Auto-highlight when URL is copied
- **Breathing animation**: Subtle pulse to indicate interactivity
- **Smart suggestions**: Show recent platform icons around button

### 2. **Contextual Animations**
- **Platform-aware colors**: YouTube red, Vimeo blue, SoundCloud orange
- **Content-aware transitions**: Different animations for video vs audio
- **Smart loading states**: Platform-specific loading animations
- **Success celebrations**: Confetti for completed downloads

### 3. **Intelligent UX**
- **Auto-format detection**: Suggest best format based on content
- **Smart quality recommendations**: Optimize for file size vs quality
- **One-click retry**: Easy retry for failed downloads
- **Batch processing**: Handle multiple URLs intelligently
- Offline capability for managing existing downloads
- Push notifications for download completion

### 4. **Keyboard Shortcuts**
- Ctrl+V: Quick paste and validate
- Space: Pause/resume current download
- Ctrl+D: Start download
- Esc: Cancel current operation

## 📱 Responsive Design

### Mobile-First Approach:
- **Mobile**: Single column, large touch targets, swipe gestures
- **Tablet**: Two-column layout, optimized for touch
- **Desktop**: Multi-column with sidebar, keyboard shortcuts

### Key Breakpoints:
- Mobile: 320px - 768px
- Tablet: 768px - 1024px
- Desktop: 1024px+

## 🎭 Animations & Interactions

### Micro-interactions:
- URL input: Smooth focus states and validation feedback
- Download button: Satisfying click animation with ripple effect
- Progress bars: Smooth animated progress with color transitions
- Cards: Hover effects with subtle shadows and scaling

### Page Transitions:
- Smooth page transitions between onboarding and main app
- Staggered animations for download cards
- Loading states with skeleton screens

## 🔧 Technical Requirements

### Framework & Tools:
- **Next.js 14** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **React Query** for API state management
- **Zustand** for global state
- **React Hook Form** for form handling

### Performance:
- Lazy loading for components
- Image optimization for thumbnails
- Code splitting for better loading
- Service worker for PWA features

## 🎯 Success Metrics

### User Experience Goals:
- **Time to First Download**: < 30 seconds from landing
- **Onboarding Completion**: > 80% of users complete tutorial
- **User Retention**: Users return to download more content
- **Error Recovery**: Clear error messages with actionable solutions

### Technical Goals:
- **Performance**: Lighthouse score > 90
- **Accessibility**: WCAG 2.1 AA compliance
- **Mobile Experience**: Smooth performance on mobile devices
- **Browser Support**: Modern browsers (Chrome, Firefox, Safari, Edge)

## 💡 Implementation Priority

### Phase 1 (MVP):
1. Basic URL input and validation
2. Simple download interface
3. Real-time progress tracking
4. Basic onboarding flow

### Phase 2 (Enhanced):
1. Advanced onboarding with animations
2. Drag & drop functionality
3. Batch downloads
4. Download history

### Phase 3 (Premium):
1. PWA features
2. Advanced animations
3. Keyboard shortcuts
4. Smart paste detection

## 🎯 Implementation Priority

### Phase 1 (Core Experience):
1. **Hero section with magnetic Paste button**
2. **Onboarding modal with 4-step flow**
3. **URL validation and platform detection**
4. **Basic format selection (Video/Audio branching)**

### Phase 2 (Enhanced UX):
1. **Advanced animations and transitions**
2. **Real-time progress tracking**
3. **Download queue management**
4. **Success celebrations and feedback**

### Phase 3 (Premium Features):
1. **Drag & drop functionality**
2. **Keyboard shortcuts**
3. **PWA capabilities**
4. **Advanced customization options**

## 🎨 Animation Specifications

### **Paste Button Animations**
- **Idle state**: Subtle breathing (scale 1.0 → 1.02 → 1.0, 3s duration)
- **Hover state**: Magnetic pull toward cursor + glow effect
- **Click state**: Scale down (0.95) then bounce back (1.05 → 1.0)
- **Clipboard detected**: Gentle highlight pulse with success color

### **Modal Transitions**
- **Entry**: Fade in background + slide up modal (0.4s ease-out)
- **Step transitions**: Slide left/right with fade (0.3s ease-in-out)
- **Exit**: Scale down + fade out (0.3s ease-in)

### **Format Card Animations**
- **Video card**: Slide in from left with video icon bounce
- **Audio card**: Slide in from right with waveform animation
- **Selection**: Card lift + glow + checkmark animation

---

**Goal**: Create a **revolutionary download experience** that feels magical and effortless. The "Paste" button should be the hero of the interface, making downloading as simple as one click. Every animation should feel premium and satisfying, inspired by the glossy, smooth aesthetic of the reference project.
