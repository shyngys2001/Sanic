from bson import ObjectId
from flask import current_app
from sanic import Sanic
from sanic.exceptions import NotFound
from pymongo import MongoClient
from django.shortcuts import render
from sanic.response import json as json_response
from umongo import Document
from umongo.fields import *
from umongo.frameworks import MotorAsyncIOInstance
from umongo.frameworks import PyMongoInstance

MONGODB_URI = current_app.config["MONGODB_URI"]
MONGODB_NAME = current_app.config["MONGODB_NAME"]

app = Sanic("project")
settings = dict(
    lazy_umongo=MotorAsyncIOInstance(),
)
app.config.update(settings)
db = MongoClient(
    MONGODB_URI
)[MONGODB_NAME]
instance = PyMongoInstance()
instance.set_db(db)


@app.config.lazy_umongo.register
class News(Document):
    _id = IntegerField(primary_key=True)
    title = StringField(required=True, allow_none=False)
    description = StringField(required=True, allow_none=False)


@app.route("/news_create", methods=["POST"])
async def create_news(request, title, description):
    news = request.json
    news["_id"] = str(ObjectId())
    news["title"] = title
    news["description"] = description

    new_news = await News.insert_one(news)
    created_news = await News.find_one(
        {"_id": new_news.inserted_id}, as_raw=True
    )

    return json_response(created_news)


@app.route("/", methods=["GET"])
async def list_news(request):

    return render('index.html')


@app.route("/<id>", methods=["GET"])
async def read_news(request, _id):
    if (news := await News.find_one({"_id": _id}, as_raw=True)) is not None:
        return json_response(news)

    raise NotFound(f"News {_id} not found")


@app.route("/<id>", methods=["PUT"])
async def update_student(request, _id):
    news = request.json
    update_result = await News.update_one({"_id": _id}, {"$set": {news["title"], news["description"]}})

    if update_result.modified_count == 1:
        if (
                updated_news := await News.find_one({"_id": _id}, as_raw=True)
        ) is not None:
            return json_response(updated_news)

    if (
            existing_news := await News.find_one({"_id": _id}, as_raw=True)
    ) is not None:
        return json_response(existing_news)

    raise NotFound(f"News {_id} not found")


@app.route("/<id>", methods=["DELETE"])
async def delete_news(request, _id):
    delete_result = await News.delete_one({"_id": _id})

    if delete_result.deleted_count == 1:
        return json_response({}, status=204)

    raise NotFound(f"News {_id} not found")


if __name__ == "__main__":
    app.run(host="localhost", port=8000, debug=True)
