from flask import Flask, request, g, jsonify
from database import get_db
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
auth = HTTPBasicAuth()


@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.username})


@auth.verify_password
@app.route('/auth', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    db = get_db()
    spec_user = db.execute('select * from user where username = ? and password = ?', [username, password])
    user = spec_user.fetchall()
    if not user:
        return jsonify({"Result": "False"}), 200
    g.user = user
    return jsonify({"Result": "True"}), 200


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/users', methods=['POST'])
@auth.login_required
def user_get_all():
    db = get_db()
    user_cur = db.execute('select * from user')
    users = user_cur.fetchall()
    return_values = []
    for user in users:
        user_dict = {}
        user_dict['id'] = user['id']
        user_dict['username'] = user['username']
        user_dict['password'] = user['password']
        user_dict['email'] = user['email']
        user_dict['is_active'] = user['is_active']
        return_values.append(user_dict)

    return jsonify({'users': return_values})


@app.route('/user/add', methods=['POST'])
def user_insert():
    data = request.get_json()
    username = data['username']
    password = data['password']
    email = data['email']
    is_active = data['isactive']
    db = get_db()
    spec_user = db.execute('select * from user where username = ?', [username])
    dup_user = spec_user.fetchall()
    if dup_user:
        return jsonify({'Message': 'Duplicate Username'}), 401
    else:
        db.execute('insert into user(username, password, email, is_active) values (?, ?, ?, ?)', [username, password, email, is_active])
        db.commit()
        user_cur = db.execute('select * from user')
        users = user_cur.fetchall()
        return_values = []
        for user in users:
            user_dict = {}
            user_dict['id'] = user['id']
            user_dict['username'] = user['username']
            user_dict['password'] = user['password']
            user_dict['email'] = user['email']
            user_dict['is_active'] = user['is_active']
            return_values.append(user_dict)

        return jsonify({'users': return_values})


@app.route('/users/edit', methods=['POST'])
def user_edit():
    data = request.get_json()
    user_id = data['user_id']
    username = data['username']
    password = data['password']
    email = data['password']
    is_active = data['is_sactive']
    db = get_db()
    db.execute('update user set username = ?, password = ?, email = ?, is_active = ? where id = ?', [username, password, email, is_active, user_id])
    db.commit()
    user_cur = db.execute('select * from user')
    users = user_cur.fetchall()
    return_values = []
    for user in users:
        user_dict = {}
        user_dict['id'] = user['id']
        user_dict['username'] = user['username']
        user_dict['password'] = user['password']
        user_dict['email'] = user['email']
        user_dict['is_active'] = user['is_active']
        return_values.append(user_dict)

    return jsonify({'users': return_values})


@app.route('/category', methods=['POST'])
def category_get_all():
    db = get_db()
    newscategory_cur = db.execute('select * from newscategory')
    newscategories = newscategory_cur.fetchall()
    return_values = []
    for newscategory in newscategories:
        newscategory_dict = {'id': newscategory['id'], 'title': newscategory['title'], 'is_deleted': newscategory['is_deleted']}
        return_values.append(newscategory_dict)

    return jsonify({'newscategory': return_values})


@app.route('/category/add', methods=['POST'])
def category_add():
    data = request.get_json()
    title = data['title']
    is_deleted = data['is_deleted']
    db = get_db()
    db.execute('insert into newscategory(title,is_deleted) values (?, ?)', [title, is_deleted])
    db.commit()
    newscategory_cur = db.execute('select * from newscategory')
    newcategories = newscategory_cur.fetchall()
    return_values = []
    for category in newcategories:
        newscategory_dict = {'id': category['id'], 'title': category['title'], 'is_deleted': category['is_deleted']}
        return_values.append(newscategory_dict)

    return jsonify({'newscategory': return_values})


@app.route('/news', methods=['GET'])
def news_get_all():
    db = get_db()
    news_cur = db.execute(('select n.*, u.username, ng.title as categoryname from news n left join user u on n.user_id = u.id left join newscategory ng on n.category_id = ng.id'))
    news = news_cur.fetchall()
    return_values = []
    for new in news:
        news_dict = {'id': new['id'], 'title': new['title'], 'body': new['body'], 'is_deleted': new['is_deleted'],
                     'create_date': new['createdate'], 'image_url': new['image'], 'username': new['username'], 'categoryname': new['categoryname']}
        return_values.append(news_dict)

    return jsonify({'news': return_values})


@app.route('/news/add', methods=['POST'])
def news_insert():
    data = request.get_json()
    title = data['title']
    created_date = data['created_date']
    category_id = data['category_id']
    body = data['body']
    is_deleted = data['is_deleted']
    image_url = data['image_url']
    user_id = data['user_id']

    db = get_db()
    db.execute('insert into news(title, createdate, category_id, body, is_deleted, image, user_id) '
                        'values (?, ?, ?, ?, ?, ?, ?)', [title, created_date, category_id, body, is_deleted, image_url, user_id])
    db.commit()
    news_cur = db.execute('select n.*, u.username, ng.title as categoryname from news n inner join user u on n.user_id = u.id inner join newscategory ng on n.category_id = ng.id')
    news = news_cur.fetchall()
    return_values = []
    for new in news:
        news_dict = {'id': new['id'], 'title': new['title'], 'body': new['body'], 'is_deleted': new['is_deleted'],
                     'create_date': new['createdate'], 'image_url': new['image'], 'username': new['username'], 'categoryname': new['categoryname']}
        return_values.append(news_dict)

    return jsonify({'news': return_values})


@app.route('/news/edit', methods=['POST'])
def news_update():
    data = request.get_json()
    news_id = data['news_id']
    title = data['title']
    category_id = data['category_id']
    body = data['body']
    is_deleted = data['created_date']

    db = get_db()
    db.execute('update news set title = ?, category_id = ?, body = ?, is_deleted = ? where id = ?', [title, category_id, body, is_deleted, news_id])
    db.commit()
    news_cur = db.execute('select n.*, u.username, ng.title as categoryname from news n inner join user u on n.user_id = u.id inner join newscategory ng on n.category_id = ng.id ')
    news = news_cur.fetchall()
    return_values = []
    for new in news:
        news_dict = {'id': new['id'], 'title': new['title'], 'body': new['body'], 'is_deleted': new['is_deleted'],
                             'create_date': new['create_date'], 'image_url': new['image'], 'username': new['username'], 'categoryname': new['categoryname']}
        return_values.append(news_dict)

    return jsonify({'news': return_values})


if __name__ == '__main__':
    app.run()
