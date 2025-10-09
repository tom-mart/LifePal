# LifePal File Management System

**Complete guide for user uploads, tool-generated files, and downloads**

---

## 📋 Overview

The file management system provides:
- ✅ User file uploads with storage quotas
- ✅ Tool-generated files (PDFs, audio, images)
- ✅ Tool-downloaded files (music, documents)
- ✅ Secure file sharing with public/private links
- ✅ Automatic cleanup of temporary files
- ✅ Storage quota management per user
- ✅ File associations with conversations, check-ins, and tools

---

## 🏗️ Architecture

### Storage Structure

```
media/
├── uploads/              # User uploads
│   └── {user_id}/
│       ├── receipt/
│       ├── document/
│       ├── image/
│       └── other/
├── tool_outputs/         # Tool-generated files
│   └── {user_id}/
│       ├── scan_receipt/
│       ├── download_music/
│       └── generate_pdf_report/
└── temp/                 # Temporary files (auto-cleanup after 24h)
    └── {user_id}/
```

### Database Models

#### UserFile
Stores all files (uploads and tool-generated):
- File metadata (name, size, MIME type, category)
- Source tracking (user upload, tool generated, tool downloaded)
- Tool association (tool name, execution ID)
- Conversation/check-in associations
- Temporary file management with expiration
- Processing status

#### FileShare
Shareable links for files:
- Public or private sharing
- Download limits
- Expiration dates
- Access tracking

#### StorageQuota
Per-user storage limits:
- Total quota (default: 1GB)
- Used storage tracking
- File count limits (default: 1000)
- Auto-recalculation

---

## 🚀 Quick Start

### 1. Run Migrations

```bash
# Local development
cd backend/src
python manage.py makemigrations files
python manage.py migrate

# Docker production
sudo docker exec lifepal-backend python manage.py makemigrations files
sudo docker exec lifepal-backend python manage.py migrate
```

### 2. Verify Installation

```bash
python manage.py shell
```

```python
from files.models import UserFile, StorageQuota
from django.contrib.auth.models import User

# Check models
print("UserFile model:", UserFile._meta.db_table)
print("StorageQuota model:", StorageQuota._meta.db_table)

# Create storage quota for a user
user = User.objects.first()
quota, created = StorageQuota.objects.get_or_create(user=user)
print(f"Quota: {quota.used_storage}/{quota.total_quota} bytes")
```

---

## 📡 API Endpoints

### Upload File
```http
POST /api/files/upload
Content-Type: multipart/form-data
Authorization: Bearer {token}

file: [binary]
category: receipt|document|image|audio|video|pdf|other
description: "My receipt from grocery store"
```

**Response:**
```json
{
  "id": "uuid",
  "original_filename": "receipt.jpg",
  "file_size": 245678,
  "mime_type": "image/jpeg",
  "category": "receipt",
  "file_url": "/media/uploads/user_id/receipt/uuid.jpg",
  "download_url": "/api/files/uuid/download",
  "created_at": "2025-10-08T19:00:00Z"
}
```

### List Files
```http
GET /api/files/list?category=receipt&limit=20&offset=0
Authorization: Bearer {token}
```

**Response:**
```json
{
  "files": [...],
  "total_count": 45,
  "used_storage": 52428800,
  "total_quota": 1073741824,
  "usage_percentage": 4.88
}
```

### Download File
```http
GET /api/files/{file_id}/download
Authorization: Bearer {token}
```

Returns file with appropriate headers for download.

### Update File Metadata
```http
PUT /api/files/{file_id}
Authorization: Bearer {token}

{
  "description": "Updated description",
  "tags": ["work", "important"],
  "category": "document"
}
```

### Delete File
```http
DELETE /api/files/{file_id}
Authorization: Bearer {token}
```

### Create Share Link
```http
POST /api/files/share
Authorization: Bearer {token}

{
  "file_id": "uuid",
  "is_public": true,
  "max_downloads": 10,
  "expires_in_hours": 24
}
```

**Response:**
```json
{
  "id": "uuid",
  "share_token": "abc123...",
  "share_url": "/api/files/shared/abc123...",
  "is_public": true,
  "download_count": 0,
  "max_downloads": 10,
  "expires_at": "2025-10-09T19:00:00Z"
}
```

### Download Shared File
```http
GET /api/files/shared/{share_token}
```

No authentication required for public shares.

### Get Storage Quota
```http
GET /api/files/quota
Authorization: Bearer {token}
```

**Response:**
```json
{
  "total_quota": 1073741824,
  "used_storage": 52428800,
  "available_storage": 1021313024,
  "usage_percentage": 4.88,
  "file_count": 45,
  "max_files": 1000
}
```

---

## 🔧 Using Files in Tools

### Method 1: Using ToolFileHelper (Recommended)

```python
#!/usr/bin/env python
import json, sys, os, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from files.utils import ToolFileHelper

def main():
    input_data = json.loads(sys.stdin.read())
    user = User.objects.get(id=input_data['user_id'])
    params = input_data['parameters']
    
    # Create helper
    helper = ToolFileHelper(
        user=user,
        tool_name='my_tool',
        tool_execution_id=params.get('execution_id')
    )
    
    # Generate some content
    pdf_content = generate_pdf()  # Your logic here
    
    # Save file from bytes
    user_file = helper.save_from_bytes(
        content=pdf_content,
        filename='report.pdf',
        category='pdf',
        mime_type='application/pdf',
        description='Generated report',
        metadata={'report_type': 'wellbeing'},
        is_temporary=False
    )
    
    # Return result
    print(json.dumps({
        'success': True,
        'file_id': str(user_file.id),
        'filename': user_file.original_filename,
        'download_url': user_file.download_url,
        'message': f'Report generated: {user_file.original_filename}'
    }))

if __name__ == '__main__':
    main()
```

### Method 2: Direct Model Usage

```python
from files.models import UserFile, StorageQuota
from django.core.files import File

# Check quota
quota, _ = StorageQuota.objects.get_or_create(user=user)
if quota.used_storage + file_size > quota.total_quota:
    raise Exception("Storage quota exceeded")

# Save file
with open('/path/to/file.pdf', 'rb') as f:
    user_file = UserFile.objects.create(
        user=user,
        file=File(f, name='report.pdf'),
        original_filename='report.pdf',
        file_size=file_size,
        mime_type='application/pdf',
        category='pdf',
        source='tool_generated',
        tool_name='my_tool'
    )

# Update quota
quota.used_storage += file_size
quota.file_count += 1
quota.save()
```

---

## 🛠️ Example Tools

### 1. Receipt Scanner Tool

**Tool Definition (Django Admin):**
- **Name**: `scan_receipt`
- **Category**: `information`
- **Execution Type**: `script`
- **Script Path**: `/app/tools/scripts/scan_receipt.py`
- **Parameters Schema**:
```json
{
  "type": "object",
  "properties": {
    "file_id": {
      "type": "string",
      "description": "ID of the uploaded receipt image"
    }
  },
  "required": ["file_id"]
}
```

**Usage Flow:**
1. User uploads receipt image via `/api/files/upload`
2. LLM calls `tool_retriever(intent_category='information')`
3. LLM calls `scan_receipt(file_id='uuid')`
4. Tool extracts: merchant, date, total, items
5. Updates file metadata with extracted data
6. Returns structured receipt data

### 2. Music Downloader Tool

**Tool Definition:**
- **Name**: `download_music`
- **Category**: `information`
- **Execution Type**: `script`
- **Script Path**: `/app/tools/scripts/download_music.py`
- **Parameters Schema**:
```json
{
  "type": "object",
  "properties": {
    "url": {
      "type": "string",
      "description": "YouTube or music URL to download"
    }
  },
  "required": ["url"]
}
```

**Usage Flow:**
1. User: "Download this song: https://youtube.com/watch?v=..."
2. LLM calls `tool_retriever(query='download music')`
3. LLM calls `download_music(url='...')`
4. Tool downloads audio using yt-dlp
5. Saves to user's storage
6. Returns file ID and download URL

### 3. PDF Report Generator Tool

**Tool Definition:**
- **Name**: `generate_pdf_report`
- **Category**: `information`
- **Execution Type**: `script`
- **Script Path**: `/app/tools/scripts/generate_pdf_report.py`
- **Parameters Schema**:
```json
{
  "type": "object",
  "properties": {
    "report_type": {
      "type": "string",
      "enum": ["wellbeing", "tasks", "summary"],
      "description": "Type of report to generate"
    },
    "days": {
      "type": "integer",
      "description": "Number of days to include (default: 30)"
    }
  },
  "required": ["report_type"]
}
```

**Usage Flow:**
1. User: "Generate a wellbeing report for the last 30 days"
2. LLM calls `tool_retriever(intent_category='information')`
3. LLM calls `generate_pdf_report(report_type='wellbeing', days=30)`
4. Tool queries check-ins and daily logs
5. Generates PDF with reportlab
6. Saves to user's storage
7. Returns download URL

---

## 🔄 Automatic Cleanup

### Celery Tasks (Configured in settings.py)

**Cleanup Expired Files** (every hour):
- Deletes files with `expires_at` <= now
- Updates storage quotas

**Cleanup Old Temporary Files** (every hour):
- Deletes temporary files older than 24 hours
- Even if no explicit expiration set

**Cleanup Expired Shares** (every hour):
- Deletes expired share links
- Deletes shares that exceeded max downloads

**Recalculate Storage Quotas** (daily at 2 AM):
- Recalculates actual storage usage
- Ensures quota accuracy

---

## 📊 Storage Quotas

### Default Limits
- **Storage**: 1GB per user
- **File Count**: 1000 files per user

### Adjusting Quotas

**Via Django Admin:**
1. Go to Files → Storage Quotas
2. Find user
3. Update `total_quota` and `max_files`

**Programmatically:**
```python
from files.models import StorageQuota

quota = user.storage_quota
quota.total_quota = 5 * 1024 * 1024 * 1024  # 5GB
quota.max_files = 5000
quota.save()
```

### Quota Enforcement
- Checked on every upload
- Checked by tools before saving files
- Returns error if exceeded
- User must delete files to free space

---

## 🔐 Security & Access Control

### File Access
- Users can only access their own files
- JWT authentication required for all endpoints
- Share links can be public or private
- Download tracking for shared files

### File Sharing
- **Public shares**: Accessible without authentication
- **Private shares**: Requires authentication + permission check
- **Expiration**: Time-based or download-count-based
- **Revocation**: Delete share to revoke access

---

## 🎨 Frontend Integration

### File Upload Component (Example)

```typescript
// components/FileUpload.tsx
import { useState } from 'react';
import { apiClient } from '@/lib/api';

export function FileUpload({ category = 'other', onUpload }) {
  const [uploading, setUploading] = useState(false);
  
  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    setUploading(true);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('category', category);
      
      const response = await apiClient.post('/api/files/upload', formData);
      
      onUpload?.(response);
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setUploading(false);
    }
  };
  
  return (
    <input
      type="file"
      onChange={handleUpload}
      disabled={uploading}
    />
  );
}
```

### File List Component (Example)

```typescript
// components/FileList.tsx
import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api';

export function FileList({ category }) {
  const [files, setFiles] = useState([]);
  const [quota, setQuota] = useState(null);
  
  useEffect(() => {
    loadFiles();
  }, [category]);
  
  const loadFiles = async () => {
    const data = await apiClient.get(`/api/files/list?category=${category}`);
    setFiles(data.files);
    setQuota({
      used: data.used_storage,
      total: data.total_quota,
      percentage: data.usage_percentage
    });
  };
  
  const downloadFile = (fileId: string) => {
    window.open(`/api/files/${fileId}/download`, '_blank');
  };
  
  return (
    <div>
      {/* Storage quota bar */}
      <div className="mb-4">
        <div className="text-sm">
          Storage: {(quota?.used / 1024 / 1024).toFixed(2)} MB / 
          {(quota?.total / 1024 / 1024).toFixed(2)} MB
        </div>
        <progress value={quota?.percentage} max="100" />
      </div>
      
      {/* File list */}
      {files.map(file => (
        <div key={file.id} className="border p-4 mb-2">
          <h3>{file.original_filename}</h3>
          <p>{file.description}</p>
          <button onClick={() => downloadFile(file.id)}>
            Download
          </button>
        </div>
      ))}
    </div>
  );
}
```

---

## 🔧 Tool Integration Examples

### Example 1: Receipt Scanner

**User Flow:**
1. User uploads receipt image
2. User: "Scan this receipt for me"
3. LLM calls `tool_retriever(query='scan receipt')`
4. LLM calls `scan_receipt(file_id='uuid')`
5. Tool extracts merchant, total, items
6. LLM: "I scanned your receipt from GROCERY STORE. Total: $12.40"

**Tool Definition (Add via Django Admin):**
```
Name: scan_receipt
Category: information
Description: Scan a receipt image and extract merchant, date, total, and items.
Use when user uploads a receipt and wants to extract information.

Execution Type: script
Script Path: /app/tools/scripts/scan_receipt.py
Parameters Schema:
{
  "type": "object",
  "properties": {
    "file_id": {"type": "string", "description": "ID of uploaded receipt image"}
  },
  "required": ["file_id"]
}
```

### Example 2: Music Downloader

**User Flow:**
1. User: "Download this song: https://youtube.com/watch?v=xyz"
2. LLM calls `tool_retriever(query='download music')`
3. LLM calls `download_music(url='...')`
4. Tool downloads audio, saves to storage
5. LLM: "Downloaded 'Song Title' by Artist (3.2 MB). [Download link]"

**Tool Definition:**
```
Name: download_music
Category: information
Description: Download audio from YouTube or other sources.
Use when user wants to download music or audio.

Execution Type: script
Script Path: /app/tools/scripts/download_music.py
Parameters Schema:
{
  "type": "object",
  "properties": {
    "url": {"type": "string", "description": "URL to download audio from"}
  },
  "required": ["url"]
}
```

### Example 3: PDF Report Generator

**User Flow:**
1. User: "Generate a wellbeing report for the last month"
2. LLM calls `tool_retriever(query='generate report')`
3. LLM calls `generate_pdf_report(report_type='wellbeing', days=30)`
4. Tool queries check-ins, generates PDF
5. LLM: "I've generated your wellbeing report covering 30 days. [Download PDF]"

**Tool Definition:**
```
Name: generate_pdf_report
Category: information
Description: Generate PDF reports from user data (wellbeing, tasks, summaries).
Use when user wants a downloadable report.

Execution Type: script
Script Path: /app/tools/scripts/generate_pdf_report.py
Parameters Schema:
{
  "type": "object",
  "properties": {
    "report_type": {
      "type": "string",
      "enum": ["wellbeing", "tasks", "summary"],
      "description": "Type of report"
    },
    "days": {"type": "integer", "description": "Number of days to include"}
  },
  "required": ["report_type"]
}
```

---

## 🧪 Testing

### Test File Upload

```bash
curl -X POST http://localhost:8000/api/files/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@receipt.jpg" \
  -F "category=receipt" \
  -F "description=Grocery receipt"
```

### Test Tool Execution

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from llm_tools import get_tool_registry

user = User.objects.first()
registry = get_tool_registry()

# Test scan_receipt tool
result = registry.execute_tool(
    'scan_receipt',
    {'file_id': 'your-file-uuid'},
    user
)
print(result)
```

---

## 📝 Adding New File-Based Tools

### Step 1: Create Tool Script

```python
#!/usr/bin/env python
import json, sys, os, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from files.utils import ToolFileHelper

def main():
    input_data = json.loads(sys.stdin.read())
    user = User.objects.get(id=input_data['user_id'])
    params = input_data['parameters']
    
    # Create helper
    helper = ToolFileHelper(user=user, tool_name='my_new_tool')
    
    # Your tool logic here
    # ...
    
    # Save result file
    user_file = helper.save_from_bytes(
        content=result_bytes,
        filename='output.pdf',
        category='pdf',
        description='Tool output'
    )
    
    print(json.dumps({
        'success': True,
        'file_id': str(user_file.id),
        'download_url': user_file.download_url
    }))

if __name__ == '__main__':
    main()
```

### Step 2: Add Tool via Django Admin

1. Go to: http://localhost:8000/admin/llm_tools/tooldefinition/add/
2. Fill in tool details
3. Set execution_type to `script`
4. Set script_path to your script
5. Define parameters schema
6. Save

### Step 3: Done!

Tool is immediately available to LLM via `tool_retriever()`.

---

## 🔍 Troubleshooting

### File Upload Fails

**Check quota:**
```python
from files.models import StorageQuota

quota = user.storage_quota
print(f"Used: {quota.used_storage}/{quota.total_quota}")
print(f"Files: {quota.file_count}/{quota.max_files}")
```

**Recalculate if incorrect:**
```python
quota.recalculate_usage()
```

### Tool Can't Save File

**Check permissions:**
```bash
# Ensure media directory is writable
sudo chown -R www-data:www-data /app/media  # Docker
chmod -R 755 /app/media
```

**Check quota in tool:**
```python
from files.utils import ToolFileHelper

helper = ToolFileHelper(user=user, tool_name='my_tool')
try:
    helper.check_quota(file_size)
except Exception as e:
    print(f"Quota error: {e}")
```

### Files Not Cleaning Up

**Check Celery Beat is running:**
```bash
# Docker
sudo docker-compose logs celery_beat

# Local
celery -A core beat --loglevel=info
```

**Manually trigger cleanup:**
```python
from files.tasks import cleanup_expired_files

result = cleanup_expired_files()
print(result)
```

---

## 📈 Monitoring

### Check Storage Usage

```python
from files.models import StorageQuota
from django.db.models import Sum

# Total storage used across all users
total_used = StorageQuota.objects.aggregate(Sum('used_storage'))
print(f"Total storage: {total_used['used_storage__sum']} bytes")

# Top users by storage
top_users = StorageQuota.objects.order_by('-used_storage')[:10]
for quota in top_users:
    print(f"{quota.user.username}: {quota.used_storage} bytes")
```

### Check File Statistics

```python
from files.models import UserFile
from django.db.models import Count

# Files by category
stats = UserFile.objects.values('category').annotate(count=Count('id'))
for stat in stats:
    print(f"{stat['category']}: {stat['count']} files")

# Files by source
stats = UserFile.objects.values('source').annotate(count=Count('id'))
for stat in stats:
    print(f"{stat['source']}: {stat['count']} files")
```

---

## 🚀 Next Steps

1. **Run migrations**: `python manage.py migrate`
2. **Add tools via Django admin**: Create tool definitions for your use cases
3. **Install dependencies**: `pip install pytesseract yt-dlp reportlab` (for production tools)
4. **Test file upload**: Use API or create frontend component
5. **Test tool execution**: Upload file, call tool via LLM
6. **Monitor storage**: Check quotas and usage regularly

---

## 📚 Related Documentation

- **[Tool System Guide](TOOL_SYSTEM_GUIDE.md)** - How to create and manage tools
- **[API Documentation](http://localhost:8000/api/docs)** - Interactive API docs
- **[Django Admin](http://localhost:8000/admin)** - Manage files and quotas

---

**Last Updated:** October 8, 2025
