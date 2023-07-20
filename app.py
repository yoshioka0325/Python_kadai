from flask import Flask, render_template, request, url_for, redirect, session
import db, string, random
from datetime import timedelta

app = Flask(__name__)
app.secret_key = ''.join(random.choices(string.ascii_letters, k=256))

@app.route('/book_register')
def tosho_register():
    return render_template('tosho_register.html')

@app.route('/book_delete')
def tosho_delete():
    return render_template('tosho_delete.html')

@app.route('/', methods=['GET'])
def index():
    msg = request.args.get('msg')
    
    if msg == None:
        return render_template('index.html')
    else :
        return render_template('index.html', msg=msg)

@app.route('/', methods=['POST'])
def login():
    user_name = request.form.get('username')
    password = request.form.get('password')
    
    if db.login(user_name, password):
        session['user'] = True
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=30)
        return redirect(url_for('mypage'))
    else :
        error = 'ログインに失敗しました。'
        input_data = {
            'user_name':user_name,
            'password':password
        }
        return render_template('index.html', error=error, data=input_data)
    
@app.route('/mypage',methods=['GET'])
def mypage():
    if 'user' in session:
        return render_template('mypage.html')
    else :
        return redirect(url_for('index'))
    
@app.route('/register')
def register_form():
    return render_template('register.html')

@app.route('/register_exe', methods=['POST'])
def register_exe():
    user_name = request.form.get('username')
    password = request.form.get('password')
    
    if user_name == '':
        error = 'ユーザ名が未入力です。'
        return render_template('register.html', error=error, user_name=user_name, password=password)
    if password == '':
        error = 'パスワードが未入力です。'
        return render_template('register.html', error=error)
    
    count = db.insert_user(user_name, password)
    
    if count == 1:
        msg = '登録が完了しました。'
        return redirect(url_for('index', msg=msg))
    else:
        error = '登録に失敗しました。'
        return render_template('register.html', error=error)
    
    
@app.route('/book/add', methods=['GET', 'POST'])
def book_add():
    if request.method == 'POST':
        name = request.form.get('name')
        author = request.form.get('author')
        publisher = request.form.get('publisher')
        isbn = request.form.get('isbn')
        
        if db.is_book_isbn_taken(isbn):
            error = '同じISBN番号の本が既に登録されています。別のISBN番号を入力してください。'
            return render_template('tosho_register.html', error=error)
        count = db.insert_book(name, author, publisher, isbn)
        if count == 1:
            msg='本が登録されました'
            return render_template('tosho_register.html', msg=msg)
        else:
            error = '本の登録に失敗しました。'
            return render_template('tosho_register.html', error=error)
    return render_template('tosho_register.html')  

@app.route('/book_delete', methods=['POST'])
def book_delete():
    id= request.form.get('id')
    db.delete_book(id)
    return render_template('delete_sucsess.html')  

@app.route('/booklist')
def tosho_list():
    book_list = db.select_all_books()
    return render_template('tosho_list.html', book=book_list)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)