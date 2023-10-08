#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @ Project: ActivityManagement
# @ File: userinfo
# @ Time: 29/3/2023 下午2:13
# @ Author: ryan.zhang
# @ Github: https://github.com/hz157
from typing import Union, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from security.token import check_jwt_token
from sql_app import models, crud
from sql_app.database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

router = APIRouter()


# Dependency
def get_db():
    # 我们需要每个请求有一个独立的数据库会话/连接（SessionLocal），
    # 在所有请求中使用相同的会话，然后在请求完成后关闭它。
    db = SessionLocal()
    # 我们的依赖项将创建一个新的 SQLAlchemy SessionLocal，
    # 它将在单个请求中使用，然后在请求完成后关闭它。
    try:
        yield db
    finally:
        db.close()


@router.get("/get/{id}", tags=["获取用户信息"])
def getInfo(id: str, db: Session = Depends(get_db), token_data: Union[str, Any] = Depends(check_jwt_token)) -> Any:
    print('123123')
    print(str(token_data))
    user = crud.getUser(db, user_id=token_data['uid'])
    if user.role == 'stu':
        # 鉴权 - 是否访问的是他人的数据
        if user.id == id:
            userInfo = crud.getStuInfo(db, user_id=id).to_json()
        # 限制访问他人数据
        raise HTTPException(status_code=401, detail='this user has no permission')
    elif user.role == 'tea':
        if user.id == id:
            userInfo = crud.getTeaInfo(db, user_id=id).to_json()
    # 超级管理员
    elif user.role == 'admin':
        if user.id == id:
            userInfo = "Super Admin"
        else:
            user = crud.getUser(db, user_id=id)
            if user.role == 'tea':
                userInfo = crud.getTeaInfo(db, user_id=id).to_json()
            elif user.role == 'stu':
                userInfo = crud.getStuInfo(db, user_id=id).to_json()
    return JSONResponse(content={'status': 'success',
                                 'detail': userInfo})



class stuInfoItem(BaseModel):
    id: str
    name: str
    sex: str
    clas: str = None
    idcard: str
    end_time: str


@router.post("/edit", tags=["编辑用户信息"])
def editInfo(data: stuInfoItem, db: Session = Depends(get_db)):
    user = crud.getUser(db, user_id=data.id)
    if user.role == 'stu':
        userInfo = crud.getStuInfo(db, user_id=id)
        userInfo._class = data.clas
    elif user.role == 'tea':
        userInfo = crud.getTeaInfo(db, user_id=id)
    userInfo.name = data.name
    userInfo.sex = data.sex
