# CardGenius Recommendations API Documentation

## Overview

REST API for batch credit card recommendations processing.

**Base URL**: `http://your-server:8000`  
**Authentication**: API Key via `X-API-Key` header

## Authentication

All requests require an API key in the header:

```
X-API-Key: YOUR_SECRET_API_KEY_HERE
```

## Endpoints

### 1. Create Recommendation Job

**POST** `/api/v1/recommendations`

Submit a batch of users for card recommendations.

**Request Body:**
```json
{
  "users": [
    {
      "user_id": "123456",
      "avg_amazon_gmv": 5000,
      "avg_flipkart_gmv": 3000,
      "avg_myntra_gmv": 2000,
      "avg_ajio_gmv": 1000,
      "avg_confirmed_gmv": 5000,
      "avg_grocery_gmv": 8000,
      "total_gmv": 24000
    }
  ],
  "top_n_cards": 10
}
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "total_users": 1,
  "message": "Job created successfully"
}
```

**Limits:**
- Maximum 200 users per batch
- All spending fields are optional (default: 0)

### 2. Check Job Status

**GET** `/api/v1/status/{job_id}`

Check the processing status of a job.

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "total_users": 200,
  "processed_users": 50,
  "successful": 48,
  "failed": 2,
  "progress_percentage": 25.0
}
```

**Status Values:**
- `queued` - Job is waiting to be processed
- `processing` - Job is currently being processed
- `completed` - Job finished successfully
- `failed` - Job encountered an error

### 3. Get Job Results

**GET** `/api/v1/results/{job_id}`

Retrieve results for a completed job.

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "total_users": 200,
  "successful": 198,
  "failed": 2,
  "results": [
    {
      "userid": "123456",
      "avg_amazon_gmv": 5000,
      "top1_card_name": "AXIS MAGNUS",
      "top1_net_savings": 15000,
      "top1_total_savings_yearly": 20000,
      "top1_joining_fees": 5000,
      "top1_amazon_spends_points": 250,
      ...
    }
  ]
}
```

### 4. Delete Job

**DELETE** `/api/v1/job/{job_id}`

Delete a job and its results (cleanup).

**Response:**
```json
{
  "message": "Job {job_id} deleted successfully"
}
```

## Usage Example

### Python Client

```python
import requests
import time

API_URL = "http://localhost:8000"
API_KEY = "YOUR_SECRET_API_KEY_HERE"
headers = {"X-API-Key": API_KEY}

# Step 1: Submit batch
response = requests.post(
    f"{API_URL}/api/v1/recommendations",
    headers=headers,
    json={
        "users": [
            {
                "user_id": "123456",
                "avg_amazon_gmv": 5000,
                "avg_flipkart_gmv": 3000
            }
        ],
        "top_n_cards": 10
    }
)
job_id = response.json()['job_id']

# Step 2: Poll for completion
while True:
    status = requests.get(
        f"{API_URL}/api/v1/status/{job_id}",
        headers=headers
    ).json()
    
    if status['status'] == 'completed':
        break
    
    print(f"Progress: {status['progress_percentage']:.1f}%")
    time.sleep(5)

# Step 3: Get results
results = requests.get(
    f"{API_URL}/api/v1/results/{job_id}",
    headers=headers
).json()

print(f"Got {len(results['results'])} user recommendations")
```

### cURL Example

```bash
# Submit batch
curl -X POST "http://localhost:8000/api/v1/recommendations" \
  -H "X-API-Key: YOUR_SECRET_API_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{"users":[{"user_id":"123","avg_amazon_gmv":5000}],"top_n_cards":10}'

# Check status
curl -X GET "http://localhost:8000/api/v1/status/{job_id}" \
  -H "X-API-Key: YOUR_SECRET_API_KEY_HERE"

# Get results
curl -X GET "http://localhost:8000/api/v1/results/{job_id}" \
  -H "X-API-Key: YOUR_SECRET_API_KEY_HERE"
```

## Rate Limiting

- CardGenius API: 1.2 seconds between requests
- Your API: No limit (handles rate limiting internally)
- Batch size: Max 200 users
- Processing time: ~2-5 minutes for 200 users

## Error Handling

**401 Unauthorized**: Invalid API key  
**400 Bad Request**: Invalid request data or batch > 200 users  
**404 Not Found**: Job ID not found  
**500 Internal Server Error**: Processing error (check logs)

## Production Deployment

### Local Testing:
```bash
pip install -r requirements.txt
python api_server.py
```

### Production:
```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker:
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Interactive Documentation

Once the API is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

You can test all endpoints directly in the browser!

