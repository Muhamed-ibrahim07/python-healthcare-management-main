import datetime
import streamlit as st
from datetime import datetime, timedelta
import database as db
import patient
import doctor
import pandas as pd
import threading
import time
from plyer import notification



# ... (Existing code for prescription, patient, doctor, etc.)

class Appointment:
    def __init__(self):
        self.id = None
        self.patient_id = None
        self.patient_name = None
        self.doctor_id = None
        self.doctor_name = None
        self.department = None
        self.appointment_date = None
        self.appointment_time = None
        self.status = "Pending"  # Initial status

    def book_appointment(self):
        st.subheader("Book Appointment")

        patient_id = st.text_input("Patient ID")
        if patient_id == '':
            st.empty()
        elif not patient.verify_patient_id(patient_id):
            st.error("Invalid Patient ID")
        else:
            self.patient_id = patient_id
            self.patient_name = patient.get_patient_name(patient_id)
            st.success("Patient Verified")

            doctor_id = st.text_input("Doctor ID")
            if doctor_id == '':
                st.empty()
            elif not doctor.verify_doctor_id(doctor_id):
                st.error("Invalid Doctor ID")
            else:
                self.doctor_id = doctor_id
                self.doctor_name = doctor.get_doctor_name(doctor_id)

                st.success("Doctor Verified")

                appointment_date = st.date_input("Appointment Date", min_value= datetime.now())
                self.appointment_date = appointment_date.strftime("%Y-%m-%d")

                appointment_time = st.time_input("Appointment Time")
                self.appointment_time = appointment_time.strftime("%H:%M:%S")

                if st.button("Book"):
                    self.id = self.generate_appointment_id()  # Generate ID after booking
                    # conn, c = db.connection()
                    # with conn:
                    #     c.execute(
                    #         """
                    #         INSERT INTO appointment_record (id, patient_id, patient_name, doctor_id, doctor_name, department, appointment_date, appointment_time, status)
                    #         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    #         """,
                    #         (self.id, self.patient_id, self.patient_name, self.doctor_id, self.doctor_name,
                    #          self.department, self.appointment_date, self.appointment_time, self.status),
                    #     )
                    # conn.close()
                    # def display_message_at_time(appointment_date, appointment_time, message):
                    #     # Convert the input date and time into a datetime object
                    #     target_time = datetime.strptime(appointment_date + ' ' + appointment_time, '%Y/%m/%d %H:%M')
                    #
                    #     # Run an infinite loop to constantly check the time
                    #     while True:
                    #         # Get the current time
                    #         current_time = datetime.now()
                    #
                    #         # Check if the current time matches the target time
                    #         if current_time >= target_time:
                    #             # Display the native message box notification using plyer
                    #             notification.notify(
                    #                 title="Reminder",
                    #                 message=message,
                    #                 timeout=10  # Duration for which the notification will be visible
                    #             )
                    #             break  # Exit the loop after the message is displayed
                    #
                    #         # Check every 10 seconds
                    #         time.sleep(10)
                    #
                    # # Wrapper function to run the display_message_at_time in a separate thread
                    # def start_message_thread(appointment_date, appointment_time, message):
                    #     # Create a new thread for the display_message_at_time function
                    #     message_thread = threading.Thread(target=display_message_at_time,
                    #                                       args=(appointment_date, appointment_time, message))
                    #     message_thread.start()
                    # st.success("Appointment booked successfully. Appointment ID: {}".format(self.id))

                    # import threading
                    import ctypes
                    # from datetime import datetime, timedelta
                    # import time  # Import the time module

                    def display_message_at_datetime(date, time_str, message, title="Notification"):
                        def wait_and_display():
                            # Combine date and time to create the target datetime string
                            target_datetime_str = f"{date} {time_str}:00"  # Append seconds to match datetime format
                            # Parse the target datetime with the new format
                            target = datetime.strptime(target_datetime_str, "%Y/%m/%d %H:%M:%S")

                            # Adjust the target time by subtracting one hour
                            target = target - timedelta(hours=1)

                            # Get the current time
                            current_time = datetime.now()

                            # Check if the target time has already passed
                            if target < current_time:
                                # Display an error message box if the target time has already passed
                                ctypes.windll.user32.MessageBoxW(0, "Error: The target time has already passed.", title,
                                                                 1)
                                return

                            # Calculate the difference in seconds between now and the target time
                            seconds_to_wait = (target - current_time).total_seconds()

                            # Sleep the thread for the calculated time
                            time.sleep(seconds_to_wait)  # Use the time module's sleep

                            # Display the message box after the sleep duration
                            ctypes.windll.user32.MessageBoxW(0, message, title, 1)

                        # Create a thread to run the function independently
                        thread = threading.Thread(target=wait_and_display, daemon=False)  # Non-daemon thread
                        thread.start()

                    # Schedule a notification
                    display_message_at_datetime(
                        date="2024/12/20",  # Date in yyyy/mm/dd format
                        time_str="06:55",  # Time in hh:mm format
                        message="You Have An Appointment after 1 Hour!"
                    )

                    # Main program ends after showing the message box
                    print("Notification displayed, program ends.")

    def generate_appointment_id(self):
        now = datetime.now()
        return f"APPT-{now.strftime('%Y%m%d%H%M%S')}"

    # Method for updating existing appointments
    def update_appointment(self):
        appointment_id = st.text_input("Enter Appointment ID to update:")

        if appointment_id:
            conn, c = db.connection()
            with conn:
                c.execute("SELECT * FROM appointment_record WHERE id = ?", (appointment_id,))
                appointment_data = c.fetchone()

            if appointment_data:
                # Display current appointment details
                st.write("Current Appointment Details:")
                st.write(
                    pd.DataFrame([appointment_data], columns=[col[0] for col in c.description]))  # Display as DataFrame

                # Update fields (you can add more fields as needed)
                new_status = st.selectbox("New Status", ["Pending", "Confirmed", "Cancelled", "Completed"])

                if st.button("Update Appointment"):
                    with conn:
                        c.execute(
                            "UPDATE appointment_record SET status = ? WHERE id = ?", (new_status, appointment_id)
                        )
                    conn.close()
                    st.success("Appointment updated successfully.")
            else:
                st.error("Appointment not found.")
        else:
            st.warning("Please enter an Appointment ID")

    # Method to view appointments
    def view_appointments(self):

        view_options = ["All Appointments", "By Patient", "By Doctor"]
        selected_view = st.selectbox("View Appointments:", view_options)

        conn, c = db.connection()

        if selected_view == "All Appointments":
            with conn:
                c.execute("SELECT * FROM appointment_record")
                appointments = c.fetchall()

        elif selected_view == "By Patient":
            patient_id = st.text_input("Enter Patient ID:")
            if patient_id:
                with conn:
                    c.execute("SELECT * FROM appointment_record WHERE patient_id = ?", (patient_id,))
                    appointments = c.fetchall()
            else:
                appointments = []

        elif selected_view == "By Doctor":
            doctor_id = st.text_input("Enter Doctor ID:")
            if doctor_id:
                with conn:
                    c.execute("SELECT * FROM appointment_record WHERE doctor_id = ?", (doctor_id,))
                    appointments = c.fetchall()

            else:
                appointments = []

        conn.close()
        if appointments:
            df = pd.DataFrame(appointments, columns=[col[0] for col in c.description])  # Use c.description
            st.write(df)
        else:
            st.warning("No appointments found.")