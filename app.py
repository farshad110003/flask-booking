from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
from datetime import datetime, timedelta
import jdatetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # کلید رمزگذاری برای مدیریت جلسه

class BookingSystem:
    def __init__(self):
        self.slots = self.initialize_slots()
        self.disabled_slots = set()

    def initialize_slots(self):
        today = jdatetime.date.today()
        start_date = today + jdatetime.timedelta(days=1)
        end_date = start_date + jdatetime.timedelta(days=13)
        slots = {}
        for day in range((end_date - start_date).days + 1):
            current_date = start_date + jdatetime.timedelta(days=day)
            slots[current_date.strftime('%Y-%m-%d')] = {hour: None for hour in range(9, 21)}
        return slots

    def book_slot(self, date, hour, name, phone):
        if self.slots[date][hour] is None and (date, hour) not in self.disabled_slots:
            self.slots[date][hour] = {'name': name, 'phone': phone}
            return True
        return False

    def toggle_slot(self, date, hour):
        if (date, hour) in self.disabled_slots:
            self.disabled_slots.remove((date, hour))
        else:
            self.disabled_slots.add((date, hour))

    def is_disabled(self, date, hour):
        return (date, hour) in self.disabled_slots

booking_system = BookingSystem()

@app.route('/')
def index():
    slots = booking_system.slots
    disabled_slots = booking_system.disabled_slots
    is_admin = session.get('is_admin', False)
    return render_template('index.html', slots=slots, disabled_slots=disabled_slots, is_admin=is_admin)

@app.route('/book', methods=['POST'])
def book():
    date = request.form['date']
    hour = int(request.form['hour'])
    name = request.form['name']
    phone = request.form['phone']
    if booking_system.book_slot(date, hour, name, phone):
        return redirect(url_for('index'))
    else:
        return "این بازه زمانی قابل رزرو نیست!", 400

@app.route('/toggle', methods=['POST'])
def toggle():
    if not session.get('is_admin', False):
        return "دسترسی غیرمجاز!", 403
    date = request.form['date']
    hour = int(request.form['hour'])
    booking_system.toggle_slot(date, hour)
    return redirect(url_for('index'))

@app.route('/admin_login', methods=['POST'])
def admin_login():
    password = request.form['password']
    if password == '110003': # رمز عبور مدیریت
        session['is_admin'] = True
    return redirect(url_for('index'))

@app.route('/admin_logout', methods=['POST'])
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
