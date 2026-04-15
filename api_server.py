#!/usr/bin/env python3
"""
FastAPI Server for CardGenius Recommendations
Provides API endpoints for batch card recommendations
"""

import os
from fastapi import FastAPI, HTTPException, Header, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import uuid
import json
import os
from datetime import datetime
import pandas as pd
from cardgenius_batch_runner import CardGeniusBatchRunner
from cardgenius_batch_runner_v2 import CardGeniusBatchRunnerV2
import tempfile
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# CORS middleware for production
app = FastAPI(
    title="CardGenius Recommendations API",
    description="Batch credit card recommendations API supporting both V1 (full output) and V2 (simplified output) formats",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key from environment variable (production) or fallback
API_KEY = os.getenv("CARDGENIUS_API_KEY", "cgapi_2025_secure_key_12345")

# Job storage (in-memory for now, can be moved to Redis/DB later)
jobs = {}
results_storage = {}

class UserSpendingData(BaseModel):
    """User spending data model"""
    user_id: str
    avg_amazon_gmv: Optional[float] = 0
    avg_flipkart_gmv: Optional[float] = 0
    avg_myntra_gmv: Optional[float] = 0
    avg_ajio_gmv: Optional[float] = 0
    avg_confirmed_gmv: Optional[float] = 0
    avg_grocery_gmv: Optional[float] = 0

class BatchRecommendationRequest(BaseModel):
    """Batch recommendation request model"""
    users: List[UserSpendingData]
    top_n_cards: Optional[int] = 10
    version: Optional[str] = "v1"  # "v1" or "v2"

class JobResponse(BaseModel):
    """Job creation response"""
    job_id: str
    status: str
    total_users: int
    version: str
    message: str

class StatusResponse(BaseModel):
    """Job status response"""
    job_id: str
    status: str
    total_users: int
    processed_users: int
    successful: int
    failed: int
    progress_percentage: float
    version: str

def verify_api_key(x_api_key: str = Header(...)):
    """Verify API key"""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

def process_batch(job_id: str, users: List[UserSpendingData], top_n_cards: int, version: str = "v1"):
    """Process batch of users in background"""
    try:
        logger.info(f"Starting job {job_id} with {len(users)} users using {version}")
        
        # Update job status
        jobs[job_id]['status'] = 'processing'
        jobs[job_id]['started_at'] = datetime.now().isoformat()
        jobs[job_id]['processed_users'] = 0
        jobs[job_id]['version'] = version
        
        # Convert users to DataFrame
        user_data = []
        for user in users:
            user_data.append({
                'userid': user.user_id,
                'avg_amazon_gmv': user.avg_amazon_gmv or 0,
                'avg_flipkart_gmv': user.avg_flipkart_gmv or 0,
                'avg_myntra_gmv': user.avg_myntra_gmv or 0,
                'avg_ajio_gmv': user.avg_ajio_gmv or 0,
                'avg_confirmed_gmv': user.avg_confirmed_gmv or 0,
                'avg_grocery_gmv': user.avg_grocery_gmv or 0
            })
        
        df = pd.DataFrame(user_data)
        
        # Create temporary files
        temp_input = f"temp_job_{job_id}_input.xlsx"
        temp_output = f"temp_job_{job_id}_output.xlsx"
        temp_config = f"temp_job_{job_id}_config.json"
        
        # Save input data
        df.to_excel(temp_input, index=False)
        
        # Create config
        config = {
            "api": {
                "base_url": "https://card-recommendation-api-v2.bankkaro.com/cg/api/pro",
                "timeout": 30,
                "sleep_between_requests": 1.2,
                "max_retries": 3
            },
            "excel": {
                "input_file": temp_input,
                "output_file": temp_output,
                "sheet_name": 0
            },
            "column_mappings": {
                "user_id": "userid",
                "amazon_spends": "avg_amazon_gmv",
                "flipkart_spends": "avg_flipkart_gmv",
                "myntra": "avg_myntra_gmv",
                "ajio": "avg_ajio_gmv",
                "avg_gmv": "avg_confirmed_gmv",
                "grocery": "avg_grocery_gmv"
            },
            "processing": {
                "top_n_cards": top_n_cards,
                "extract_spend_keys": [
                    "amazon_spends",
                    "flipkart_spends",
                    "grocery_spends_online",
                    "other_online_spends"
                ],
                "skip_empty_rows": True,
                "continue_on_error": True,
                "other_online_mode": "sum_components"
            }
        }
        
        with open(temp_config, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Process using appropriate batch runner based on version
        if version == "v2":
            runner = CardGeniusBatchRunnerV2(temp_config)
        else:
            runner = CardGeniusBatchRunner(temp_config)
        output_file = runner.process_excel()
        
        # Read results
        result_df = pd.read_excel(output_file)
        
        # Replace NaN values appropriately based on column type
        # For string columns, replace NaN with empty string
        string_columns = result_df.select_dtypes(include=['object']).columns
        for col in string_columns:
            result_df[col] = result_df[col].fillna('')
        
        # For numeric columns, replace NaN with 0
        numeric_columns = result_df.select_dtypes(include=['number']).columns
        for col in numeric_columns:
            result_df[col] = result_df[col].fillna(0)
        
        # Convert to JSON
        results = result_df.to_dict('records')
        
        # Store results
        results_storage[job_id] = results
        
        # Update job status
        jobs[job_id]['status'] = 'completed'
        jobs[job_id]['completed_at'] = datetime.now().isoformat()
        jobs[job_id]['processed_users'] = len(users)
        jobs[job_id]['successful'] = len([r for r in results if not r.get('cardgenius_error')])
        jobs[job_id]['failed'] = len([r for r in results if r.get('cardgenius_error')])
        
        # Cleanup temp files
        try:
            os.unlink(temp_input)
            os.unlink(temp_config)
            # Keep output file for download
        except:
            pass
        
        logger.info(f"Job {job_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}", exc_info=True)
        jobs[job_id]['status'] = 'failed'
        jobs[job_id]['error'] = str(e)
        jobs[job_id]['completed_at'] = datetime.now().isoformat()
        
        # Cleanup temp files on error
        try:
            if 'temp_input' in locals():
                os.unlink(temp_input)
            if 'temp_config' in locals():
                os.unlink(temp_config)
            if 'temp_output' in locals() and os.path.exists(temp_output):
                os.unlink(temp_output)
        except:
            pass

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "service": "CardGenius Recommendations API",
        "version": "2.0.0",
        "status": "running",
        "supported_versions": ["v1", "v2"],
        "description": "Supports both V1 (full output) and V2 (simplified output) recommendation formats"
    }

@app.get("/api/v1/versions")
async def get_version_info():
    """Get information about supported API versions"""
    return {
        "supported_versions": ["v1", "v2"],
        "v1": {
            "description": "Full output format with all CardGenius data",
            "output_columns": "Complete set of columns including rewards, cashback, and detailed breakdowns"
        },
        "v2": {
            "description": "Simplified output format for frontend",
            "output_columns": "8 columns per card: card_name, total_savings_yearly, net_savings, joining_fees, amazon_breakdown, flipkart_breakdown, grocery_breakdown, other_online_breakdown"
        }
    }

@app.post("/api/v1/recommendations", response_model=JobResponse)
async def create_recommendation_job(
    request: BatchRecommendationRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Header(None, alias="X-API-Key")
):
    """
    Create a new batch recommendation job
    
    Args:
        request: Batch recommendation request with user spending data
        X-API-Key: API key for authentication
        
    Returns:
        Job ID and status
    """
    # Verify API key
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Validate request
    if not request.users:
        raise HTTPException(status_code=400, detail="No users provided")
    
    if len(request.users) > 200:
        raise HTTPException(status_code=400, detail="Maximum 200 users per batch")
    
    # Validate version
    if request.version not in ["v1", "v2"]:
        raise HTTPException(status_code=400, detail="Version must be 'v1' or 'v2'")
    
    # Create job
    job_id = str(uuid.uuid4())
    
    jobs[job_id] = {
        'job_id': job_id,
        'status': 'queued',
        'total_users': len(request.users),
        'processed_users': 0,
        'successful': 0,
        'failed': 0,
        'version': request.version,
        'created_at': datetime.now().isoformat(),
        'started_at': None,
        'completed_at': None
    }
    
    # Schedule background processing
    background_tasks.add_task(
        process_batch,
        job_id,
        request.users,
        request.top_n_cards,
        request.version
    )
    
    logger.info(f"Created job {job_id} with {len(request.users)} users")
    
    return JobResponse(
        job_id=job_id,
        status="queued",
        total_users=len(request.users),
        version=request.version,
        message=f"Job created successfully using {request.version}. Use /api/v1/status/{job_id} to check progress"
    )

@app.get("/api/v1/status/{job_id}", response_model=StatusResponse)
async def get_job_status(
    job_id: str,
    api_key: str = Header(None, alias="X-API-Key")
):
    """
    Get status of a recommendation job
    
    Args:
        job_id: Job ID returned from create_recommendation_job
        X-API-Key: API key for authentication
        
    Returns:
        Job status and progress
    """
    # Verify API key
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Check if job exists
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    return StatusResponse(
        job_id=job_id,
        status=job['status'],
        total_users=job['total_users'],
        processed_users=job.get('processed_users', 0),
        successful=job.get('successful', 0),
        failed=job.get('failed', 0),
        progress_percentage=(job.get('processed_users', 0) / job['total_users'] * 100) if job['total_users'] > 0 else 0,
        version=job.get('version', 'v1')
    )

@app.get("/api/v1/results/{job_id}")
async def get_job_results(
    job_id: str,
    api_key: str = Header(None, alias="X-API-Key")
):
    """
    Get results of a completed recommendation job
    
    Args:
        job_id: Job ID returned from create_recommendation_job
        X-API-Key: API key for authentication
        
    Returns:
        Recommendation results for all users
    """
    # Verify API key
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Check if job exists
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    # Check if job is completed
    if job['status'] != 'completed':
        raise HTTPException(
            status_code=400,
            detail=f"Job is not completed yet. Current status: {job['status']}"
        )
    
    # Get results
    if job_id not in results_storage:
        raise HTTPException(status_code=404, detail="Results not found")
    
    return {
        "job_id": job_id,
        "status": "completed",
        "version": job.get('version', 'v1'),
        "total_users": job['total_users'],
        "successful": job['successful'],
        "failed": job['failed'],
        "results": results_storage[job_id]
    }

@app.delete("/api/v1/job/{job_id}")
async def delete_job(
    job_id: str,
    api_key: str = Header(None, alias="X-API-Key")
):
    """
    Delete a job and its results
    
    Args:
        job_id: Job ID to delete
        X-API-Key: API key for authentication
    """
    # Verify API key
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Delete job and results
    if job_id in jobs:
        del jobs[job_id]
    if job_id in results_storage:
        del results_storage[job_id]
    
    return {"message": f"Job {job_id} deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment (for production) or default to 8000
    port = int(os.getenv("PORT", 8000))
    
    print("Starting CardGenius Recommendations API Server v2.0")
    print(f"API Documentation: http://localhost:{port}/docs")
    print(f"API Key: {API_KEY}")
    print("Supported Versions: V1 (full output) and V2 (simplified output)")
    print(f"Environment: {'Production' if os.getenv('PORT') else 'Development'}")
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=port)

