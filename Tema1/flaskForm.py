from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import oneapi
import logging

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'


class ReusableForm(Form):
    Gname = StringField('Genre:', validators=[validators.required()])
    Mname = StringField('Movie:')

movies=[]
@app.route("/", methods=['GET', 'POST'])
def hello():
    form = ReusableForm(request.form)
    showName = True
    global movies
    print(form.errors)
    if request.method == 'POST':
        genreName = request.form['Gname']
        movieName = request.form['Mname']
        print(genreName)

        if movieName:
            videos=oneapi.GetVideos(movieName)
            for i in videos:
                i=("https://www.youtube.com/watch?v="+i[0],i[1])
                flash(i,"videos")
            review=oneapi.GetReview(movieName)
            review=oneapi.processReview(review)
            for i in review:
                print(i[0])
                if i[0]>0:
                    i=('green',i[1])
                elif i[0]==0:
                    i=('yellow',i[1])
                else:
                    i=('red',i[1])
                flash(i,"reviews")
            comments=oneapi.GetComments(videos[0][0])
            comments=oneapi.processReview(comments)
            for i in comments:
                print(i[0])
                if i[0]>0:
                    i=('green',i[1])
                elif i[0]==0:
                    i=('yellow',i[1])
                else:
                    i=('red',i[1])
                flash(i,"comments")

        if form.validate():
            movies=oneapi.GetMovies(genreName)
           # showName=True
            #print(movies,name)
            # Save the comment here.
            for i in movies:
                flash(i[1],"movienames")
            #flash('Bye ' + name)
        else:
            flash('All the form fields are required. ')


    return render_template('index.html',showName=showName, form=form)


if __name__ == "__main__":
    logging.basicConfig(filename='requests.log',level=logging.DEBUG)
    app.run()
