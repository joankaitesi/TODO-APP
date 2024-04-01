
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import TodoAppForm
from .models import TodoAppModel
from django.utils import timezone
import datetime
import json
from django.core.mail import send_mail
from django.conf import settings

def welcome(request):
    """
    Render the welcome page
    
    Parameters:
        - request: The HTTP request object
        
    Returns:
        - A rendered HTML template (base/welcome.html) with the context
    """
    page = 'welcome'
    context = {'page': page}
    return render(request, 'base/welcome.html', context)


def aboutUs(request):
    """
    Render the about us page
    
    Parameters:
        - request: The HTTP request object
        
    Returns:
        - A rendered HTML template (base/aboutUs.html) with the context
    """
    page = 'aboutUs'
    context = {'page': page}
    return render(request, 'base/aboutUs.html', context)


def contactUs(request):
    """
    Render the contact us page
    
    Parameters:
        - request: The HTTP request object
        
    Returns:
        - A rendered HTML template (base/contactUs.html) with the context
    """
    page = 'contactUs'
    context = {'page': page}
    return render(request, 'base/contactUs.html', context)


@login_required(login_url='login')
def viewTasks(request):
    """
    Render the view tasks page
    
    Parameters:
        - request: The HTTP request object
        
    Returns:
        - A rendered HTML template (todo_app/viewTasks.html) with the context
    """
    page = 'home'
    todoTask = TodoAppModel.objects.filter(user=request.user)
    context = {'page': page, 'todoTask': todoTask}
    return render(request, 'todo_app/viewTasks.html', context)


@login_required(login_url='login')
def createTask(request):
    """
    Create a new task
    
    Parameters:
        - request: The HTTP request object
        
    Returns:
        - If the request method is 'GET', a rendered HTML template (todo_app/create_or_update_task.html)
          with the context.
        - If the request method is 'POST' and the task is successfully created, a redirect to the 'viewTasks' URL.
        - If the form is invalid or the task due date is in the past, a rendered HTML template (todo_app/create_or_update_task.html)
          with the context and an error message.
    """
    page = 'createTask'
    todoTaskCreate = TodoAppForm()

    if request.method == 'POST':
        date_string = request.POST['due_date']
        time_string = request.POST['due_time']

        # Combine date and time from user input
        due_datetime = datetime.datetime.strptime(date_string + ' ' + time_string, '%Y-%m-%d %H:%M')

        # Task should be for a future date only
        if due_datetime > datetime.datetime.now():
            todoTaskCreate = TodoAppForm(request.POST or None)

            if todoTaskCreate.is_valid():
                todo_task = todoTaskCreate.save(commit=False)

                # Add user field
                todo_task.user = request.user

                # Add datetime to the task 
                todo_task.due_datetime = due_datetime

                todo_task.save()

                return redirect('viewTasks')
            else:
                messages.error(request, 'ERROR: The task can\'t be created because the form is invalid')
        else:
            messages.error(request, 'ERROR: Tasks can only be created for future dates')

    context = {'page': page, 'todoTaskCreate': todoTaskCreate}
    return render(request, 'todo_app/create_or_update_task.html', context)


@login_required(login_url='login')
def updateTask(request, pk):
    """
    Update an existing task
    
    Parameters:
        - request: The HTTP request object
        - pk: The primary key of the task to be updated
        
    Returns:
        - If the request method is 'GET', a rendered HTML template (todo_app/create_or_update_task.html)
          with the context.
        - If the request method is 'POST' and the task is successfully updated, a redirect to the 'viewTasks' URL.
        - If the form is invalid or the task due date is in the past, a rendered HTML template (todo_app/create_or_update_task.html)
          with the context and an error message.
    """
    page = 'updateTask'
    todoTask = TodoAppModel.objects.get(id=int(pk))
    todoTaskCreate = TodoAppForm(instance=todoTask)

    if request.method == 'POST':
        date_string = request.POST['due_date']
        time_string = request.POST['due_time']

        # Combine date and time from user input
        due_datetime = datetime.datetime.strptime(date_string + ' ' + time_string, '%Y-%m-%d %H:%M')

        # Task should be for a future date only
        if due_datetime > datetime.datetime.now():
            todoTaskCreate = TodoAppForm(request.POST, instance=todoTask)

            if todoTaskCreate.is_valid():
                todo_task = todoTaskCreate.save(commit=False)

                # Add user field
                todo_task.user = request.user

                # Add datetime to the task 
                todo_task.due_datetime = due_datetime

                # Allow email to be resent again
                todo_task.email_notification_sent = False

                todo_task.save()

                return redirect('viewTasks')
            else:
                messages.error(request, 'ERROR: The task can\'t be created because the form is invalid')
        else:
            messages.error(request, 'ERROR: Tasks can only be created for future dates')

    context = {'page': page, 'todoTaskCreate': todoTaskCreate}
    return render(request, 'todo_app/create_or_update_task.html', context)


@login_required(login_url='login')
def deleteTask(request, pk):
    """
    Delete a task
    
    Parameters:
        - request: The HTTP request object
        - pk: The primary key of the task to be deleted
        
    Returns:
        - If the request method is 'GET', a rendered HTML template (todo_app/deleteTask.html)
          with the context.
        - If the request method is 'POST' and the task is successfully deleted, a redirect to the 'viewTasks' URL.
    """
    page = 'deleteTask'
    todoTask = TodoAppModel.objects.get(id=int(pk))
    if request.method == 'POST':
        todoTask.delete()
        return redirect('viewTasks')

    context = {'page': page, 'todoTask': todoTask}
    return render(request, 'todo_app/deleteTask.html', context)


@login_required(login_url='login')
def calendarView(request):
    """
    Render the calendar view page
    
    Parameters:
        - request: The HTTP request object
        
    Returns:
        - A rendered HTML template (todo_app/calendarView.html) with the context
    """
    page = 'calendar'
    todo_app_tasks = TodoAppModel.objects.filter(user=request.user)

    # Convert tasks to JSON format for FullCalendar
    calendarEvents = []
    
    for task in todo_app_tasks:
        event = {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'start': task.due_datetime.isoformat(),
            'end': task.due_datetime.isoformat(),
        }
        calendarEvents.append(event)

    context = {'page': page, 'calendarEvents_json': json.dumps(calendarEvents)}
    return render(request, 'todo_app/calendarView.html', context)

