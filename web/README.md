# ReWOO Streaming Web Interface

Một giao diện web React với Tailwind CSS để tương tác với ReWOO API thông qua streaming real-time.

## Tính năng

- ✅ **Giao diện chat real-time**: Chat interface để gửi câu hỏi và nhận phản hồi
- ✅ **Streaming response**: Hiển thị kết quả streaming từ API với media_type="text/event-stream"
- ✅ **Markdown support**: Render markdown format với syntax highlighting
- ✅ **Responsive design**: Thiết kế responsive với Tailwind CSS
- ✅ **Real-time updates**: Cập nhật real-time không cần refresh

## Cài đặt và chạy

### 1. Cài đặt Node.js (nếu chưa có)
```bash
# Tự động cài đặt Node.js qua Homebrew
./setup_nodejs.sh

# Hoặc cài đặt thủ công
brew install node
```

### 2. Cài đặt dependencies
```bash
cd web
npm install
```

### 3. Chạy ứng dụng
```bash
# Sử dụng Vite dev server
npm run dev
```

Hoặc sử dụng script:
```bash
./start_web.sh
```

### 4. Truy cập ứng dụng
Mở trình duyệt và truy cập: `http://localhost:3000`

## Cấu trúc dự án

```
web/
├── public/
│   └── index.html          # HTML template
├── src/
│   ├── components/
│   │   └── StreamingChat.js # Component xử lý streaming và markdown
│   ├── App.js              # Component chính
│   ├── index.js            # Entry point
│   └── index.css           # Styles với Tailwind
├── package.json            # Dependencies
├── tailwind.config.js      # Tailwind configuration
├── postcss.config.js       # PostCSS configuration
└── start_web.sh            # Script chạy ứng dụng
```

## API Integration

Ứng dụng kết nối với ReWOO API endpoint:
- **URL**: `http://localhost:8000/agent/tasks/execute-stream`
- **Method**: POST
- **Content-Type**: `application/json`
- **Response**: `text/event-stream`

### Request format:
```json
{
  "description": "Your question here",
  "task_type": "RESEARCH",
  "priority": "MEDIUM",
  "streaming": true
}
```

## Cách sử dụng

1. **Khởi động ReWOO API server** (port 8000)
2. **Khởi động web application** (port 3000)  
3. **Mở trình duyệt** và truy cập `http://localhost:3000`
4. **Nhập câu hỏi** vào ô text và nhấn Send
5. **Xem kết quả streaming** real-time với markdown formatting

## Tính năng chính

### 1. Chat Interface
- Input field để nhập câu hỏi
- Send button để gửi request
- Chat history với user/bot messages
- Timestamp cho mỗi message

### 2. Streaming Response
- Hiển thị response real-time khi API streaming
- Loading indicators khi đang xử lý
- Error handling khi có lỗi xảy ra

### 3. Markdown Rendering
- Support full markdown syntax
- Code highlighting
- Tables, lists, links
- Custom styling với Tailwind CSS

### 4. UI/UX Features
- Responsive design
- Auto-scroll to latest message
- Typing indicators
- Clean, modern interface
- Custom scrollbar styling

## Dependencies

### Production
- `react` ^18.2.0
- `react-dom` ^18.2.0
- `react-markdown` ^9.0.1
- `remark-gfm` ^4.0.0
- `lucide-react` ^0.294.0

### Development
- `tailwindcss` ^3.3.0
- `autoprefixer` ^10.4.16
- `postcss` ^8.4.31
- `react-scripts` 5.0.1

## Customization

### Styling
- Chỉnh sửa `src/index.css` để thay đổi custom styles
- Chỉnh sửa `tailwind.config.js` để thêm custom Tailwind classes

### API Endpoint
- Thay đổi API URL trong `src/App.js` nếu cần
- Customize request format trong `handleSendMessage` function

### Streaming Logic
- Chỉnh sửa `StreamingChat.js` để customize cách hiển thị streaming text
- Thay đổi typing speed trong `useEffect` với `setInterval`