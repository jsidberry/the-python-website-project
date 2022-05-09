from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime, timedelta
# import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # removes FSADeprecationWarning
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id

# headings = ("Day", "Date", "100.00", "700.00","1801.00","10,001.00")
# data = (
#     ("Day-1","May 14, 2022","010.50","710.50","1,835.22","10,271.31"),
#     ("Day-2","May 15, 2022","103.02","712.16","1,870.09","10,548.34"),
# )

def calc_date(initdate, day_increment):
    modified_date = initdate + timedelta(days=day_increment)
    result = modified_date.strftime("%d-%b-%Y")
    return result

def calc_interest(current_dollar_amt, interest_rate, iteration: int):
    x = 1
    new_amt = current_dollar_amt
    for y in range(iteration):
        amt = new_amt + (new_amt * interest_rate)
        # x = x + y
        new_amt = amt
    return str(round(amt,2))

def add_two_place_decimal(dollar):
    if dollar[-2] == '.':
        dollar = (dollar + '0')
    return dollar

def add_commas_to_dollar_amounts(money):
    if len(money) == 7 or len(money) == 8 or len(money) == 9:
        money = (money[:-6] + "," + money[-6:])
    elif len(money) == 10 or len(money) == 11 or len(money) == 12:
        money = (f'{money[:-9]},{money[-9:-6]},{money[-6:]}')
    return money
            


@app.route("/calc")
def calc():
    init_date = datetime.now()
    data = []
    dollar_calc = dict()
    heading_amts = dict()
    dollar_amts = [100,700,1801,750000]
    for item in dollar_amts:
        heading_amts[item] = (str(item) + ".00")
    headings = ("Day", "Date", heading_amts[dollar_amts[0]], heading_amts[dollar_amts[1]], heading_amts[dollar_amts[2]], heading_amts[dollar_amts[3]])
    
    for day_num in range(1,366,1):
        numbered_day = f'day-{str(day_num)}'
        date = calc_date(init_date, day_num)
        for item in dollar_amts:
            x = str(item)
            dollar_calc[x] = calc_interest(int(item), 0.015, day_num)
            dollar_calc[x] = add_two_place_decimal(dollar_calc[x])
            dollar_calc[x] = add_commas_to_dollar_amounts(dollar_calc[x])
                
        data_row = (numbered_day, date, dollar_calc[str(dollar_amts[0])], dollar_calc[str(dollar_amts[1])], dollar_calc[str(dollar_amts[2])], dollar_calc[str(dollar_amts[3])])
        # print(f'{data_row}')
        data.append(data_row)

    return render_template("calc.html", headings=headings, data=data)


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task'

    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks)


@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your task'

    else:
        return render_template('update.html', task=task)


if __name__ == "__main__":
    app.run(debug=True)
