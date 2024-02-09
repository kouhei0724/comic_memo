# Description: マンガのリストを表示するアプリケーション
# データベースはMariaDBを使用
# データベースのテーブル名はcomic
# テーブルのカラムはcomic_id, comic_image, comic_title, comic_author, comic_purchased
# comic_idは主キーでautoincrement
# comic_imageはマンガの画像のURL
# comic_titleはマンガのタイトル
# comic_authorはマンガの作者
# comic_purchasedはマンガを購入済みかどうかのフラグ

from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import asyncio

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)

# データベースの設定
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://masa:masa0528@100.67.234.65/list'

try:
    db = SQLAlchemy(app)
except SQLAlchemyError as e:
    error = str(e.__dict__['orig'])
    print(error)

class Comic(db.Model):
    __tablename__ = 'comic'
    comic_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    comic_image = db.Column(db.String(255))
    comic_title = db.Column(db.String(255), nullable=False)
    comic_author = db.Column(db.String(255), nullable=False)
    comic_purchased = db.Column(db.Boolean, nullable=False, default=False)

@app.route('/')
def home():
    """
    トップページを表示する
    """
    return render_template('main.html')

async def get_manga_list():
  """
  データベースからマンガのリストを取得する
  """
  manga_list = []
  comics = Comic.query.all()
  for comic in comics:
    manga_list.append({
      "comic_id": comic.comic_id,
      "comic_image": comic.comic_image,
      "comic_title": comic.comic_title,
      "comic_author": comic.comic_author,
      "comic_purchased": comic.comic_purchased,
    })
  return manga_list

@app.route('/list')
def list():
    """
    マンガのリストを表示する
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    manga_list = loop.run_until_complete(get_manga_list())
    return render_template('list.html', manga_list=manga_list)

# マンガの追加
class AddForm(FlaskForm):
    comic_image = StringField('画像URL', validators=[DataRequired()])
    comic_title = StringField('タイトル', validators=[DataRequired()])
    comic_author = StringField('作者', validators=[DataRequired()])
    comic_purchased = StringField('購入済み', validators=[DataRequired()])

# マンガの追加
@app.route('/add', methods=['GET', 'POST'])
def add():
    form = AddForm()
    if form.validate_on_submit():
        comic = Comic(
            comic_image=form.comic_image.data,
            comic_title=form.comic_title.data,
            comic_author=form.comic_author.data,
            comic_purchased=form.comic_purchased.data,
        )
        db.session.add(comic)
        db.session.commit()
        return redirect(url_for('list'))
    return render_template('add.html', form=form)

if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = 5000, debug = True)
    