from fastapi import FastAPI, HTTPException, status, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from database import init_db, get_db_connection

init_db()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount('/static', StaticFiles(directory="static"), name="static")

class PostBase(BaseModel):
    author: str = "Tonhie"
    title: str
    content: str
    level: str = "INFO"

class Post(PostBase):
    id: int
    published: int = 1
    rating: Optional[int] = None
    created_at: Optional[str] = None

class CommentBase(BaseModel):
    content: str
    rating: int = 5

class SysLogBase(BaseModel):
    env_key: str
    env_val: str

@app.get("/")
def read_root():
    return "Hello, World!"

@app.get("/api/ip")
def get_ip(request: Request):
    ip = request.headers.get("CF-Connecting-IP")
    if not ip:
        ip = request.client.host if request.client else "UNKNOWN"
    return {"ip": ip}

@app.post("/posts")
def createpost(newPost : PostBase):
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO POSTS (author, title, content, level) VALUES (?, ?, ?, ?)",
            (newPost.author, newPost.title, newPost.content, newPost.level)
        )
        conn.commit()
        return {"message" : "Post created"}
    finally:
        conn.close()

@app.get("/posts")
def getAllPosts():
    conn = get_db_connection()
    try:
        cursor = conn.execute("""
            SELECT p.*, COALESCE(AVG(CAST(c.rating AS FLOAT)), 0) as avg_rating
            FROM POSTS p
            LEFT JOIN COMMENTS c ON p.ID = c.post_id
            WHERE p.published=1
            GROUP BY p.ID
        """)
        rows = cursor.fetchall()
        data = []
        for row in rows:
            d = dict(row)
            d['avg_rating'] = round(d['avg_rating'], 1) if d['avg_rating'] else 0.0
            data.append(d)
        return {"message" : "Found all post", "data" : data}
    finally:
        conn.close()

@app.get("/posts/{post_id}")
def getPost(post_id : int):
    conn = get_db_connection()
    try:
        cursor = conn.execute("SELECT * FROM POSTS WHERE published=1 AND id=?", [post_id])
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        return {"message" : "Post found", "data" : dict(row)}
    finally:
        conn.close()

@app.delete("/posts/{post_id}")
def deletePost(post_id : int):
    conn = get_db_connection()
    try:
        cursor = conn.execute("DELETE FROM POSTS WHERE id=?", [post_id])
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        conn.commit()
        return {"message" : "Post Deleted"}
    finally:
        conn.close()

@app.put("/posts/{post_id}")
def updatePost(post_id : int, newPost : PostBase):
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "UPDATE POSTS SET author=?, title=?, content=?, level=? WHERE id=?", 
            [newPost.author, newPost.title, newPost.content, newPost.level, post_id]
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        return {"message" : "Post Updated"}
    finally:
        conn.close()
@app.post("/posts/{post_id}/comments")
def add_comment(post_id: int, comment: CommentBase, request: Request):
    conn = get_db_connection()
    try:
        ip = request.headers.get("CF-Connecting-IP")
        if not ip:
            ip = request.client.host if request.client else "UNKNOWN"
        conn.execute(
            "INSERT INTO COMMENTS (post_id, content, ip_address, rating) VALUES (?, ?, ?, ?)",
            (post_id, comment.content, ip, comment.rating)
        )
        conn.commit()
        return {"message": "Comment injected"}
    finally:
        conn.close()

@app.get("/posts/{post_id}/comments")
def get_comments(post_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.execute("SELECT * FROM COMMENTS WHERE post_id=? ORDER BY created_at ASC", [post_id])
        rows = cursor.fetchall()
        return {"message": "Found comments", "data": [dict(row) for row in rows]}
    finally:
        conn.close()

@app.post("/sys_logs")
def add_sys_log(log: SysLogBase, request: Request):
    conn = get_db_connection()
    try:
        ip = request.headers.get("CF-Connecting-IP")
        if not ip:
            ip = request.client.host if request.client else "UNKNOWN"
        conn.execute(
            "INSERT INTO SYS_LOGS (ip_address, env_key, env_val) VALUES (?, ?, ?)",
            (ip, log.env_key, log.env_val)
        )
        conn.commit()
        return {"message": "Syslog injected"}
    finally:
        conn.close()

@app.get("/sys_logs")
def get_sys_logs(request: Request):
    conn = get_db_connection()
    try:
        ip = request.headers.get("CF-Connecting-IP")
        if not ip:
            ip = request.client.host if request.client else "UNKNOWN"
        cursor = conn.execute("SELECT * FROM SYS_LOGS WHERE ip_address=? ORDER BY created_at ASC", [ip])
        rows = cursor.fetchall()
        return {"message": "Found sys logs", "data": [dict(row) for row in rows]}
    finally:
        conn.close()
