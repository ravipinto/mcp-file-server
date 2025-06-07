# n8n Integration Guide for MCP File Server

This guide shows you how to integrate your MCP file server with n8n to create powerful AI workflows with file system capabilities.

## Prerequisites

1. **n8n installed** (local or cloud)
2. **MCP file server running** (your current setup)
3. **HTTP API server** (provided in this guide)

## Setup Steps

### Step 1: Start the HTTP API Server

The MCP file server communicates via stdio, but n8n needs HTTP endpoints. We've created a FastAPI wrapper:

```bash
# Start the HTTP API server
uv run python n8n_server.py
```

This will start a server at `http://localhost:8000` with these endpoints:
- `GET /health` - Health check
- `GET /tools` - List available tools
- `POST /file-operation` - Execute any file operation
- Individual endpoints: `/read-file`, `/write-file`, etc.

### Step 2: Test the API

```bash
# Test health
curl http://localhost:8000/health

# List available tools
curl http://localhost:8000/tools

# Test file operation
curl -X POST "http://localhost:8000/write-file" \
  -H "Content-Type: application/json" \
  -d '{"path": "/tmp/n8n_test.txt", "content": "Hello from n8n!"}'
```

## n8n Integration Methods

### Method 1: Using HTTP Request Node (Simple)

This is the simplest approach for basic file operations.

**Workflow Example: File Processing Pipeline**

1. **Trigger Node** - Manual trigger or webhook
2. **HTTP Request Node** - Call your file operations
3. **Function Node** - Process the response
4. **Conditional Node** - Handle errors

**HTTP Request Node Configuration:**
```json
{
  "method": "POST",
  "url": "http://localhost:8000/file-operation",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "operation": "read_file",
    "path": "/path/to/your/file.txt"
  }
}
```

### Method 2: Using AI Agent Node (Advanced)

For more complex workflows with AI decision-making.

**n8n Workflow Configuration:**

1. **AI Agent Node** setup:
   - Choose your LLM (OpenAI, Anthropic, etc.)
   - Add custom tools that call your MCP HTTP endpoints

2. **Custom Tool Configuration:**
```javascript
// In n8n Function Node - Create custom tools
const tools = [
  {
    name: "read_file",
    description: "Read the contents of a file",
    parameters: {
      type: "object",
      properties: {
        path: {
          type: "string",
          description: "The path to the file to read"
        }
      },
      required: ["path"]
    }
  },
  // ... other tools
];

return { tools };
```

3. **Tool Execution Function:**
```javascript
// Function Node to execute MCP operations
const operation = $input.all()[0].json.operation;
const path = $input.all()[0].json.path;
const content = $input.all()[0].json.content;

const response = await $http.request({
  method: 'POST',
  url: 'http://localhost:8000/file-operation',
  headers: {
    'Content-Type': 'application/json'
  },
  body: {
    operation: operation,
    path: path,
    content: content
  }
});

return response.json();
```

## Example n8n Workflows

### Workflow 1: Document Processing Pipeline

**Nodes:**
1. **Webhook Trigger** - Receives file path
2. **HTTP Request** - Read file content
3. **OpenAI Node** - Summarize content
4. **HTTP Request** - Write summary back
5. **Slack/Email Node** - Notify completion

**Workflow JSON Export:**
```json
{
  "name": "MCP File Processor",
  "nodes": [
    {
      "parameters": {
        "operation": "read_file",
        "path": "{{ $json.file_path }}"
      },
      "type": "n8n-nodes-base.httpRequest",
      "name": "Read File"
    },
    {
      "parameters": {
        "model": "gpt-3.5-turbo",
        "messages": [
          {
            "role": "user",
            "content": "Summarize this document: {{ $json.result }}"
          }
        ]
      },
      "type": "n8n-nodes-base.openAi",
      "name": "Summarize"
    }
  ]
}
```

### Workflow 2: Smart File Organizer

**Use Case:** AI analyzes files and organizes them into folders

**Nodes:**
1. **Schedule Trigger** - Run daily
2. **HTTP Request** - List directory contents
3. **Split in Batches** - Process files one by one
4. **HTTP Request** - Read each file
5. **OpenAI Node** - Classify file content
6. **HTTP Request** - Create appropriate directories
7. **Function Node** - Move files to correct folders

### Workflow 3: Code Documentation Generator

**Use Case:** Generate documentation for code files

**Nodes:**
1. **Manual Trigger** - Start process
2. **HTTP Request** - List all `.py` files
3. **AI Agent** - Analyze code and generate docs
4. **HTTP Request** - Write documentation files
5. **Slack Notification** - Report completion

## Advanced Integration: Custom Node

For heavy usage, you can create a custom n8n node:

### Custom Node Template

```typescript
// File: nodes/McpFileServer/McpFileServer.node.ts
import { IExecuteFunctions } from 'n8n-core';
import {
  INodeExecutionData,
  INodeType,
  INodeTypeDescription,
} from 'n8n-workflow';

export class McpFileServer implements INodeType {
  description: INodeTypeDescription = {
    displayName: 'MCP File Server',
    name: 'mcpFileServer',
    group: ['transform'],
    version: 1,
    description: 'Interact with MCP File Server',
    defaults: {
      name: 'MCP File Server',
    },
    inputs: ['main'],
    outputs: ['main'],
    properties: [
      {
        displayName: 'Operation',
        name: 'operation',
        type: 'options',
        options: [
          { name: 'Read File', value: 'read_file' },
          { name: 'Write File', value: 'write_file' },
          { name: 'List Directory', value: 'list_directory' },
          { name: 'Create Directory', value: 'create_directory' },
          { name: 'Delete File', value: 'delete_file' },
        ],
        default: 'read_file',
      },
      {
        displayName: 'File Path',
        name: 'path',
        type: 'string',
        default: '',
        required: true,
      },
      {
        displayName: 'Content',
        name: 'content',
        type: 'string',
        default: '',
        displayOptions: {
          show: {
            operation: ['write_file'],
          },
        },
      },
    ],
  };

  async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
    const items = this.getInputData();
    const returnData: INodeExecutionData[] = [];

    for (let i = 0; i < items.length; i++) {
      const operation = this.getNodeParameter('operation', i) as string;
      const path = this.getNodeParameter('path', i) as string;
      const content = this.getNodeParameter('content', i) as string;

      const body: any = { operation, path };
      if (content) body.content = content;

      const response = await this.helpers.httpRequest({
        method: 'POST',
        url: 'http://localhost:8000/file-operation',
        body,
        json: true,
      });

      returnData.push({
        json: response,
      });
    }

    return [returnData];
  }
}
```

## Deployment Considerations

### Production Setup

1. **Secure the API**: Add authentication to your HTTP endpoints
2. **Error Handling**: Implement retry logic and proper error responses
3. **Logging**: Add comprehensive logging for debugging
4. **Monitoring**: Set up health checks and monitoring

### Docker Setup

```dockerfile
# Dockerfile for MCP + HTTP server
FROM python:3.12-slim

WORKDIR /app
COPY . .

RUN pip install uv
RUN uv sync

EXPOSE 8000

CMD ["uv", "run", "python", "n8n_server.py"]
```

### n8n Cloud Configuration

If using n8n Cloud, ensure your HTTP server is:
1. **Publicly accessible** (use ngrok for testing)
2. **HTTPS enabled** (n8n Cloud requires HTTPS)
3. **CORS enabled** if calling from n8n web interface

## Testing Your Integration

### Test Workflow Template

Import this into n8n to test your integration:

```json
{
  "name": "MCP File Server Test",
  "nodes": [
    {
      "parameters": {},
      "id": "manual-trigger",
      "name": "Manual Trigger",
      "type": "n8n-nodes-base.manualTrigger",
      "position": [260, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "http://localhost:8000/write-file",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "Content-Type",
              "value": "application/json"
            }
          ]
        },
        "sendBody": true,
        "contentType": "json",
        "body": "={\"path\": \"/tmp/n8n_test.txt\", \"content\": \"Hello from n8n workflow!\"}"
      },
      "id": "write-file",
      "name": "Write File",
      "type": "n8n-nodes-base.httpRequest",
      "position": [460, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "http://localhost:8000/read-file",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "Content-Type",
              "value": "application/json"
            }
          ]
        },
        "sendBody": true,
        "contentType": "json",
        "body": "={\"path\": \"/tmp/n8n_test.txt\"}"
      },
      "id": "read-file",
      "name": "Read File",
      "type": "n8n-nodes-base.httpRequest",
      "position": [660, 300]
    }
  ],
  "connections": {
    "Manual Trigger": {
      "main": [
        [
          {
            "node": "Write File",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Write File": {
      "main": [
        [
          {
            "node": "Read File",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **Connection Refused**: Ensure your HTTP server is running on port 8000
2. **MCP Not Connected**: Check that your MCP file server is properly configured
3. **CORS Errors**: Add CORS headers to your FastAPI server if needed
4. **Timeout Errors**: Increase timeouts for large file operations

### Debug Tips

1. **Check server logs**: Monitor your HTTP server output
2. **Test endpoints directly**: Use curl or Postman to test
3. **n8n execution logs**: Check n8n's execution panel for errors
4. **Network connectivity**: Ensure n8n can reach your HTTP server

## Next Steps

1. **Start simple**: Begin with basic read/write operations
2. **Build workflows**: Create increasingly complex automation
3. **Add AI**: Integrate with LLMs for intelligent file processing
4. **Scale up**: Move to production with proper security and monitoring

Your MCP file server is now ready for powerful n8n workflows! 🚀