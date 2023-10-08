#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @ Project: ActivityManagement
# @ File: user
# @ Time: 29/3/2023 下午2:13
# @ Author: ryan.zhang
# @ Github: https://github.com/hz157
import json

import requests as requests
from pydantic import BaseModel

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from config import config
from security.token import create_access_token
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


class loginItem(BaseModel):
    id: str
    password: str


@router.post("/login", tags=["用户登录"])
async def login(data: loginItem, db: Session = Depends(get_db)):
    """
    用户登录接口
    :param data: loginItem实体类
    :param db: 数据库实例
    :return: 接口响应
    """
    user = crud.getUser(db, user_id=data.id)
    if user:
        # 判断是否绑定微信
        if user.openid is None:
            return JSONResponse(content={'status': 'success'})
        else:
            return JSONResponse(content={'status': 'error',
                                         'msg': 'please use wechat to login'})  # 限制微信登录
    else:
        return JSONResponse(content={'status': 'error',
                                     'msg': 'wrong id or password'})    # 账号密码有误


@router.get("/login/wx/{code}", tags=["微信登录"])
async def wechatLogin(code: str, db: Session = Depends(get_db)):
    # result = wechatLoginApi(code)
    # if len(result) == 2:
    #     return JSONResponse(content=result)
    # else:
    #     user = crud.getUser(db, openid=result['openid'])
    user = crud.getUser(db, openid=code)
    # 判断openid用户是否存在
    if user:
        # 登录token 只存放了user.id
        return JSONResponse(content={'status': 'success',
                                     'detail': {'token': create_access_token(user.id)}
                                     })
    else:
        return JSONResponse(content={'status': 'error',
                                     'msg': 'wechat not tied'})


async def wechatLoginApi(code):
    """
    微信登录API
    :param code: JS_Code
    :return: 微信服务器返回结果
    """
    conf = config.getYaml()
    host = conf['wechat']['login_host']
    appid = conf['wechat']['appid']
    secret = conf['wechat']['secret']
    url = f"{host}?appid={appid}&secret={secret}&js_code={code}&grant_type=authorization_code"
    header = {'user-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/111.0.0.0 Safari/537.36'}
    wechat_api = json.loads(requests.get(url=url, header=header).text)
    # 无效 JS_Code
    if wechat_api['errcode'] == 40029:
        return {'status': 'error',
                'msg': 'code invalid'}
    # API 调用太频繁
    elif wechat_api['errcode'] == 45011:
        return {'status': 'error',
                'msg': 'api minute-quota reach limit mustslower retry next minute'}
    # 高风险等级用户
    elif wechat_api['errcode'] == 40226:
        return {'status': 'error',
                'msg': 'code blocked'}
    # 系统繁忙
    elif wechat_api['errcode'] == -1:
        return {'status': 'error',
                'msg': 'system error'}
    return wechat_api


class bindWechatItem(BaseModel):
    id: str
    password: str
    openid: str
    unionid: str = None


@router.post("/bind/wx", tags=["微信绑定"])
async def bindWechat(data: bindWechatItem, db: Session = Depends(get_db)):
    """
    用户微信绑定
    :param data: bindWechatItem实体类
    :param db: 数据库实例
    :return: 接口响应
    """
    # 请求用户表
    user = crud.getUser(db, user_id=data.id)
    # 判断用户账号密码是否匹配
    if user.id == data.id and user.password == data.password:
        if crud.userBandWechat(db, user=user, openid=data.openid, unionid=data.unionid):
            return JSONResponse(content={'status': 'success'})
    else:
        return JSONResponse(content={'status': 'error',
                                     'msg': 'wrong id or password'})


@router.get("/unbind/wx/{id}", tags=["解除微信绑定"])
async def unbindWechat(id: str, db: Session = Depends(get_db)):
    """
    解除用户微信绑定
    :param id: 用户id
    :param db: 数据库实例
    :return: 接口响应
    """
    # 请求用户表
    user = crud.getUser(db, user_id=id)
    # 判断是否存在用户
    if user:
        # 执行修改
        if crud.userUnbandWechat(db, user):
            return JSONResponse(content={'status': 'success'})
    else:
        return JSONResponse(content={'status': 'error',
                                     'msg': 'uid does not exist'})
