#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @ Project: ActivityManagement
# @ File: token
# @ Time: 30/3/2023 上午10:18
# @ Author: hz157
# @ Github: https://github.com/hz157
from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import jwt
from fastapi import Header, HTTPException

from config import config

# 导入配置文件

ALGORITHM = "HS256"
SECRET_KEY = config.getYaml()['token']['secret_key']


def create_access_token(uid: str, expires_delta: timedelta = None) -> str:
    """
    生成token
    :param uid: 用户标签
    :param expires_delta: 过期时间
    :return:
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode = {"exp": expire, "uid": uid}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def check_jwt_token(token: Optional[str] = Header(...)) -> Union[str, Any]:
    """
    解析验证 headers中为token的值 当然也可以用 Header(..., alias="Authentication") 或者 alias="X-token"
    :param token:
    :return:
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except (jwt.JWTError, jwt.ExpiredSignatureError, AttributeError):
        # 抛出自定义异常， 然后捕获统一响应
        raise HTTPException(status_code=401, detail='this user has no permission')
