from sqlalchemy import Column, Sequence, ForeignKey, String, Integer, Float
from database import Base
from datetime import datetime, date, timedelta
import schema
from .UserModel import User
    
# The Savings tables will store the budget goals and updates for the user to progress towards
# This can be used for reccommendation and finance based itineraries 
class Savings(Base):
    __tablename__ = 'savings'

    email_address = Column(String, ForeignKey('user.email_address'), primary_key=True)
    travel_budget = Column(Float, nullable=False)
    goal = Column(Float, nullable=False)
    period = Column(String, nullable=False)
    goal_per_period = Column(Float, nullable=False)
    progress_per_period = Column(Float, nullable=False)
    start_date = Column(String, nullable=False)
    travel_date = Column(String, nullable=False)

    def __repr__(self):
        return '<Savings: email_address=%s, travel_budget=%s, goal=%s, period=%s, goal_per_period=%s, progress_per_period=%s>' % (
            repr(self.email_address),
            repr(self.travel_budget),
            repr(self.goal),
            repr(self.period),
            repr(self.goal_per_period),
            repr(self.progress_per_period),
            repr(self.start_date),
            repr(self.travel_date)
        )
    
    @classmethod
    def create_savings(cls, db_session, request: schema.SavingsCreate):
        """Create a new savings goal."""
        savings_obj = cls(
            email_address=request.email_address,
            travel_budget=request.travel_budget,
            goal=request.goal,
            period=request.period,
            # goal_per_period=cls.update_goal_per_period(request.goal, request.travel_budget, request.period, request.travel_date),
            goal_per_period=request.goal,
            progress_per_period=0.0,
            start_date=date.today(),
            travel_date=request.travel_date
        )
        db_session.add(savings_obj)
        db_session.commit()
        return savings_obj
    
    @classmethod
    def update_savings(cls, db_session, email_address, request: schema.SavingsCreate):
        """Update an existing savings goal."""
        savings_obj = cls.get_savings_user(db_session, email_address)
        if savings_obj == None:
            return None
        savings_obj.travel_budget = request.travel_budget
        savings_obj.goal = request.goal
        savings_obj.period = request.period
        # goal per period will be updated with progress per period
        savings_obj.progress_per_period = cls.update_progress(request.travel_budget, request.period, request.travel_date)
        savings_obj.start_date = request.start_date
        savings_obj.travel_date = request.travel_date
        db_session.commit()
        return savings_obj
    
    @classmethod
    def add_savings(cls, db_session, email_address, amount):
        """Add the amount to the current budget."""
        savings_obj = cls.get_savings_user(db_session, email_address)
        if savings_obj == None:
            return None
        savings_obj.travel_budget += amount
        savings_obj.progress_per_period += amount
        db_session.commit()
        return savings_obj
    
    @classmethod 
    def get_period(cls, db_session, email_address):
        """Return the period of the savings object."""
        savings_obj = cls.get_savings_user(db_session, email_address)
        if savings_obj == None:
            return None
        return savings_obj.period
    
    @classmethod 
    def get_start_date(cls, db_session, email_address):
        """Return the start date of the savings object."""
        savings_obj = cls.get_savings_user(db_session, email_address)
        if savings_obj == None:
            return None
        return savings_obj.start_date
    
    @classmethod
    def get_savings_user(cls, db_session, email_address):
        """Return the savings object whose user_id is ``id``."""
        return db_session.query(cls).filter_by(email_address=email_address).first()
    
    @classmethod
    def update_goal_per_period(cls, goal, travel_budget, period, travel_date):

        today = date.today()
        d1 = datetime.strptime(today, "%Y/%m/%d")
        d2 = datetime.strptime(travel_date, "%Y/%m/%d")
        remaining_goal = goal - travel_budget

        if (period.lower() == "weekly"):
            return remaining_goal / ((d2 - d1).days / 7)
        elif (period.lower() == "monthly"):
            return remaining_goal / ((d2 - d1).days / 30)
        elif (period.lower() == "yearly"):
            return remaining_goal / ((d2 - d1).days / 365)
        else:
            return None
        
    @classmethod
    def update_progress(cls, db_session, email_address, progress):
        savings_obj = cls.get_savings_user(db_session, email_address)
        if savings_obj is None:
            return None

        savings_obj.progress_per_period += progress
        savings_obj.travel_budget += progress
        savings_obj.goal_per_period = cls.update_goal_per_period(savings_obj.goal, savings_obj.travel_budget, savings_obj.period, savings_obj.travel_date)

        db_session.commit()
        return savings_obj
    
    @classmethod
    def reset_progress_per_period(cls, db_session, email_address): 
        """Reset the progress_per_period to 0 based on the goal and period."""

        savings_obj = cls.get_savings_user(db_session, email_address)

        today = date.today()
        d1 = datetime.strptime(today, "%Y/%m/%d")
        d2 = datetime.strptime(savings_obj.travel_date, "%Y/%m/%d")

        if savings_obj.period.lower() == "weekly":
            if (d2 - d1).days % 7 == 0:
                savings_obj.progress_per_period = 0
        elif savings_obj.period.lower() == "monthly":
            if (d2 - d1).days % 30 == 0:
                savings_obj.progress_per_period = 0
        elif savings_obj.period.lower() == "yearly":
            if (d2 - d1).days % 365 == 0:
                savings_obj.progress_per_period = 0
        else:
            return None

        db_session.commit()
        return savings_obj
        
    @classmethod
    def check_period_success(cls, db_session, email_address):
        """Check if the user has successfully saved enough money for the period."""
        savings_obj = db_session.query(cls).filter_by(email_address=email_address).first()
        if savings_obj.progress_per_period >= savings_obj.goal_per_period:
            return True
        return False
    
    @classmethod
    def check_savings_success(cls, db_session, email_address):
        """Check if the user has successfully saved enough money for the trip."""
        savings_obj = db_session.query(cls).filter_by(email_address=email_address).first()
        if savings_obj.travel_budget >= savings_obj.goal:
            return True
        return False
    
    @classmethod
    def delete_savings(cls, db_session, email_address):
        """Delete the savings object whose user_id is ``id``."""
        savings_obj = cls.get_savings_user(db_session, email_address)
        if savings_obj == None:
            return None
        db_session.delete(savings_obj)
        db_session.commit()
        return savings_obj
     

class Transaction(Base):
    __tablename__ = 'transaction'

    transaction_id = Column(Integer, Sequence('transaction_id_seq'), primary_key=True, autoincrement=True)
    email_address = Column(String, ForeignKey('user.email_address'))
    transaction_date = Column(String, nullable=False)
    transaction_amount = Column(Float, nullable=False)

    def __repr__(self):
        return '<Transaction: transaction_id=%s, email_address=%s, transaction_date=%s, transaction_amount=%s, transaction_type=%s, transaction_category=%s>' % (
            repr(self.transaction_id),
            repr(self.email_address),
            repr(self.transaction_date),
            repr(self.transaction_amount)
        )
    
    @classmethod
    def create_transaction(cls, db_session, request: schema.TransactionCreate):
        """Create a new transaction."""
        transaction_obj = cls(
            email_address=request.email_address,
            transaction_date=request.transaction_date,
            transaction_amount=request.transaction_amount
        )
        db_session.add(transaction_obj)
        db_session.commit()
        return transaction_obj
    
    @classmethod
    def get_transaction_user(cls, db_session, email_address):
        """Return the transaction object whose user_id is ``id``."""
        return db_session.query(cls).filter_by(email_address=email_address).all()
    
    @classmethod
    def delete_transaction(cls, db_session, transaction_id):
        """Delete the transaction object whose transaction_id is ``id``."""
        transaction_obj = cls.get_transaction_user(db_session, transaction_id)
        if transaction_obj == None:
            return None
        db_session.delete(transaction_obj)
        db_session.commit()
        return transaction_obj
    
    @classmethod
    def get_transactions_per_day(cls, db_session, email_address):
        """Return a dictionary of all transactions from a user with the key as the date and value as the amount."""
        transactions = cls.get_transaction_user(db_session, email_address)
        transactions_per_day = []
        for transaction in transactions:
            transaction_date = datetime.strptime(transaction.transaction_date, "%Y-%m-%d")
            transaction_json = {
                'transaction_date': transaction_date.strftime("%Y-%m-%d"),
                'transaction_amount': transaction.transaction_amount
            }
            transactions_per_day.append(transaction_json)
        return transactions_per_day

    @classmethod
    def get_transactions_per_week(cls, db_session, email_address, start_date):
        """Return a list of transactions as JSON objects with the keys 'transaction_date' and 'transaction_amount'."""
        transactions = cls.get_transaction_user(db_session, email_address)
        transactions_per_week = []
        for transaction in transactions:
            transaction_date = datetime.strptime(transaction.transaction_date, "%Y-%m-%d")
            week_start_date = transaction_date - timedelta(days=transaction_date.weekday())
            if week_start_date < start_date:
                continue
            transaction_json = {
                'transaction_date': transaction_date.strftime("%Y-%m-%d"),
                'transaction_amount': transaction.transaction_amount
            }
            transactions_per_week.append(transaction_json)
        return transactions_per_week
    
    @classmethod
    def get_transactions_per_month(cls, db_session, email_address, start_date):
        """Return a list of transactions as JSON objects with the keys 'transaction_date' and 'transaction_amount'."""
        transactions = cls.get_transaction_user(db_session, email_address)
        transactions_per_month = []
        for transaction in transactions:
            transaction_date = datetime.strptime(transaction.transaction_date, "%Y-%m-%d")
            month_start_date = transaction_date.replace(day=1)
            if month_start_date < start_date:
                continue
            transaction_json = {
                'transaction_date': transaction_date.strftime("%Y-%m-%d"),
                'transaction_amount': transaction.transaction_amount
            }
            transactions_per_month.append(transaction_json)
        return transactions_per_month
    
    @classmethod
    def get_transactions_per_year(cls, db_session, email_address, start_date):
        """Return a dictionary of the sum of transactions per year."""
        transactions = cls.get_transaction_user(db_session, email_address)
        transactions_per_year = []
        for transaction in transactions:
            transaction_date = datetime.strptime(transaction.transaction_date, "%Y-%m-%d")
            year_start_date = transaction_date.replace(month=1, day=1)
            if year_start_date < start_date:
                continue
            transaction_json = {
                'transaction_date': transaction_date.strftime("%Y-%m-%d"),
                'transaction_amount': transaction.transaction_amount
            }
            transactions_per_year.append(transaction_json)
        return transactions_per_year
    


