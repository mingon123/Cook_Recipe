from flask import Blueprint, request, make_response, jsonify

import mysql.connector

from appmain import app

from appmain.utils import verifyJWT, getJWTContent

reply = Blueprint('reply', __name__)

def get_mysql_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="0000",
        database="recipes",
        auth_plugin='mysql_native_password'
    )

@reply.route('/api/reply/leave', methods=['POST'])
def leaveReply():
    headerData = request.headers
    data = request.form

    authToken = headerData.get("authtoken")

    payload = {"success": False}

    if authToken:
        isValid = verifyJWT(authToken)

        if isValid:
            token = getJWTContent(authToken)
            username = token["username"]

            articleNo = data.get("articleNo")
            reply = data.get("reply")

            conn = get_mysql_connection()
            cursor = conn.cursor()

            if cursor:
                SQL = 'INSERT INTO replies (author, description, targetArticle) VALUES(%s, %s, %s)'
                cursor.execute(SQL, (username, reply, articleNo))
                replyNo = cursor.lastrowid
                conn.commit()

                cursor.close()
            conn.close()

            payload = {"success": True, "replyNo": replyNo, "author": username, "desc": reply}
        else:   # if isValid:
            pass
    else:   # if authToken:
        pass

    return make_response(jsonify(payload), 200)


@reply.route('/api/reply/get', methods=['POST'])
def getReply():
    data = request.form
    articleNo = data["articleNo"]
    baseIndex = data["baseIndex"]
    numReplyRead = data["numReplyRead"]

    payload = {"success": False}

    try:
        conn = get_mysql_connection()
        cursor = conn.cursor()

        if cursor:
            SQL = 'SELECT replyNo, author, description FROM replies WHERE targetArticle=%s \
                        ORDER BY replyNo DESC LIMIT %s, %s'
            cursor.execute(SQL, (articleNo, int(baseIndex), int(numReplyRead)))
            result = cursor.fetchall()

            SQL = 'SELECT COUNT(*) FROM replies WHERE targetArticle=%s'
            cursor.execute(SQL, (articleNo,))
            numTotalReply = cursor.fetchone()[0]

            cursor.close()
        conn.close()

        replies = []

        for reply in result:
            replies.append({"replyNo": reply[0], "author": reply[1], "desc": reply[2]})

        if numTotalReply <= (int(baseIndex) + int(numReplyRead)):
            moreReplies = False
        else:
            moreReplies = True

        payload = {"success": True, "replies": replies, "moreReplies": moreReplies}
    except Exception as err:
        print('[Error]getReply():%s' % err)

    return make_response(jsonify(payload), 200)


@reply.route('/api/reply/delete', methods=['POST'])
def deleteReply():
    headerData = request.headers
    data = request.form

    authToken = headerData.get("authtoken")

    payload = {"success": False}

    if authToken:
        isValid = verifyJWT(authToken)

        if isValid:
            replyNo = data.get("replyNo")

            conn = get_mysql_connection()
            cursor = conn.cursor()

            if cursor:
                SQL = 'DELETE FROM replies WHERE replyNo=%s'
                cursor.execute(SQL, (replyNo,))
                conn.commit()

            payload = {"success": True}
        else:   # if isValid:
            pass
    else:   # if authToken:
        pass

    return make_response(jsonify(payload), 200)