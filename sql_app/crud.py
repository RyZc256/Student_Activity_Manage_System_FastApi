#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @ Project: ActivityManagement
# @ File: crud
# @ Time: 29/3/2023 下午2:46
# @ Author: ryan.zhang
# @ Github: https://github.com/hz157
from sqlalchemy.orm import Session

from . import models


# 获取用户
def getUser(db: Session, user_id: str = None, openid: str = None):
    if user_id:
        return db.query(models.User).filter(models.User.id == user_id).first()
    else:
        return db.query(models.User).filter(models.User.openid == openid).first()


# 获取学生用户信息
def getStuInfo(db: Session, user_id: str):
    return db.query(models.StuInfo).filter(models.StuInfo.id == user_id).first()


# 获取教师用户信息
def getTeaInfo(db: Session, user_id: str):
    return db.query(models.TeaInfo).filter(models.TeaInfo.id == user_id).first()


# 新建用户
def createUser(db: Session, user: models.User):
    # Encry Password
    user.password = user.password + "salt"
    # 使用add来将该实例对象添加到您的数据库。
    db.add(user)
    # 使用commit来对数据库的事务提交（以便保存它们）。
    db.commit()
    # 使用refresh来刷新您的数据库实例（以便它包含来自数据库的任何新数据，例如生成的 ID）。
    db.refresh(user)
    return user


# 编辑学生信息
def editStuInfo(db: Session, stuInfo: models.StuInfo):
    db.add(stuInfo)
    db.commit()
    db.refresh(stuInfo)
    return stuInfo


# 用户绑定微信
def userBandWechat(db: Session, user: models.User, openid: str, unionid: str = None):
    user.openid = openid
    if unionid is not None:
        user.unionid = unionid
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# 用户解绑定微信
def userUnbandWechat(db: Session, user: models.User):
    user.openid = None
    user.unionid = None
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
