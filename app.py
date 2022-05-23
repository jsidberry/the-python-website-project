from curses import raw
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime, timedelta
import pprint as pp
# import SQLAlchemy
from forms import RegistrationForm, LoginForm

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # removes FSADeprecationWarning
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = '4b39b1b88a8ed15cf284911793c2134f'


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id


def calc_date(initdate, day_increment):
    modified_date = initdate + timedelta(days=day_increment)
    result = modified_date.strftime("%d-%b-%y")
    return result

def calc_interest(current_dollar_amt: int, iteration: int):
    new_amt = current_dollar_amt
    for item in range(iteration):
        if new_amt > 74 and new_amt < 1801:
            interest_rate = 0.015
        elif new_amt > 1800 and new_amt < 10001:
            interest_rate = 0.019
        elif new_amt > 10000 and new_amt < 75001:
            interest_rate = 0.027
        else:
            interest_rate = 0.032
        amt = new_amt + (new_amt * interest_rate)
        new_amt = amt
    # print(type(round(amt,2)))
    return str(round(amt,2))


def add_two_place_decimal(dollar):
    if dollar[-2] == '.':
        dollar = (dollar + '0')
    return dollar


def add_commas_to_dollar_amounts(money):
    if len(money) < 7:
        results = money
    # elif len(money) < 7 and money[-3] == '.':
    #     results = (money + '0')
    elif len(money) == 7 or len(money) == 8 or len(money) == 9:
        results = (money[:-6] + "," + money[-6:])
    elif len(money) == 10 or len(money) == 11 or len(money) == 12:
        results = (f'{money[:-9]},{money[-9:-6]},{money[-6:]}')
    # elif len(money) == 13 or len(money) == 14 or len(money) == 15:
    else:
        results = (f'{money[:-12]},{money[-12:-9]},{money[-9:-6]},{money[-6:]}')
    return results


def dollar_list_html(dollar_int, dollar_str, day_num, date_num):
    html_list = [('table__cell',day_num),('table__cell', date_num)]

    for item in dollar_int:
        item_tmp = float(item)
        item_int = (f'%.2f' % item_tmp)

        for item_str in dollar_str:
            if item_str == add_commas_to_dollar_amounts(str(item_int)):
                if item_tmp < 1801.00:
                    html_class = 'table__cell_1pt5'
                elif item_tmp < 10001.00:
                    html_class = 'table__cell_1pt9'
                elif item_tmp < 75001.00:
                    html_class = 'table__cell_2pt7'
                elif item_tmp < 1000000.00:
                    html_class = 'table__cell_3pt2'
                elif item_tmp < 10000000.00:
                    html_class = 'table__cell_1m'
                elif item_tmp is not None:
                    html_class = 'table__cell_1b'
                html_list.append((html_class,item_str))

    return html_list


@app.route('/', methods=['POST', 'GET'])
def index():
    init_date = datetime.now()
    data = []
    datum = []
    html_list = []
    dollar_calc = dict()
    dollar_intg = dict()
    day_date = ["Day","Date"]
    dollar_amts = [100,700,1801,10001,75001,100000]
    day_range = 366
    dollars = []
    dollar_list = []

    # table-header dataset
    dollars = [f'${str(dollar_amt)}.00' for dollar_amt in dollar_amts]
    headings = tuple(day_date + dollars)
    
    # table-data dataset 
    for day_num in range(1,day_range,1):
        numbered_day = f'day-{str(day_num)}'
        date = calc_date(init_date, day_num)

        for dollar_amt in dollar_amts:
            dollar_calc[str(dollar_amt)] = add_commas_to_dollar_amounts(
                                                add_two_place_decimal(
                                                    calc_interest(int(dollar_amt), day_num)
                                                )
            )
            dollar_intg[str(dollar_amt)] = calc_interest(int(dollar_amt), day_num)

        dollar_list = [dollar_calc[item] for item in dollar_calc]
        dollar_html = [dollar_intg[item] for item in dollar_intg]
        html_td_list = dollar_list_html(dollar_html, dollar_list, numbered_day, date)

        data.append(tuple([numbered_day] + [date] + dollar_list))
        datum.append(html_td_list)  
        dollar_html.clear()
        dollar_list.clear()

    return render_template("index.html", headings=headings, data=datum, dollar_amts=dollar_amts)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    return render_template('register.html', title="Register", form=form)

@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', title="Login", form=form)

if __name__ == "__main__":
    app.run(debug=True)
