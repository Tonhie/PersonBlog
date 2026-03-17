from fastapi import FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from random import randint
import sqlite3
import os

pathDB = './blog.db'

def get_db_connection():
    exist = os.path.exists(pathDB)
    conn = sqlite3.connect(pathDB, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""--sql
        CREATE TABLE IF NOT EXISTS POSTS (
            ID INTEGER PRIMARY KEY,
            author TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            published INTEGER DEFAULT 1,
            rating INTEGER
        )
    """)
    cursor = conn.execute("SELECT COUNT(*) FROM POSTS")
    if cursor.fetchone()[0] == 0:
        origin_query = ("INSERT INTO POSTS (author, title, content) VALUES (?, ?, ?)")
        conn.execute(origin_query, ('Tonhie', 'Origin Blog', 'Dreaming back to Origin.'))
        conn.commit()
    conn.close()

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
    author: str
    title: str
    content: str

class Post(PostBase):
    id: int
    published: int = 1
    rating: Optional[int]

@app.get("/")
def read_root():
    return "Hello, World!"

@app.post("/posts")
def createpost(newPost : PostBase):
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO POSTS (author, title, content) VALUES (?, ?, ?)",
            (newPost.author, newPost.title, newPost.content)
        )
        conn.commit()
        return {"message" : "Post created"}
    finally:
        conn.close()

@app.get("/posts")
def getAllPosts():
    conn = get_db_connection()
    try:
        cursor = conn.execute("SELECT * FROM POSTS WHERE published=1")
        rows = cursor.fetchall()
        return {"message" : "Found all post", "data" : [dict(row) for row in rows]}
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
            "UPDATE POSTS SET author=?, title=?, content=? WHERE id=?", 
            [newPost.author, newPost.title, newPost.content, post_id]
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
