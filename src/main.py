# SPDX-License-Identifier: GPL-3.0 
# T818
# A photo tagging system
#
# main.py
#
# COPYRIGHT NOTICE
# Copyright (C) 2025 0x4248 and contributors
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the license is not changed.
#
# This software is free and open source. Licensed under the GNU general
# public license version 3.0 as published by the Free Software Foundation.


from fastapi import FastAPI, Request, Header, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse, PlainTextResponse, HTMLResponse, FileResponse
from typing import Annotated
from lib import database
from asyncio import run
from PIL import Image
import uvicorn
import hashlib
import time
import datetime
import base64
import PIL
import os

app = FastAPI()

@app.get("/")
async def root():
    f = open("src/static/index.html", "r")
    html = f.read()
    f.close()
    return HTMLResponse(content=html)

@app.get("/static/{path:path}")
async def root(path):
    return FileResponse("src/static/" + path)


@app.get("/posts")
async def get_posts(q: str = None):
    if q == None:
        posts = database.get_recent_posts()
        html = "<html><head><title>Recent Posts</title></head><body><div>"
        for post in posts:
            html += f"<a href='/posts/{post[0]}'><img src='/image/thumb/{post[2]}'></a>"
        html += "</div>"
        html += "</body></html>"
        return HTMLResponse(content=html)
    
    if q != None:
        posts = database.get_with_tags(q)
        html = "<html><head><title>Posts with tag</title></head><body><ul>"
        for post in posts:
            html += f"<li><a href='/posts/{post[0]}'>{post[3]}</a> by {post[1]}</li>"
        html += "</ul>"
        html += "</body></html>"
        return HTMLResponse(content=html)
    
@app.get("/posts/{ID}")
async def get_post(ID: int):
    post = database.get_post(ID)
    if post == None:
        return JSONResponse(content={"status": "error", "message": "post not found"}, status_code=404)
    html = "<html><head><title>Post</title></head><body>"
    html += f"<h1>{post[3]}</h1>"
    html += f"<p>By {post[1]}</p>"
    html += f"<p>{post[4]}</p>"
    html += f"<img src='/image/{post[2]}' width='50%'>"
    html += "</body></html>"
    return HTMLResponse(content=html)

@app.post("/upload")
async def upload_post(User: str = Header(None), Tags: str = Header(None), Description: str = Header(None),
                    Rating: str = Header(None), Type: str = Header(None), Source: str = Header(None),
                    FileData: UploadFile = File(...)):
    OriginalFileName = FileData.filename
    FileData = await FileData.read()
    FileID = hashlib.sha256(FileData).hexdigest()
    Date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    Score = 0
    database.add_post(User, FileID, Tags, Description, Date, Rating, Score, Type, Source, OriginalFileName)
    os.makedirs(f"data/posts/{FileID}")

    file_extention = OriginalFileName.split(".")[-1]

    f = open(f"data/posts/{FileID}/post.{file_extention}", "wb")
    f.write(FileData)
    f.close()
    img = Image.open(f"data/posts/{FileID}/post.{file_extention}")
    img.thumbnail((100, 100))
    img.save(f"data/posts/{FileID}/post.thumb.{file_extention}")
    f.close()
    return {"status": "success", "FileID": FileID}

@app.get("/image/{FileID}")
async def get_image(FileID: str):
    return FileResponse(f"data/posts/{FileID}/post.jpg")

@app.get("/image/thumb/{FileID}")
async def get_image(FileID: str):
    return FileResponse(f"data/posts/{FileID}/post.thumb.jpg")

@app.middleware("http")
async def log_request_info(request: Request, call_next):
    pre_reqtime = time.time()
    response = await call_next(request)
    post_reqtime = time.time()
    response.headers["server"] = "T818"
    response.headers["t818ng-version"] = "0.1"
    response.headers["compute-time"] = str(post_reqtime - pre_reqtime)
    return response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")