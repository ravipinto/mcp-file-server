# n8n JSON Body Troubleshooting

## Problem Identified
Health check works, but file operations fail with "request is invalid or could not be processed by the service"

## Root Cause
n8n's JSON body formatting may not be compatible with the expected format for the `/file-operation` endpoint.

## Solutions

### Solution 1: Use Individual Endpoints with Query Parameters (Recommended)

Instead of using `/file-operation` with JSON body, use the individual endpoints with query parameters:

**Write File:**
```
Method: POST
URL: http://192.168.0.116:8000/write-file
Query Parameters:
  - path: /tmp/your_file.txt
  - content: Your content here
```

**Read File:**
```
Method: POST
URL: http://192.168.0.116:8000/read-file
Query Parameters:
  - path: /tmp/your_file.txt
```

### Solution 2: Fixed n8n Workflow Template

Import `n8n_workflow_simple.json` which uses query parameters:

1. **Manual Trigger** node
2. **Health Check** (GET to `/health`)
3. **Write File** (POST to `/write-file` with query params)
4. **Read File** (POST to `/read-file` with query params)

### Solution 3: JSON Body Alternative (if needed)

If you must use JSON bodies, try this format in n8n:

**In HTTP Request node:**
- Method: POST
- URL: `http://192.168.0.116:8000/file-operation`
- Content Type: JSON
- Use "JSON Parameters" instead of raw body:
  - operation: write_file
  - path: /tmp/test.txt
  - content: Your content

## Available Endpoints

| Endpoint | Method | Parameters | Purpose |
|----------|--------|------------|---------|
| `/health` | GET | None | Health check |
| `/tools` | GET | None | List available tools |
| `/file-operation` | POST | JSON body | General endpoint (problematic) |
| `/write-file` | POST | path, content (query) | Write file (working) |
| `/read-file` | POST | path (query) | Read file (working) |
| `/list-directory` | POST | path (query) | List directory |
| `/create-directory` | POST | path (query) | Create directory |
| `/delete-file` | POST | path (query) | Delete file |

## Testing Your Fix

**Test write file:**
```bash
curl -X POST "http://192.168.0.116:8000/write-file?path=/tmp/test.txt&content=Hello%20World"
```

**Test read file:**
```bash
curl -X POST "http://192.168.0.116:8000/read-file?path=/tmp/test.txt"
```

## Why This Happens

n8n's JSON formatting in HTTP Request nodes can sometimes add extra formatting or encoding that doesn't match the expected Pydantic model format. Query parameters are more reliable and simpler for n8n to handle.

## Next Steps

1. **Import the simple workflow**: Use `n8n_workflow_simple.json`
2. **Test each step**: Start with health check, then write, then read
3. **Build from there**: Add more complex operations as needed

The query parameter approach is more reliable for n8n integration!