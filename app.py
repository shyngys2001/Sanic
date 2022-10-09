from bson import ObjectId
from sanic import Sanic, response
from pymongo import MongoClient
from sanic_ext import render
from umongo.frameworks import PyMongoInstance

MONGODB_URI = 'mongodb+srv://h4ww:98mUStcarE@forcourier.cfbnpsh.mongodb.net/?retryWrites=true&w=majority'
MONGODB_NAME = 'sample_prog'

app = Sanic("project")
app.static('/static', './static')

db = MongoClient(
    MONGODB_URI
)[MONGODB_NAME]
instance = PyMongoInstance()
instance.set_db(db)


@app.route("/", methods=["GET"])
async def list_news(request):
    all_news = list(db.news.find({}, {'title': 1, 'photo': 1, 'content': 1}))
    return await render('news.html', context={'all_news': all_news})


@app.route("/create", methods=["POST", "GET"])
async def create_news(request):
    action = request.form.get('action')
    if action == 'create':
        photo = request.files.get('photo', None)
        if photo:
            file_content = photo.body
            hashing = hash(photo)
            open(f'static/media/{hashing}.png', 'wb').write(file_content)
            create = {
                'title': request.form.get('title'),
                "content": request.form.get('content'),
                'photo': f"{hashing}.png"
            }
            db.news.insert_one(create)
        return response.redirect('/')
    return await render('add_news.html')


@app.route("/<nid>", methods=["POST", "GET"])
async def read_news(request, nid):
    news = db.news.find_one({"_id": ObjectId(nid)}, {'title': 1, 'photo': 1, 'content': 1})

    return await render('news_id.html', context={"news": news})


@app.route("/update/<nid>", methods=["POST", "GET"])
async def update_student(request, nid):
    news = db.news.find_one({"_id": ObjectId(nid)}, {'title': 1, 'photo': 1, 'content': 1})
    action = request.form.get('action')
    if action == 'update':
        photo = request.files.get('photo', None)
        if photo:
            file_content = photo.body
            hashing = hash(photo)
            open(f'static/media/{hashing}.png', 'wb').write(file_content)
            db.news.update_one(
                {'_id': ObjectId(nid)},
                {'$set': {'title': request.form.get('title'), 'photo': f'{hashing}.png',
                          'content': request.form.get('content')}}
            )
            return response.redirect('/')
        elif request.form.get('title') and request.form.get('content'):
            db.news.update_one(
                {'_id': ObjectId(nid)},
                {'$set': {'title': request.form.get('title'), 'content': request.form.get('content')}}
            )
            return response.redirect('/')
        elif request.form.get('title'):
            db.news.update_one(
                {'_id': ObjectId(nid)},
                {'$set': {'title': request.form.get('title')}}
            )
            return response.redirect('/')
        elif request.files.get('photo'):
            file_content = photo.body
            hashing = hash(photo)
            open(f'static/media/{hashing}.png', 'wb').write(file_content)
            db.news.update_one(
                {'_id': ObjectId(nid)},
                {'$set': {'photo': f'{hashing}.png'}}
            )
            return response.redirect('/')
        elif request.form.get('title') and request.files.get('photo'):
            file_content = photo.body
            hashing = hash(photo)
            open(f'static/media/{hashing}.png', 'wb').write(file_content)
            db.news.update_one(
                {'_id': ObjectId(nid)},
                {'$set': {'title': request.form.get('title'), 'photo': f'{hashing}.png'}}
            )
            return response.redirect('/')
        elif request.files.get('photo') and request.form.get('content'):
            file_content = photo.body
            hashing = hash(photo)
            open(f'static/media/{hashing}.png', 'wb').write(file_content)
            db.news.update_one(
                {'_id': ObjectId(nid)},
                {'$set': {'photo': f'{hashing}.png', 'content': request.form.get('content')}}
            )
            return response.redirect('/')
        elif request.form.get('content'):
            db.news.update_one(
                {'_id': ObjectId(nid)},
                {'$set': {'title': request.form.get('title')}}
            )
            return response.redirect('/')
    return await render('update_news.html', context={'news': news})


@app.route("/delete/<nid>", methods=["POST", "GET"])
async def delete_news(request, nid):
    news = db.news.find_one({"_id": ObjectId(nid)}, {'title': 1, 'photo': 1, 'content': 1})
    action = request.form.get('action')
    if action == 'delete':
        db.news.delete_one({'_id': ObjectId(nid)})
        return response.redirect('/')
    return await render('delete_news.html', context={'news': news})


if __name__ == "__main__":
    app.run(host="localhost", port=8000, debug=True)
