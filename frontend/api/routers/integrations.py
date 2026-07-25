from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import requests
from api.services.ingestion_service import ingestion_service

router = APIRouter(prefix="/integrations", tags=["integrations"])

@router.post("")
async def create_integration(data: dict):
    return {"message": "Integration created successfully", "id": data.get("id", "int_" + str(hash(data.get("platform_name", "platform"))))}

@router.post("/{id}/sync")
async def sync_integration(id: str, data: dict):
    platform = data.get("platform_type", "").lower()
    token = data.get("api_token", "")
    
    if not token:
        raise HTTPException(status_code=400, detail="API Token is required for synchronization")
        
    pages_indexed = 0
    
    try:
        if platform == "notion":
            headers = {
                "Authorization": f"Bearer {token}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json"
            }
            response = requests.post("https://api.notion.com/v1/search", headers=headers, json={"filter": {"value": "page", "property": "object"}})
            
            if not response.ok:
                raise HTTPException(status_code=response.status_code, detail=f"Notion API error: {response.text}")
                
            results = response.json().get("results", [])
            for page in results:
                page_id = page["id"]
                title_prop = page.get("properties", {}).get("title", {}).get("title", [])
                title = title_prop[0]["plain_text"] if title_prop else f"Notion Page {page_id}"
                
                text_content = f"Notion Page: {title}\nID: {page_id}\nURL: {page.get('url', '')}"
                
                await ingestion_service.process_document(
                    filename=f"notion_{page_id}.txt",
                    content=text_content
                )
                pages_indexed += 1
                
        elif platform == "github":
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github.v3+json"
            }
            response = requests.get("https://api.github.com/user/repos", headers=headers)
            
            if not response.ok:
                raise HTTPException(status_code=response.status_code, detail=f"GitHub API error: {response.text}")
                
            repos = response.json()
            for repo in repos:
                text_content = f"GitHub Repository: {repo.get('name')}\nDescription: {repo.get('description', '')}\nURL: {repo.get('html_url')}"
                await ingestion_service.process_document(
                    filename=f"github_{repo.get('name')}.txt",
                    content=text_content
                )
                pages_indexed += 1
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    return {"message": f"Integration {id} synced successfully", "pages_indexed": pages_indexed}
