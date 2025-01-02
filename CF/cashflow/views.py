from datetime import timedelta
import json
from khayyam import JalaliDate
from django import forms
from decimal import Decimal
from django.contrib import messages
from .forms import parentSignupForm, ChildSignupForm, ParentLoginForm, ChildLoginForm, costsForm, goalsForm, GoalUpdateForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import check_password
from django.utils.timezone import now
# from django.core.mail import send_mail
# from django.conf import settings
# from .models import EmailConfirmation
# from django.http import JsonResponse
from .models import Child, Cost, Parent, Goals
from django.db.models import Q, Sum
import jdatetime



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
                    request.session['user_type'] = 'Parent'
                    request.session['user_id'] = parent.id

                    child=parent.children.first()
                    if child:
                        return redirect('parent_dashboard', child.id)
                    else:
                        #in case the parent doesn't have any children they will be immediatly taken to the child sign up page
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
    children = parent.children.all()
    if request.method=="POST":
        form=ChildSignupForm(request.POST)
        if form.is_valid():
            child=form.save(commit=False)
            child.parent=parent
            child.save()
            print("CHILD_ID: ", child.id)
            return redirect("parent_dashboard", child_id = child.id)
        
    else:
        form=ChildSignupForm()
    print("PARENT_ID: ", parent.id, parent)
    
    
    return render(request, 'cashflow/child_signup.html', {'form': form, "parent":parent, "children": children})

#..........................................................................................................................

def costs(request, child_id):
    child=get_object_or_404(Child, id=child_id)
    filter_option = request.GET.get('filter', 'all')

    persian_today = jdatetime.date.fromgregorian(date=now().date())

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
    ).order_by('-date')
    else:
        costs = child.costs.all().order_by('-date')
    
    if request.method=="POST":
        print("Form submitted with POST data:", request.POST) 
        delete_cost_id = request.POST.get("delete_cost_id") 
       
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
            'filter_option': filter_option,
            
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
                    request.session['user_type'] = 'Child'
                    request.session['user_id'] = child.id
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

#.........................................................................................................................

def details(request, child_id):
    child=get_object_or_404(Child, id=child_id)
    children=child.parent.children.all()
    user_type = request.session.get('user_type') 
    user_id = request.session.get('user_id') 

    needs = Cost.objects.filter(child=child, type='expense', cate_choices='needs').order_by('-date')
    wants = Cost.objects.filter(child=child, type='expense', cate_choices='wants').order_by('-date')
    other=Cost.objects.filter(child=child, type='expense', cate_choices='else').order_by('-date')

    print("chilldren: ",children)
    
    total_needs = Cost.objects.filter(child=child, type='expense', cate_choices='needs').aggregate(Sum('amount'))['amount__sum'] or 0
    total_wants = Cost.objects.filter(child=child, type='expense', cate_choices='wants').aggregate(Sum('amount'))['amount__sum'] or 0
    total_other = Cost.objects.filter(child=child, type='expense', cate_choices='else').aggregate(Sum('amount'))['amount__sum'] or 0

    # username=child.parent.username
    # print("usermameeeeeeeeeeeeeeeeeeeeeeee:", username)

    # parent=Parent.objects.filter(username=username).first()
    if user_type == 'Parent':
        # user = Parent.objects.get(id=user_id)
        is_parent = True
    else :
        # user = Child.objects.get(id=user_id)
        is_parent = False
        
    print("IS_PARENT: ", is_parent, user_type)

    context={
        'child':child,
        'needs': needs,
        'wants': wants,
        'other':other,
        'children':children,
        'total_needs':total_needs,
        'total_wants':total_wants,
        'total_other':total_other,
        'is_parent': is_parent,
    }

    return render(request, "cashflow/details.html", context)


#.........................................................................................................................


def goals(request, child_id):
    child=get_object_or_404(Child, id=child_id)
    goals=child.goals.all()
    

    goal_to_edit=None
    edit_goal_id=request.POST.get("edit_goal_id")

    if edit_goal_id:
        goal_to_edit=goals.filter(id=edit_goal_id).first()
        if not goal_to_edit:
            messages.error(request, "Goal not found")
            return redirect('goals', child_id = child_id)
        
        
    goal_form = goalsForm()
    update_form = GoalUpdateForm(instance=goal_to_edit)
        

        
    if request.method == "POST":
        print("Form submitted with POST data:", request.POST) 

        if 'add_goal' in request.POST:
            goal_form = goalsForm(request.POST)
            if goal_form.is_valid():
                goal = goal_form.save(commit=False)
                goal.child=child
                print("Goals for child:", child.goals.all())
                goal.save()
                messages.success(request, "Goal added successfully.")
                return redirect('goals', child_id=child_id)
            else:
                messages.error(request, "Failed to add goal. Please fix the errors below.")

        elif 'update_savings' in request.POST and goal_to_edit:
            update_form=GoalUpdateForm(request.POST, instance=goal_to_edit)
            if update_form.is_valid():
                update_form.save()
                messages.success(request, "Savings updated successfully.")
                return redirect('goals', child_id=child_id)
            else:
                messages.error(request, "Failed to update savings. Please fix the errors below.")
  
        delete_goal_id = request.POST.get("delete_goal_id") 
       
        if delete_goal_id:
            goal = goals.filter(id=delete_goal_id).first()
            if  goal:
                goal.delete()
                messages.success(request, "Goal deleted successfully.")
            else:
                messages.error(request, "Goal not found.")
            return redirect('goals', child_id=child_id)
        
    # else:      
    #     goal_form = goalsForm()
    #     update_form = GoalUpdateForm(instance = goal_to_edit)
    chart_data = [    
        {
            'name': goal.goal,
            'progress': round((goal.savings / goal.goal_amount) * 100) if goal.goal_amount > 0 else 0,
        }
        for goal in goals
    ]
    for goal in goals:
        goal.progress_percentage = round((goal.savings / goal.goal_amount) * 100) if goal.goal_amount > 0 else 0
    print("Chart Data:", chart_data)


    context = {
        'goal_form': goal_form, 
        'update_form': update_form, 
        'child': child,
        'goal_to_edit': goal_to_edit,
        'goals': goals,
        'chart_data': json.dumps(chart_data),
    }

    return render(request, 'cashflow/goals.html', context)


#.........................................................................................................................

def child_dashboard(request, child_id):
   
   child=get_object_or_404(Child, id=child_id)
   print(request.session.get('child_id'))

   persian_today = jdatetime.date.today()
    
   

   start_day = persian_today
   start_week = persian_today - jdatetime.timedelta(days=persian_today.weekday())
   start_month = persian_today.replace(day=1)

   start_day_str = start_day.strftime('%Y-%m-%d')
   start_week_str = start_week.strftime('%Y-%m-%d')
   start_month_str = start_month.strftime('%Y-%m-%d')

   daily_costs = child.costs.filter(date=start_day_str, type='expense')
   weekly_costs = child.costs.filter(date__gte=start_week_str, type='expense')
   monthly_costs = child.costs.filter(date__gte=start_month_str, type='expense')

   daily_total = daily_costs.aggregate(total=Sum('amount'))['total'] or Decimal(0)
   weekly_total = weekly_costs.aggregate(total=Sum('amount'))['total'] or Decimal(0)
   monthly_total = monthly_costs.aggregate(total=Sum('amount'))['total'] or Decimal(0)

   CATEGORY_TRANSLATIONS = {key: value for key, value in Cost.EXPENSE_CATEGORIES}

   top_categories = (
       Cost.objects.filter(child = child, type='expense', date__gte = start_month_str)
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

   top_goals = child.goals.all()[:3]
   for goal in top_goals:
       goal.progress_percentage = ((goal.savings/goal.goal_amount) * 100) 
       if goal.progress_percentage == 100:
        goal.border_radius = "10px"
       else:
        goal.border_radius = "0"


   print("Categories:", categories)
   print("Amounts:", amount)
   print("Income:", income)


   context = {
       'child' : child,
       'categories' : categories,
       'amount' : amount,
       'income': income,
       'recent_costs': recent_costs,
       'daily_total': daily_total,
       'weekly_total': weekly_total,
       'monthly_total': monthly_total,
       'persian_today': persian_today.strftime('%Y-%m-%d'),
       'top_goals': top_goals,
   }


   return render(request, 'cashflow/child_dashboard.html', context)


#.........................................................................................................................

def parent_dashboard(request, child_id):
    child=get_object_or_404(Child, id=child_id)
    parent=child.parent
    print(request.session.get('child_id'))
    children=parent.children.all()



    persian_today = jdatetime.date.today()

    # filter_options = request.GET.get('filter', 'all')

    start_day = persian_today
    start_week = persian_today - jdatetime.timedelta(days=persian_today.weekday())
    start_month = persian_today.replace(day=1)

    start_day_str = start_day.strftime('%Y-%m-%d')
    start_week_str = start_week.strftime('%Y-%m-%d')
    start_month_str = start_month.strftime('%Y-%m-%d')

    daily_costs = child.costs.filter(date=start_day_str, type='expense')
    weekly_costs = child.costs.filter(date__gte=start_week_str, type='expense')
    monthly_costs = child.costs.filter(date__gte=start_month_str, type='expense')

    daily_total = daily_costs.aggregate(total=Sum('amount'))['total'] or Decimal(0)
    weekly_total = weekly_costs.aggregate(total=Sum('amount'))['total'] or Decimal(0)
    monthly_total = monthly_costs.aggregate(total=Sum('amount'))['total'] or Decimal(0)


    now=jdatetime.datetime.now()

    current_month_start=now.replace(day=1)
    prev_month_start=(current_month_start - timedelta(days=1)).replace(day=1)
    two_months_ago_start = (prev_month_start - timedelta(days=1)).replace(day=1)
    
    next_month_start = (current_month_start + jdatetime.timedelta(days=31)).replace(day=1)
    current_month_end = next_month_start - jdatetime.timedelta(days=1)
    current_month_end_str = current_month_end.strftime('%Y-%m-%d')

    CATEGORY_TRANSLATIONS = {key: value for key, value in Cost.EXPENSE_CATEGORIES}

    top_categories = (
       Cost.objects.filter(
           child = child, 
           type='expense',
           date__gte=start_month_str, 
           date__lte=current_month_end_str,   
           )
       .values('cate_choices')
       .annotate(total_spending=Sum('amount'))
       .order_by('-total_spending')[:6]
    )
    total_income = (
     Cost.objects.filter(child=child, type='income')
    .aggregate(total_income=Sum('amount'))
    )

        # The calculation needed for the bar diagram:

   

    #get their names in persian:

    persian_months = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور", "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
    months = [
        persian_months[two_months_ago_start.month - 1],
        persian_months[prev_month_start.month - 1],
        persian_months[current_month_start.month - 1]
    ]

    

    
    needs = Cost.objects.filter(
        child=child,
        date__gte=start_month_str, 
        date__lte=current_month_end_str,
        type='expense', 
        cate_choices='needs'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    wants = Cost.objects.filter(
        child=child, 
        date__gte=start_month_str,
        date__lte=current_month_end_str, 
        type='expense', 
        cate_choices='wants'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    other = Cost.objects.filter(
        child=child, 
        date__gte=start_month_str, 
        date__lte=current_month_end_str,
        type='expense', 
        cate_choices='else'
        ).aggregate(Sum('amount'))['amount__sum'] or 0

    categories = [CATEGORY_TRANSLATIONS[item['cate_choices']] for item in top_categories] 

    amount = [float(item['total_spending']) for item in top_categories] 

    income = total_income['total_income'] if total_income['total_income'] else 0
    recent_costs=Cost.objects.filter(child_id=child_id).order_by('-date')[:6]

    CA_pairs = zip(categories, amount)
    periods = ['روز', 'هفته', 'ماه', 'همه']

    savings=Goals.objects.filter(child=child).aggregate(Sum('savings'))['savings__sum'] 
    if savings:
        savings = float(f"{savings:.1f}")






    income_expense_data = []

    for start_date in [two_months_ago_start, prev_month_start, current_month_start]:

        end_date = ((start_date + timedelta(days=31)).replace(day=1))- timedelta(days=1)

        start_date_str = start_date.strftime('%Y-%m-%d') 
        end_date_str = end_date.strftime('%Y-%m-%d') 
        print("Start date:", start_date_str, "End date:", end_date_str)

        total_income = (
            Cost.objects.filter(
                child=child,
                date__gte=start_date_str,
                date__lte = end_date_str,
                type='income',
            ).aggregate(Sum('amount'))['amount__sum'] or 0
        )

        total_expense = (
            Cost.objects.filter(
                child=child,
                date__gte = start_date_str,
                date__lte = end_date_str,
                type = 'expense'
            ).aggregate(Sum('amount'))['amount__sum'] or 0
        )

        income_expense_data.append(
           { 
               'income': float(total_income),  
               'expense': float(total_expense) 
            }
        )


        print("mmmmmmmmm: ", months)
        print("incomExpeneeee: ", income_expense_data)




    context = {
        'child': child,
        'parent': parent,
        'categories': categories,
        'amount': amount,
        'income': income,
        'recent_costs': recent_costs,
        'CA_pairs': CA_pairs,
        'periods': periods,
        'daily_total': daily_total,
        'weekly_total': weekly_total,
        'monthly_total': monthly_total,
        'persian_today': persian_today.strftime('%Y-%m-%d'),
        'children': children,
        'savings': savings,
        'needs': needs,
        'wants': wants,
        'other':other,
        'months': json.dumps(months),
        'income_expense_data': json.dumps(income_expense_data), 
    }
    return render(request, 'cashflow/parent_dashboard.html', context)


def education(request, child_id):
    child=get_object_or_404(Child, id=child_id)
    persian_today=jdatetime.date.today()

    current_month_start=persian_today.replace(day=1)
    next_month_start = (current_month_start + timedelta( days = 31 )).replace(day=1)
    current_month_end = next_month_start - timedelta( days = 1 )

    needs = Cost.objects.filter(
        child = child,
        type = 'expense',
        cate_choices = 'needs',
        date__gte = current_month_start,
        date__lte = current_month_end,
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    wants = Cost.objects.filter(
        child = child,
        type = 'expense',
        cate_choices = 'wants',
        date__gte = current_month_start,
        date__lte = current_month_end,
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    other = Cost.objects.filter(
        child = child,
        type = 'expense',
        cate_choices = 'else',
        date__gte = current_month_start,
        date__lte = current_month_end,
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    income = Cost.objects.filter(
        child=child,
        type = 'income',
        date__gte = current_month_start,
        date__lte = current_month_end,
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    supposed_needs_amount = (Decimal(income) * Decimal(50)) / Decimal(100)
    supposed_wants_amount = (Decimal(income) * Decimal(30)) / Decimal(100)
    supposed_other_amount = (Decimal(income) * Decimal(20)) / Decimal(100)
    if(income>0):
        actual_needs_perce = round((needs / income) * 100) if income > 0 else 0
        actual_wants_perce = round((wants / income) * 100) if income > 0 else 0
        actual_other_perce = round((other / income) * 100) if income > 0 else 0
    else:
        total_sum = needs + wants + other
        if total_sum > 0: 
            actual_needs_perce = round((needs / total_sum) * 100, 0)
            actual_wants_perce = round((wants / total_sum) * 100, 0)
            actual_other_perce = round((other / total_sum) * 100, 0)
        else:
            actual_needs_perce = 0
            actual_wants_perce = 0
            actual_other_perce = 0
    print("***************************************************")
    print("income:", income)
    print("needs", needs)
    print("wants", wants)
    print("other", other)
    print("actual_needs_perce", actual_needs_perce)
    print("actual_wants_perce", actual_wants_perce)
    print("actual_other_perce", actual_other_perce)

    needs_difference = abs(needs - supposed_needs_amount)
    wants_difference = abs(wants - supposed_wants_amount)
    other_difference = abs(other - supposed_other_amount)

    

    

    context = {
        'child': child,
        'needs': needs,
        'wants': wants,
        'other': other,
        'income': income,
        'supposed_needs_amount': supposed_needs_amount,
        'supposed_wants_amount': supposed_wants_amount,
        'supposed_other_amount': supposed_other_amount,
        'actual_needs_perce': actual_needs_perce,
        'actual_wants_perce': actual_wants_perce,
        'actual_other_perce': actual_other_perce,
        'needs_difference': needs_difference,
        'wants_difference': wants_difference,
        'other_difference': other_difference,
    }

    return render(request, 'cashflow/education.html', context)
    






    