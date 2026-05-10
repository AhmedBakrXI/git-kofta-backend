from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import httpx
import os
import requests
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

FRONTEND_URL = os.getenv("FRONTEND_URL")

app = FastAPI(title="Git Spicy")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health_check():
    return {"message": "healthy"}



@app.get("/auth/github/login")
def github_login():
    github_url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={CLIENT_ID}&scope=read:user user:email repo read:org"
        "&prompt=select_account"
    )
    return RedirectResponse(github_url)


@app.get("/auth/github/callback")
async def github_callback(code: str):
    # 1. Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "code": code,
            },
        )
        token = token_res.json().get("access_token")


    # 2. Redirect to frontend with token
    return RedirectResponse(
        f"{FRONTEND_URL}/auth/github?token={token}"
    )


class LogoutRequest(BaseModel):
    token: str


@app.post("/auth/github/logout")
async def revoke_token(payload: LogoutRequest):
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method="DELETE",
            url=f"https://api.github.com/applications/{CLIENT_ID}/token",
            auth=(CLIENT_ID, CLIENT_SECRET),
            json={
                "access_token": payload.token
            },
            headers={
                "Accept": "application/vnd.github+json"
            }
        )

    if response.status_code == 204:
        return {
            "status": "success",
            "message": "Token revoked successfully"
        }

    raise HTTPException(
        status_code=response.status_code,
        detail=response.text
    )
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"https://api.github.com/applications/{CLIENT_ID}/token",
            auth=(CLIENT_ID, CLIENT_SECRET),
            json={"access_token": token},
            headers={
                "Accept": "application/vnd.github+json"
            }
        )

    if response.status_code == 204:
        return {
            "status": "success",
            "message": "Token revoked successfully"
        }

    raise HTTPException(
        status_code=response.status_code,
        detail=response.json()
    )