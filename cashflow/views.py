from django import forms
from django.contrib import messages
from .forms import parentSignupForm, ChildSignupForm, ParentLoginForm, ChildLoginForm, costsForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import check_password
# from django.utils.timezone import now, timedelta
# from django.core.mail import send_mail
# from django.conf import settings
# from .models import EmailConfirmation
# from django.http import JsonResponse
from .models import Child, Cost, Parent
from django.db.models import Q, Sum
import jdatetime
import random


def landing(request):
    return render(request, 'cashflow/landing.html')

#..........................................................................................................................



def parent_signup(request):
    if request.method == "POST":
        form = parentSignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('landing')
    else:
        form = parentSignupForm()

    return render(request, "cashflow/parent_signup.html", {'form': form})


# def parent_signup(request):
#     step=1
#     form = None
#     if request.method=="POST":

#         if 'email' in request.POST:

#             email=request.POST['email']
#             confirmation, created=EmailConfirmation.objects.get_or_create(email=email)
#             confirmation.generate_code()

#             request.session['confirmation_code'] = confirmation.confirmation_code
#             request.session['verified_email'] = email
            
#             send_mail(
#             'کد تایید ثبت نام',
#             f'کد تایید شما: {confirmation.confirmation_code}',
#             'settings.EMAIL_HOST_USER',
#             [email],
#             fail_silently=False,
#             )
            
#             step = 2
#             return render(
#                 request, 
#                 'cashflow/parent_signup.html', 
#                 {'step': step, 'email': email}
#                 )
        
#         elif 'confirmation_code' in request.POST:
#             email=request.POST['email'] or request.session.get('verified_email')
#             entered_code=request.POST.get('confirmation_code')
#             try:
#                 confirmation = EmailConfirmation.objects.get(email=email)
#                 if confirmation.confirmation_code == entered_code:

#                     confirmation.delete()
#                     step=3
#                 else:
#                     return render(
#                         request,
#                         'cashflow/parent_signup.html',
#                         {'step': 2, 'email': email, 'error': 'کد تایید نامعتبر است.'}
#                     )
#             except EmailConfirmation.DoesNotExist:
#                 return render(
#                     request,
#                     'cashflow/parent_signup.html',
#                     {'step': 2, 'email': email, 'error': 'کد تاییدی برای این ایمیل پیدا نشد.'}
#                 )
        

#         elif 'username' in request.POST:
#             form=parentSignupForm(request.POST)
#             if form.is_valid():
#                 form.save()

#                 request.session.pop('confirmation_code', None)
#                 request.session.pop('verified_email', None)

#                 return redirect('landing')
#             else:
#                 step=3

#     if step == 3 and form is None:
#         form = parentSignupForm()

        
#     return render(request, "cashflow/parent_signup.html", {'form': form, 'step': step})

#...........................................................................................................................

def parent_login(request):
    if request.method == 'POST':
        form=ParentLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
        
            try:
                parent=Parent.objects.get(username=username)
                if check_password(password, parent.password):
                    return redirect('child_signup', parent.id)
                else:
                    return render(request, 'cashflow/parent_login.html', {
                        'form':form,
                        'error': "رمز عبور اشتباه است. لطفاً دوباره تلاش کنید."
                    })
        
            except Parent.DoesNotExist:
                return render(request, 'cashflow/parent_login.html', {
                    'form':form,
                    'error': "هیچ کاربری با این نام کاربری یا رمز عبور وجود ندارد. لطفاً ثبت نام کنید."
                })
        else:
            return render(request, 'cashflow/parent_login.html', {'form':form })
    else:
        form=ParentLoginForm()

    return render(request, 'cashflow/parent_login.html', {'form':form})

#...........................................................................................................................

def child_signup(request, parent_id):
    parent=get_object_or_404(Parent, id=parent_id)
    if request.method=="POST":
        form=ChildSignupForm(request.POST)
        if form.is_valid():
            child=form.save(commit=False)
            child.parent=parent
            child.save()
            return redirect("parent_dashboard", child.id)
        
    else:
        form=ChildSignupForm()
    
    return render(request, 'cashflow/child_signup.html', {'form': form, "parent":parent})

#..........................................................................................................................

def costs(request, child_id):
    child=get_object_or_404(Child, id=child_id)
    filter_option = request.GET.get('filter', 'all')

    persian_today = jdatetime.date.today()

    if filter_option == 'day':
        start_date=persian_today
        end_date=persian_today
    elif filter_option == 'month':
        start_date=persian_today.replace(day=1)
        end_date=persian_today
    elif filter_option =='all':
        start_date=None
        end_date=None

    else: 
        start_date=persian_today - jdatetime.timedelta(days=persian_today.weekday())
        end_date=persian_today

    if start_date and end_date:
        costs=child.costs.filter(
        Q(date__gte=start_date.strftime('%Y-%m-%d')) &
        Q(date__lte=end_date.strftime('%Y-%m-%d'))
    )
    else:
        costs=child.costs.all()

    if request.method=="POST":
        print("Form submitted with POST data:", request.POST) 
        delete_cost_id = request.POST.get("delete_cost_id") 
        # print('iddddddddddddddddd',delete_cost_id) 
        if delete_cost_id:
            cost = child.costs.filter(id=delete_cost_id).first()
            if cost:
                cost.delete()
                messages.success(request, "Cost deleted successfully.")
            else:
                messages.error(request, "Cost not found.")
            return redirect('costs', child_id=child_id)
        

        form=costsForm(request.POST)

        type_value = request.POST.get('type', 'expense')
        if type_value == 'income':
            form.fields['cate_choices'].choices = Cost.INCOME_CATEGORIES
        elif type_value == 'expense':
            form.fields['cate_choices'].choices = Cost.EXPENSE_CATEGORIES

        if form.is_valid():
            print("Form is valid")
            cost = form.save(commit=False)
            persian_date = form.cleaned_data['date']  
            cost.date = persian_date
            cost.child = child
            cost.save()
            messages.success(request, "Cost saved successfully.")
            return redirect('costs', child_id=child_id)
        else:
            print("Form errors:", form.errors)

    else:
        initial_type = request.GET.get('type', 'expense')
        form = costsForm(initial={'type': initial_type})
 
        if initial_type == 'income':
            form.fields['cate_choices'].choices = Cost.INCOME_CATEGORIES
        else:
            form.fields['cate_choices'].choices = Cost.EXPENSE_CATEGORIES

    for cost in costs:
        cost.persian_date = cost.date 
    return render(
        request,
        'cashflow/costs.html',
        {
            'form':form,
            'costs': costs,
            'child': child, 
            'persian_today': persian_today.strftime('%Y-%m-%d'),
            'filter_option': filter_option
        },
    )
#.........................................................................................................................

def child_login(request):
    if request.method=="POST":
        form=ChildLoginForm(request.POST)
        if form.is_valid():
            username=form.cleaned_data["username"]
            password=form.cleaned_data["password"]
        
            try:
                child=Child.objects.get(username=username)

                if check_password(password, child.password):
                    return redirect('child_dashboard', child.id)
                    # return redirect('costs', child.id)
                else:
                    return render(request, 'cashflow/child_login.html', {
                        'form':form,
                        'error': "رمز عبور اشتباه است. لطفاً دوباره تلاش کنید."
                    })
            except Child.DoesNotExist:
                return render(request, 'cashflow/child_login.html', {
                    'form':form,
                    'error': "هیچ کاربری با این نام کاربری یا رمز عبور وجود ندارد. لطفاً ثبت نام کنید."
                })
        else:
            return render(request, 'cashflow/child_login.html', {'form':form})
    else:
        form=ChildLoginForm()
    return render(request, 'cashflow/child_login.html', {
        'form':form
    })

#.......................................................................................................................

def child_dashboard(request, child_id):
   
   child=get_object_or_404(Child, id=child_id)
   print(request.session.get('child_id'))

   CATEGORY_TRANSLATIONS = {key: value for key, value in Cost.EXPENSE_CATEGORIES}

   top_categories = (
       Cost.objects.filter(child = child, type='expense')
       .values('cate_choices')
       .annotate(total_spending=Sum('amount'))
       .order_by('-total_spending')[:6]
   )
   total_income = (
    Cost.objects.filter(child=child, type='income')
    .aggregate(total_income=Sum('amount'))
)

   categories = [CATEGORY_TRANSLATIONS[item['cate_choices']] for item in top_categories]

   amount = [float(item['total_spending']) for item in top_categories]

   income = total_income['total_income'] if total_income['total_income'] else 0
   recent_costs=Cost.objects.filter(child_id=child_id).order_by('-date')[:10]

   context = {
       'child' : child,
       'categories' : categories,
       'amount' : amount,
       'income': income,
       'recent_costs': recent_costs,
   }


   return render(request, 'cashflow/child_dashboard.html', context)




def parent_dashboard(request, child_id):
    child=get_object_or_404(Child, id=child_id)
    parent=child.parent

    context = {
        'child': child,
        'parent': parent,
    }

    return render(request, 'parent_dashboard.html', context)






    