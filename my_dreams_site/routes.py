
from app import app, db, login_manager  
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from forms import RegistrationForm, LoginForm, PurchaseForm, GoalForm, ContributionForm
from models import User, Purchase, Goal, Contribution, POPULAR_CATEGORIES
from datetime import datetime, timedelta

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
@app.route("/home")
@login_required
def home():
    # Рассчитаем общий баланс
    total_contributions = sum(c.amount for c in current_user.contributions)
    total_purchases = sum(p.amount for p in current_user.purchases)
    balance = total_contributions - total_purchases
    return render_template('home.html', balance=balance)



@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Проверяем, существует ли уже пользователь с указанным email
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user and existing_user.password == form.password.data:  # Проверка на совпадение пароля
            flash('Такой аккаунт уже существует! Попробуйте войти в систему.', 'danger')
            return redirect(url_for('login'))  # Перенаправление на страницу входа

        # Если пользователь не существует, создаем нового
        user = User(email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('Ваш аккаунт успешно создан!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('home'))
        flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/add_purchase", methods=['GET', 'POST'])
@login_required
def add_purchase():
    form = PurchaseForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            purchase = Purchase(
                user_id=current_user.id,
                category=form.category.data,
                amount=form.amount.data
            )
            db.session.add(purchase)
            db.session.commit()
            flash('Purchase added!', 'success')
            return redirect(url_for('add_purchase'))
    form.category.choices = [(category, category) for category in POPULAR_CATEGORIES]  # Установка списка категорий
    return render_template('add_purchase.html', form=form)


@app.route("/goals", methods=['GET', 'POST'])
@login_required
def goals():
    form = GoalForm()
    current_goal = Goal.query.filter_by(user_id=current_user.id).first()  # Получение текущей цели пользователя
    total_contributions = sum(c.amount for c in current_user.contributions)  # Сумма всех взносов
    current_amount = total_contributions * 0.20  # 20% от взносов идут на цель

    if form.validate_on_submit():
        # Если есть текущая цель, удаляем её
        if current_goal:
            db.session.delete(current_goal)  # Удаление текущей цели из базы данных

        # Создание новой цели
        new_goal = Goal(
            user_id=current_user.id,
            target_amount=form.target_amount.data,
            dream_name=form.dream_name.data  # Получение названия мечты
        )
        db.session.add(new_goal)  # Добавляем новую цель
        db.session.commit()  # Коммитим изменения в базе данных
        flash('Goal set!', 'success')
        return redirect(url_for('goals'))

    # Передаем форму, текущую цель и сумму накоплений в шаблон
    return render_template('goals.html', form=form, goal=current_goal, current_amount=current_amount)


@app.route('/loan_calculator', methods=['GET', 'POST'])
def loan_calculator():
    error = None
    results = None
    
    if request.method == 'POST':
        try:
            # Получаем данные формы
            P = float(request.form['loan_amount'])
            n = int(request.form['period_months'])
            annual_rate = float(request.form['annual_rate'])
            if P <= 0 or n <= 0 or annual_rate < 0:
                error = "Пожалуйста, введите корректные значения."
            else:
                # Расчет
                i = annual_rate / 100 / 12  # месячная ставка
                if i == 0:
                    monthly_payment = P / n
                else:
                    monthly_payment = P * (i / (1 - (1 + i) ** (-n)))
                total_payment = monthly_payment * n
                overpayment = total_payment - P

                results = {
                    'monthly_payment': f"{monthly_payment:,.2f}".replace(',', ' '),
                    'total_payment': f"{total_payment:,.2f}".replace(',', ' '),
                    'overpayment': f"{overpayment:,.2f}".replace(',', ' '),
                    'period_months': n,
                    'annual_rate': f"{annual_rate:.2f}"
                }
        except ValueError:
            error = 'Некорректный формат данных.'

    return render_template('loan_calculator.html', results=results, error=error)



@app.route("/add_contribution", methods=['GET', 'POST'])
@login_required
def add_contribution():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        new_contribution = Contribution(amount=amount, contributor=current_user)
        db.session.add(new_contribution)
        db.session.commit()
        flash('Contribution added!', 'success')
        return redirect(url_for('home'))
    return render_template('add_contribution.html')

@app.route("/goal_progress/<int:goal_id>", methods=['GET'])
@login_required
def goal_progress(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    progress = (goal.current_amount / goal.target_amount) * 100 if goal.target_amount > 0 else 0
    return render_template('goal_progress.html', progress=progress, goal=goal)



@app.route("/expense_analysis", methods=['GET'])
@login_required
def expense_analysis():
    last_month = datetime.now() - timedelta(days=30)
    purchases_last_month = Purchase.query.filter(Purchase.owner == current_user, Purchase.timestamp >= last_month).all()
    category_totals = {}
    total_expense = 0
    for purchase in purchases_last_month:
        if purchase.category in category_totals:
            category_totals[purchase.category] += purchase.amount
        else:
            category_totals[purchase.category] = purchase.amount
        total_expense += purchase.amount
    return render_template('expense_analysis.html', category_totals=category_totals, total_expense=total_expense)



@app.route("/income_distribution", methods=['GET'])
@login_required
def income_distribution():
    contributions = Contribution.query.filter_by(user_id=current_user.id).all()
    total_income = sum(contribution.amount for contribution in contributions)


    savings = total_income * 0.20    # 20% на сбережения
    consumption = total_income * 0.50  # 50% на потребление
    dreams = total_income * 0.30      # 30% на мечты
    
    return render_template('income_distribution.html', total_income=total_income, savings=savings, consumption=consumption, dreams=dreams)
