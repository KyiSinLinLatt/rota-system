import os
import sqlalchemy as sa
import pandas as pd
from pywebio import *
from pywebio.pin import *
from pywebio.input import *
from pywebio.output import *
from pywebio import start_server
from pywebio.output import put_html
from pywebio.output import clear
from pywebio.session import CoroutineBasedSession
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker, declarative_base, Session
from datetime import date
from sqlalchemy import Date
from jinja2 import Template
from datetime import timedelta

#Get the absolute path of the script's directory
base_dir = os.path.dirname(os.path.abspath(__file__))

#Construct the path to the 'db' folder dynamically
employee_path = os.path.join(base_dir, "db", "employee.xlsx")
senior_path = os.path.join(base_dir, "db", "senior.xlsx")
junior_path = os.path.join(base_dir, "db", "junior.xlsx")
availability_path = os.path.join(base_dir, "db", "availability.xlsx")
shift_requirements_path = os.path.join(base_dir, "db", "shiftRequirements.xlsx")

#### DATABASE SETUP ####
employeeImport = pd.read_excel(employee_path, engine="openpyxl")
seniorImport = pd.read_excel(senior_path, engine='openpyxl')
juniorImport = pd.read_excel(junior_path, engine='openpyxl')
availabilityImport = pd.read_excel(availability_path, engine='openpyxl')
shiftRequirementsImport = pd.read_excel(shift_requirements_path, engine='openpyxl')

# Remove any extra unnamed columns:
employeeImport = employeeImport.loc[:, ~employeeImport.columns.str.contains('^Unnamed')]
seniorImport = seniorImport.loc[:, ~seniorImport.columns.str.contains('^Unnamed')]
juniorImport = juniorImport.loc[:, ~juniorImport.columns.str.contains('^Unnamed')]
availabilityImport = availabilityImport.loc[:, ~availabilityImport.columns.str.contains('^Unnamed')]
shiftRequirementsImport = shiftRequirementsImport.loc[:, ~shiftRequirementsImport.columns.str.contains('^Unnamed')]

#Creating a SQLite Database 'rota-system.db' with SQLAlchemy
sqlite_file_name = "rota-system.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
db = sa.create_engine(sqlite_url, echo=True)
Session = sessionmaker(bind=db)
Base = declarative_base()

with db.connect() as connection:
    connection.execute(sa.text("DROP TABLE IF EXISTS employee"))
    connection.execute(sa.text("DROP TABLE IF EXISTS senior"))
    connection.execute(sa.text("DROP TABLE IF EXISTS junior"))
    connection.execute(sa.text("DROP TABLE IF EXISTS availability"))
    connection.execute(sa.text("DROP TABLE IF EXISTS shiftRequirements"))
    connection.execute(sa.text("DROP TABLE IF EXISTS shiftAssignments"))
    connection.execute(sa.text("DROP TABLE IF EXISTS assignedHours"))

#Defining the Employee class with table name 'employee'
class Employee(Base):
    """
    Employee class to define the structure of the 'employee' table
    :param Base: Base class from SQLAlchemy to inherit from
    :var id: Employee Numbers
    :var employeeID: Employee ID, the primary key of the table which is unique
    :var name: Employee Name
    :var niNum: Employee's National Insurance Number, this must be unique
    :var homeAddress: Employee's Home Address
    :var phNum: Employee's Phone Number, this must be unique 
    """
    __tablename__ = 'employee'

    id: Mapped[int]
    employeeID: Mapped[int] = mapped_column(primary_key=True, unique=True)
    name: Mapped[str] 
    niNum: Mapped[str] = mapped_column(unique=True)
    homeAddress: Mapped[str]
    phNum: Mapped[str] = mapped_column(unique=True)

#Defining the Senior class with table name 'senior'
class Senior(Base):
    """
    Senior class to define the structure of the 'senior' table
    :param Base: Base class from SQLAlchemy to inherit from
    :var seniorID: Senior Employees ID, the primary key of the table which is unique
    :var employeeID: Employee ID, Connect to employee table as a foreign key to the employeeID of "employee" table
    """
    __tablename__ = 'senior'

    seniorID: Mapped[int] = mapped_column(primary_key=True, unique=True)
    employeeID: Mapped[int] = mapped_column(ForeignKey("employee.employeeID"))

#Defining the Junior class with table name 'junior'
class Junior(Base):
    """
    Junior class to define the structure of the 'junior' table
    :param Base: Base class from SQLAlchemy to inherit from
    :var juniorID: Junior Employees ID, the primary key of the table which is unique
    :var employeeID: Employee ID, Connect to employee table as a foreign key to the employeeID of "employee" table
    """
    __tablename__ = 'junior'

    juniorID: Mapped[int] = mapped_column(primary_key=True, unique=True)
    employeeID: Mapped[int] = mapped_column(ForeignKey("employee.employeeID"))

#Defining the Availability class with table name 'availability'
class Availability(Base):
    """
    Availability class to define the structure of the 'availability' table
    :param Base: Base class from SQLAlchemy to inherit from
    :var availableID: Available ID, the primary key of the table which is unique
    :var employeeiD: Employee ID, Connect to employee table as a foreign key to the employeeID of "employee" table
    :var mon: Availability on Monday
    :var tues: Availability on Tuesday
    :var wed: Availability on Wednesday
    :var thurs: Availability on Thursday
    :var fri: Availability on Friday
    :var sat: Availability on Saturday
    :var sun: Availability on Sunday
    :var weekDate: Start Date of the Week
    """
    __tablename__ = 'availability'

    availableID: Mapped[int] = mapped_column(primary_key=True, unique=True)
    employeeID: Mapped[int] = mapped_column(ForeignKey("employee.employeeID"))
    mon: Mapped[str] 
    tues: Mapped[str] 
    wed: Mapped[str] 
    thurs: Mapped[str] 
    fri: Mapped[str] 
    sat: Mapped[str] 
    sun: Mapped[str] 
    weekDate: Mapped[date] = mapped_column(Date)

#Defining the ShiftRequirements class with table name 'shiftRequirements'
class ShiftRequirements(Base):
    """
    ShiftRequirements class to define the structure of the 'shiftRequirements' table
    :param Base: Base class from SQLAlchemy to inherit from
    :var shiftID: Shift ID, the primary key of the table which is unique
    :var dayOfWeek: Name of the Day of the Week
    :var shiftType: the Type of the Shift which is Day Shift or Night Shift
    :var requiredSenior: Number of Required Senior Staff
    :var requiredJunior: Number of Required Junior Staff
    :var weekDate: Start Date of the Week
    """
    __tablename__ = 'shiftRequirements'

    shiftID: Mapped[int] = mapped_column(primary_key=True, unique=True)
    dayOfWeek: Mapped[str]
    shiftType: Mapped[str]
    requiredSenior: Mapped[int]
    requiredJunior: Mapped[int]
    weekDate: Mapped[date] = mapped_column(Date)

#Defining the ShiftAssignments class with table name 'shiftAssignments'
class ShiftAssignments(Base):
    """
    ShiftAssignments class to define the structure of the 'shiftAssignments' table
    :param Base: Base class from SQLAlchemy to inherit from
    :var assignmentID: Shift Assignment ID, the primary key of the table which is unique
    :var employeeID: Employee ID, Connect to employee table as a foreign key to the employeeID of "employee" table
    :var shiftID: Shift ID, Connect to shiftRequirements table as a foreign key to the shiftID of "shiftRequirements" table
    :var assignedHours: Total Number of Assigned Hours
    """
    __tablename__ = 'shiftAssignments'

    assignmentID: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)
    employeeID: Mapped[int] = mapped_column(ForeignKey("employee.employeeID"))
    shiftID: Mapped[int] = mapped_column(ForeignKey("shiftRequirements.shiftID"))

class AssignedHours(Base):
    """
    AssignedHours class to define the structure of the 'assighedHours' table
    :param Base: Base class from SQLAlchemy to inherit from
    :var employeeID: Employee ID, Connect to shiftAssignments table as a foreign key to the employeeID of "shiftAssignments" table, the primary key of the table
    :var weekDate: Start Date of the Week, Connect to availability table as a foreign key to the weekDate of "availability" table, the primary key of the table
    :var totalHours: Total Working Hours of the Employee
    """
    __tablename__ = 'assignedHours'

    employeeID: Mapped[int] = mapped_column(ForeignKey("shiftAssignments.employeeID"), primary_key=True)
    weekDate: Mapped[date] = mapped_column(ForeignKey("availability.weekDate"), primary_key=True)
    totalHours: Mapped[int]    

#Create tables IMMEDIATELY after dropping them
Base.metadata.create_all(db)

class ShiftAssigned:
    def __init__(self, session, all_seniors, all_juniors, latest_date):
        """
        Initialize the ShiftAssigned
        :param session: SQLAlchemy session
        :param all_seniors: List of senior employees
        :param all_juniors: List of junior employees
        :param latest_date: Latest week date in the shiftRequirements table
        """
        self.session = session
        self.all_seniors = all_seniors
        self.all_juniors = all_juniors
        self.latest_date = latest_date

    def assign_shift(self, day_name, shift_type, actual_staff_counter, required_staff_counter, employee_type, employee_ID):
        """
        Assigns a shift to an employee.
        :param day_name: Name of the day (e.g., Monday)
        :param shift_type: Shift type (e.g., D1, N1, N2)
        :param actual_staff_counter: Counter for actual assigned employee
        :param required_staff_counter: Counter for required employee
        :param employee_type: Either senior or junior
        :return: Updated counters (actual_staff_counter, required_staff_counter)
        """

        #Retrieve the data from senior and junior table 
        if employee_type == "senior":
            employee_list = self.all_seniors
        elif employee_type == "junior":
            employee_list = self.all_juniors
        else: 
            return actual_staff_counter, required_staff_counter
        
        #Skip if the employee is not in the list
        if employee_ID not in employee_list:
            return actual_staff_counter, required_staff_counter
        
        #Remove the employee from the list
        employee_list.remove(employee_ID)

        #Find the matching shift ID
        shift = self.session.query(ShiftRequirements).filter(
            ShiftRequirements.dayOfWeek == day_name,
            ShiftRequirements.shiftType == shift_type,
            ShiftRequirements.weekDate == self.latest_date
        ).first()

        #Assign all the data into the shiftAssignment table
        if shift:
            new_assignment = ShiftAssignments(
                employeeID = employee_ID,
                shiftID = shift.shiftID
            )

            #Add the data into the database table
            self.session.add(new_assignment)
            self.session.commit()

            #Update staff counters
            actual_staff_counter += 1
            required_staff_counter = max(0, required_staff_counter - 1) #Prevent negative values

            #Check whether the employee has assigned in the table
            add_hours = self.session.query(AssignedHours).filter(
                AssignedHours.employeeID == employee_ID,
                AssignedHours.weekDate == self.latest_date
            ).first()

            #Add 5 hours to the total hours of the employee if already exist
            if add_hours:
                add_hours.totalHours += 5
            
            #Add the data into the database table if it is not existed yet
            else:
                new_assigned_hours = AssignedHours(
                    employeeID = employee_ID,
                    weekDate = self.latest_date,
                    totalHours = 5
                )
                self.session.add(new_assigned_hours)
            
            self.session.commit()
            self.session.expire_all()
        return actual_staff_counter, required_staff_counter

    def checking_constraints(self, employee_type, required_staff, actual_staff, 
                             availability_day, shift_types, all_employees, day_name):
        """
        General method for checking constraints for both senior and junior
        :param employee_type: Either senior or junior
        :param required_staff: Total required staff per shift
        :param actual_staff: Total actual assigned staff per shift
        :param availability_day: Day Name 
        :param shift_types: List of shift types (D1, N1, N2)
        :param all_employees: List of either senior or junior IDs
        """

        for employee_ID in all_employees[:]:
            #Retrieve the total hours of the staff
            assigned_hours = self.session.query(AssignedHours).filter(
                AssignedHours.employeeID == employee_ID,
                AssignedHours.weekDate == self.latest_date
            ).first()
            total_hours = assigned_hours.totalHours if assigned_hours else 0
            
            #Going to assign the shift if total hours is less than 20
            if total_hours < 20:
                availability = self.session.query(availability_day).filter(
                    Availability.employeeID == employee_ID,
                    Availability.weekDate == self.latest_date
                ).scalar()

                assigned = False

                #Assigning the shift based on availability and shift requirements
                if availability:
                    for shift_type in shift_types:
                        if shift_type == "D1" and required_staff["D1"] > 0 and availability in ["A", "D"]:
                            actual_staff["D1"], required_staff["D1"] = self.assign_shift(
                                day_name, "D1", actual_staff["D1"], required_staff["D1"], employee_type, employee_ID
                            )
                            assigned = True
                            break
                        elif shift_type == "N1" and required_staff["N1"] > 0 and availability in ["A", "N"]:
                            actual_staff["N1"], required_staff["N1"] = self.assign_shift(
                                day_name, "N1", actual_staff["N1"], required_staff["N1"], employee_type, employee_ID
                            )
                            assigned = True
                            break
                        elif shift_type == "N2" and required_staff["N2"] > 0 and availability in ["A", "N", "NN"]:
                            actual_staff["N2"], required_staff["N2"] = self.assign_shift(
                                day_name, "N2", actual_staff["N2"], required_staff["N2"], employee_type, employee_ID
                            )
                            assigned = True
                            break
            else: 
                continue

            #Removing the processed employee from the list
            if employee_ID in all_employees:
                all_employees.remove(employee_ID)

        return actual_staff, required_staff

def show_schedule_output(sesh, latest_date, total_score, shift_fulfilled, work_satisfied, total_requirements, total_assigned):
    with Session() as sesh:
        #Retrieving all the data from tables 
        shift_data = sesh.query(ShiftAssignments, ShiftRequirements).join(
            ShiftRequirements, ShiftAssignments.shiftID == ShiftRequirements.shiftID
        ).all()

        #Get senior and junior names in order
        all_seniors = [s[0] for s in sesh.query(Senior.employeeID).all()]
        all_juniors = [j[0] for j in sesh.query(Junior.employeeID).all()]

        #Change the employee IDs to names 
        staff_names = {
            staff.employeeID: staff.name for staff in sesh.query(Employee).all()
        }

        #Order the staff name
        ordered_staff = [staff_names[id] for id in all_seniors if id in staff_names] + \
                        [staff_names[id] for id in all_juniors if id in staff_names]

        #Putting the dayname into the array
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        #Prepare the date to match with days
        day_dates = {}
        for i, day in enumerate(day_order):
            actual_date = latest_date + timedelta(days = i)
            day_dates[day] = str(actual_date.day)

        #Changing the timetable code to displayable data
        shift_table = {
            name: {day: "OFF" for day in day_order}
            for name in ordered_staff
        }
        shift_times = {
            "D1": "12-5",
            "N1": "5-10",
            "N2": "6-11"
        }

        #Retrieve the month and year of the date
        month_name = latest_date.strftime("%B %Y")

        #Accessing the assigned shift for each employee 
        for assignment, shift in shift_data:
            employee = sesh.query(Employee).filter_by(employeeID=assignment.employeeID).first()
            if shift.dayOfWeek in day_order:
                time_str = shift_times.get(shift.shiftType, "TIME")
                shift_table[employee.name][shift.dayOfWeek] = time_str

        #output the data 
        html_template = Template("""
        <div style="text-align: center; font-size: 20px; margin-bottom: 10px;">
            <b>{{ month_name }}</b>
        </div>
        <table border="1">
            <tr>
                <th></th>
                {% for day in days %}<th>{{ day }}</th>{% endfor %}
            </tr>
            <tr>
                <td><b>Date</b></td>
                {% for day in days %}<td>{{ day_dates[day] }}</td>{% endfor %}
            </tr>
            {% for name, schedule in shift_table.items() %}
            <tr>
                <td>{{ name }}</td>
                {% for day in days %}<td>{{ schedule[day] }}</td>{% endfor %}
            </tr>
            {% endfor %}
        </table>
                                 
        <div style="margin-top: 30px; font-size: 16px;">
            <strong> Total Score: {{ total_score }}%</strong><br>
            <span> Shift Fulfillment Score (60%): {{ shift_fulfilled }}%</span><br>
            <span> Work Hour Satisfaction Score (40%): {{ work_satisfied }}%</span><br>
            <span> Total Required Slot: {{ total_requirements }}</span><br>
            <span> Total Assigned Shift: {{ total_assigned }}</span>
        </div>
        """)

        html_output = html_template.render(
            shift_table = shift_table, 
            days = day_order, 
            day_dates = day_dates,
            total_score = f"{total_score:.2f}",
            shift_fulfilled = f"{shift_fulfilled:.2f}",
            work_satisfied = f"{work_satisfied:.2f}",
            total_requirements = f"{total_requirements}",
            total_assigned = f"{total_assigned}",
            month_name = month_name
            )
        put_html(html_output)

#Global variables 
rotated_seniors = []
rotated_juniors = []
rotation_index = {'senior': 0, 'junior': 0}

#Assign shifts dynamically
shift_types = ["D1", "N1", "N2"]

async def show_schedule(reschedule = False):
    clear()

    #Initializing
    daily_shortage = 0
    total_shortage = 0
    shift_fulfilled = 0
    shift_score = 0
    satisfied_staff = 0 
    work_satisfied = 0
    work_score = 0
    total_score = 0
    total_requirements = 0
    total_assigned = 0

    global rotated_seniors, rotated_juniors
    seniors_list = rotated_seniors[:]
    juniors_list = rotated_juniors[:]

    with Session() as sesh:

        #Inserting dummy data into the respective tables
        if sesh.query(Employee).count() == 0:
            employeeImport.to_sql('employee', db, if_exists='append', index=False)
        if sesh.query(Availability).count() == 0:
            availabilityImport["weekDate"] = pd.to_datetime(availabilityImport["weekDate"]).dt.date
            availabilityImport.to_sql('availability', db, if_exists='append', index=False)
        if sesh.query(ShiftRequirements).count() == 0:
            shiftRequirementsImport["weekDate"] = pd.to_datetime(shiftRequirementsImport["weekDate"]).dt.date
            shiftRequirementsImport.to_sql('shiftRequirements', db, if_exists='append', index=False)
        
        #Clear existing assignments if the user want to regenerate again
        sesh.query(ShiftAssignments).delete()
        sesh.query(AssignedHours).delete()
        sesh.commit()

        #Find the latest date in shiftRequirements table
        latest_date = sesh.query(func.max(ShiftRequirements.weekDate)).scalar()

        #Retrieve all shifts for the latest date
        all_shifts = sesh.query(ShiftRequirements).filter(ShiftRequirements.weekDate == latest_date).all()

        #Retrieve the data from the day name columns of the availability table
        day_to_column = {
            "Monday": Availability.mon,
            "Tuesday": Availability.tues,
            "Wednesday": Availability.wed,
            "Thursday": Availability.thurs,
            "Friday": Availability.fri,
            "Saturday": Availability.sat,
            "Sunday": Availability.sun,
        }
        
        #Prepare to make the day loop in order
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        distinct_days = [day[0] for day in sesh.query(ShiftRequirements.dayOfWeek)
                        .filter(ShiftRequirements.weekDate == latest_date)
                        .distinct().all()]
        ordered_days = [day for day in day_order if day in distinct_days]

        #Get the total number of staff
        total_staff = sesh.query(Employee).count()

        #Check whether there is columns in ShiftRequirements table
        for day_name in ordered_days:

            senior_process = False

            #Initialize the variables
            d1_required_s_staff = 0
            n1_required_s_staff = 0
            n2_required_s_staff = 0
            d1_required_j_staff = 0
            n1_required_j_staff = 0
            n2_required_j_staff = 0
            d1_actual_s_staff = 0
            n1_actual_s_staff = 0
            n2_actual_s_staff = 0
            d1_actual_j_staff = 0
            n1_actual_j_staff = 0
            n2_actual_j_staff = 0
            total_required_staff = 0
            total_required_s_staff = 0
            total_required_j_staff = 0
            total_actual_staff = 0
            total_actual_s_staff = 0
            total_actual_j_staff = 0

            #Initialize required staff numbers
            required_s_staff = {"D1":0, "N1": 0, "N2": 0}
            required_j_staff = {"D1":0, "N1": 0, "N2": 0}

            #if no more days found, exit loop
            if not all_shifts:
                break
            
            #Fresh copies of all employees for this day
            all_seniors = seniors_list[:]
            all_juniors = juniors_list[:]
            senior_count = len(all_seniors)
            junior_count = len(all_juniors)

            #Use the class ShiftAssigned 
            shift_assigned = ShiftAssigned(sesh, all_seniors, all_juniors, latest_date)

            #Ensure the availability from the same date
            availability_day = day_to_column.get(day_name)
            if not availability_day:
                continue

            #Get shift requirements for the current day
            shifts = [shift for shift in all_shifts if shift.dayOfWeek == day_name]
            if not shifts:
                continue

            #Retrieve the staff for the day's shifts
            for shift in shifts:
                if shift.shiftType in required_s_staff:
                    required_s_staff[shift.shiftType] += shift.requiredSenior
                    required_j_staff[shift.shiftType] += shift.requiredJunior

            d1_required_s_staff = required_s_staff["D1"]
            n1_required_s_staff = required_s_staff["N1"]
            n2_required_s_staff = required_s_staff["N2"]

            required_staff = {
                "D1": d1_required_s_staff, 
                "N1": n1_required_s_staff, 
                "N2": n2_required_s_staff
                }
            actual_staff = {
                "D1": d1_actual_s_staff, 
                "N1": n1_actual_s_staff, 
                "N2": n2_actual_s_staff
                }  

            #Check whether the senior employee are required
            while (d1_required_s_staff > 0 or n1_required_s_staff > 0 or n2_required_s_staff > 0) and senior_count > 0:
                shift_assigned.checking_constraints(
                    employee_type = "senior",
                    required_staff = required_staff,
                    actual_staff = actual_staff,
                    availability_day = availability_day,
                    shift_types = shift_types,
                    all_employees = all_seniors,
                    day_name = day_name
                )
                senior_count = len(all_seniors)
                
                #Update staff after each assigning
                d1_actual_s_staff = actual_staff["D1"]
                n1_actual_s_staff = actual_staff["N1"]
                n2_actual_s_staff = actual_staff["N2"]

                d1_required_s_staff = required_staff["D1"]
                n1_required_s_staff = required_staff["N1"]
                n2_required_s_staff = required_staff["N2"]

                #Make the checkpoint after senior process is done
                senior_process = True

                #Breaking the loop
                if not (d1_required_s_staff == 0 and n1_required_s_staff == 0 and n2_required_s_staff == 0) or senior_count == 0:
                    break

            d1_required_j_staff = required_j_staff["D1"]
            n1_required_j_staff = required_j_staff["N1"]
            n2_required_j_staff = required_j_staff["N2"]

            #Convert remaining required senior staff to junior staff
            d1_required_j_staff += d1_required_s_staff * 2
            n1_required_j_staff += n1_required_s_staff * 2
            n2_required_j_staff += n2_required_s_staff * 2

            required_staff = {
                "D1": d1_required_j_staff, 
                "N1": n1_required_j_staff, 
                "N2": n2_required_j_staff
                }
            actual_staff = {
                "D1": d1_actual_j_staff, 
                "N1": n1_actual_j_staff, 
                "N2": n2_actual_j_staff
                }

            #Check whether the junior employee are required
            while (d1_required_j_staff > 0 or n1_required_j_staff > 0 or n2_required_j_staff > 0) and junior_count > 0:
                shift_assigned.checking_constraints(
                    employee_type = "junior",
                    required_staff = required_staff,
                    actual_staff = actual_staff,
                    availability_day = availability_day,
                    shift_types = shift_types,
                    all_employees = all_juniors,
                    day_name = day_name
                )
                junior_count = len(all_juniors)

                #Update staff after each assigning
                d1_actual_j_staff = actual_staff["D1"]
                n1_actual_j_staff = actual_staff["N1"]
                n2_actual_j_staff = actual_staff["N2"]

                d1_required_j_staff = required_staff["D1"]
                n1_required_j_staff = required_staff["N1"]
                n2_required_j_staff = required_staff["N2"]

                #Breaking the loop
                if not (d1_required_j_staff == 0 and n1_required_j_staff == 0 and n2_required_j_staff == 0) or junior_count == 0:
                    break
            
            #Convert remaining required junior staff to senior staff
            if not senior_process:
                d1_required_s_staff += d1_required_j_staff/2
                n1_required_s_staff += n1_required_j_staff/2
                n2_required_s_staff += n2_required_j_staff/2

                #Assign the values into the variables
                required_staff = {
                    "D1": int(d1_required_s_staff),
                    "N1": int(n1_required_s_staff),
                    "N2": int(n2_required_s_staff)
                }
                actual_staff = {
                    "D1": d1_actual_s_staff,
                    "N1": n1_actual_s_staff,
                    "N2": n2_actual_s_staff
                }
                #Check whether the senior employee are required
                while (d1_required_s_staff > 0 or n1_required_s_staff > 0 or n2_required_s_staff > 0) and senior_count > 0:
                    shift_assigned.checking_constraints(
                        employee_type = "senior",
                        required_staff = required_staff,
                        actual_staff = actual_staff,
                        availability_day = availability_day,
                        shift_types = shift_types,
                        all_employees = all_seniors,
                        day_name = day_name
                    )
                    senior_count = len(all_seniors)

                    #Update staff after each assigning
                    d1_actual_s_staff = actual_staff["D1"]
                    n1_actual_s_staff = actual_staff["N1"]
                    n2_actual_s_staff = actual_staff["N2"]

                    d1_required_s_staff = required_staff["D1"]
                    n1_required_s_staff = required_staff["N1"]
                    n2_required_s_staff = required_staff["N2"]

                    #Make the checkpoint after senior process is done
                    senior_process = True

                    #Breaking the loop
                    if not (d1_required_s_staff == 0 and n1_required_s_staff == 0 and n2_required_s_staff == 0) or senior_count == 0:
                        break
            
            #Get Daily Shortage
            total_required_s_staff = required_s_staff["D1"] + required_s_staff["N1"] + required_s_staff["N2"]
            total_required_j_staff = required_j_staff["D1"] + required_j_staff["N1"] + required_j_staff["N2"]
            total_actual_s_staff = d1_actual_s_staff + n1_actual_s_staff + n2_actual_s_staff
            total_actual_j_staff = d1_actual_j_staff + n1_actual_j_staff + n2_actual_j_staff

            total_required_staff = (total_required_s_staff * 2) + total_required_j_staff
            total_actual_staff = (total_actual_s_staff * 2) + total_actual_j_staff
            if total_required_staff > 0:
                daily_shortage += round(((total_required_staff - total_actual_staff) / total_required_staff) * 100, 2)
            else:
                daily_shortage = 0

            #Remove processed shifts for the day from the list
            all_shifts = [shift for shift in all_shifts if shift.dayOfWeek != day_name]

        #Get Total Shortage Percentage
        total_shortage = round(daily_shortage / 7, 2)

        #Get Shift Fulfilled Percentage
        shift_fulfilled = 100 - total_shortage

        #Get Shift Fulfillment Score 
        shift_score = shift_fulfilled * 0.6

        #Get the number of staff who get more than 10 hours
        satisfied_staff = sesh.query(AssignedHours).filter(
            AssignedHours.totalHours > 10
        ).count()

        #Get Work Satisfied Percentage
        work_satisfied = round((satisfied_staff / total_staff) * 100, 2)

        #Get Work Hour Score
        work_score = work_satisfied * 0.4

        #Get Total Score
        total_score = shift_score + work_score

        #Get Total Required Slot
        total_requirements = sesh.query(
            func.sum(ShiftRequirements.requiredSenior + ShiftRequirements.requiredJunior)
        ).scalar() or 0

        #Get Total Assigned Shifts
        total_assigned = sesh.query(ShiftAssignments).count()

        show_schedule_output(
            sesh, latest_date,
            total_score, shift_fulfilled, work_satisfied,
            total_requirements, total_assigned
        )

async def main():
    global rotated_seniors, rotated_juniors

    # Load once initially
    with Session() as sesh:
        #Retrieving senior and junior data
        if sesh.query(Senior).count() == 0:
            seniorImport.to_sql('senior', db, if_exists='append', index=False)
        if sesh.query(Junior).count() == 0:
            juniorImport.to_sql('junior', db, if_exists='append', index=False)

        #Put the value in the list
        rotated_seniors = [s[0] for s in sesh.query(Senior.employeeID).all()]
        rotated_juniors = [j[0] for j in sesh.query(Junior.employeeID).all()]

    while True:
        await show_schedule()

        #Output the buttons
        choice = await actions('Choose an action:', ['Reschedule Again', 'Exit'])

        if choice == 'Reschedule Again':
            # Rotate global lists
            if rotated_seniors:
                rotated_seniors = rotated_seniors[1:] + rotated_seniors[:1]
            if rotated_juniors:
                rotated_juniors = rotated_juniors[1:] + rotated_juniors[:1]
        else:
            break

#Retrieve the table for output
if __name__ == "__main__":
    start_server(main, port=8080, debug=True, session_cls=CoroutineBasedSession)