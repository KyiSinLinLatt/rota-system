# Employee-Centric Rota Scheduling System

🧠 Overview

This project presents an employee-centric rota scheduling system designed for small businesses and charities that rely on part-time and flexible staff. The system automates shift allocation based on employee availability, business requirements, and predefined constraints.

It aims to reduce the complexity and time required for manual scheduling while improving decision-making through performance evaluation of generated schedules.  ￼

⸻

⚙️ Features
	•	Generates weekly shift schedules based on availability and requirements
	•	Applies constraint-based scheduling logic (no optimisation algorithms)
	•	Supports:
	•	Maximum working hours (e.g. 20 hours/week)
	•	Employee availability
	•	Seniority-based assignment
	•	Calculates a performance score based on:
	•	Shift fulfilment
	•	Employee satisfaction
	•	Allows regeneration of alternative schedules

⸻

🛠️ Technologies Used
	•	Python – backend logic and scheduling system
	•	SQL (SQLite) – data storage and management
	•	HTML / CSS – schedule visualisation
	•	PyWebIO – web-based interface

⸻

🧩 Approach

The system uses a constraint-based approach combined with demand modelling, focusing on generating feasible schedules rather than optimal ones.  ￼

Employees are assigned to shifts based on:
	•	availability
	•	required staffing levels
	•	hierarchical skill structure (senior vs junior staff)

⸻

🎯 Key Contributions
	•	Designed and implemented a full scheduling system from scratch
	•	Developed constraint-checking and shift assignment logic
	•	Integrated database handling with scheduling workflow
	•	Created a scoring mechanism to evaluate schedule quality

⸻

⚠️ Limitations
	•	Limited input validation (invalid data may be skipped)
	•	Constraints are hardcoded (not fully configurable)
	•	Performance may decrease with larger datasets

⸻

🌱 Future Improvements
	•	User input forms for dynamic data entry
	•	Schedule comparison functionality
	•	Improved validation and error handling
	•	Configurable constraints for broader use cases
⸻

## 📄 Project Report  
This report provides a detailed explanation of the system design, implementation, and evaluation.  
[View Report](https://github.com/KyiSinLinLatt/rota-system/releases/tag/v1.0)
