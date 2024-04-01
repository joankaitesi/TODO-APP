from django.core.mail import send_mail
from django.conf import settings
from todo_app .models import TodoAppModel
from datetime import timedelta,datetime
from django.utils import timezone


def check_task_due_datetime():
    todoTasks = TodoAppModel.objects.all()
    current_datetime = timezone.now()
    # thirty2_min_b4_current_datetime = current_datetime - timedelta(minutes=32)


    for task in todoTasks:

        # if task is not yet due. (due date greater than todays date)
        if task.due_datetime > current_datetime:

            task_remaining_time = task.due_datetime - current_datetime             


            # Task is due in 32 minutes
            if task_remaining_time < timedelta(minutes=32):


                # task email notification has not been sent already
                if task.email_notification_sent == False :

                    # send an email showing task is due                
                    send_email_notification(task_remaining_time ,task) 

                    # mark email as sent, save email field
                    task.email_notification_sent = True
                    task.save()    

                else:
                    pass #email already sent to the user


            else:
                pass # task is not yet 30 min to due datetime

        
        else:
            pass # task is overdue. Action will be considered later



def send_email_notification(timeRemaining, task):
    # convert time to minutes. Put in email
    minutes_remaining = int(timeRemaining.total_seconds() // 60)

    subject = f'Todo App: Your task "{task.title}" is due in {minutes_remaining} minutes'
    message = f'Dear {task.user.username},\n\nThis is a reminder that your task "{task.title}" is due in {minutes_remaining} minutes.\n\nTask Details:\nTitle: {task.title}\nDescription: {task.description}\nDue Date: {task.due_datetime}\n\nBest regards,\nYour Task Management System'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [task.user.email]
    send_mail(subject, message, from_email, recipient_list)