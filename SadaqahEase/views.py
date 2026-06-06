from django.shortcuts import render, redirect, get_object_or_404
from django.utils.html import escape
from django.contrib import messages
from datetime import datetime
import datetime
from .models import Admin,Report, Treasurer, Donor,Campaign,Donation,TabungDonation,Financial,AllocateFund
from django.views.decorators.http import require_POST
from django.db.models import Sum
from django.db import models
from datetime import date
from decimal import Decimal
from django.db.models.functions import ExtractYear
import calendar


# ------------------- HOME PAGE -------------------
def SadaqahEase(request):
    
    campaigns = Campaign.objects.filter(
        status='Approved',
        end_date__gte=date.today()
    ).exclude(current_amount__gte=models.F('goal_amount')).order_by('-start_date')[:4]

    for campaign in campaigns:
        campaign.image_url = campaign.campaignimage.url if campaign.campaignimage else '/static/default.jpg'
        campaign.donate_url = f"/donate/{escape(campaign.campaignid)}"

   
    general_donations = Donation.objects.filter(donation_type='General')
    campaign_donations = Donation.objects.filter(donation_type='Campaign')

    general_total = general_donations.aggregate(Sum('amount'))['amount__sum'] or 0
    campaign_total = campaign_donations.aggregate(Sum('amount'))['amount__sum'] or 0
    total_donations = general_total + campaign_total

    
    total_donors = Donor.objects.count()

   
    total_campaigns = Campaign.objects.filter(status='Approved').count()

    return render(request, 'homepage.html', {
        'campaigns': campaigns,
        'total_donations': total_donations,
        'total_donors': total_donors,
        'total_campaigns': total_campaigns,
    })
# ------------------- LOGIN SELECTION PAGE -------------------
def login_page(request):
    return render(request, 'loginpage.html')

# ------------------- ADMIN & TREASURER LOGIN -------------------
def login_view(request):
    if request.method == 'POST':
        admin_id = request.POST.get('admin_id')
        password = request.POST.get('password')
        role = request.POST.get('role')

        if role == 'admin':
            try:
                admin = Admin.objects.get(adminid=admin_id, password=password)
                request.session['admin_id'] = admin.adminid
                return redirect('admin_mainpage')
            except Admin.DoesNotExist:
                messages.error(request, 'Invalid Admin credentials.')
        elif role == 'treasurer':
            try:
                treasurer = Treasurer.objects.get(treasurerid=admin_id, password=password)
                request.session['treasurer_id'] = treasurer.treasurerid
                return redirect('treasurer_mainpage')
            except Treasurer.DoesNotExist:
                messages.error(request, 'Invalid Treasurer credentials.')
        else:
            messages.error(request, 'Please select a valid role.')

    return render(request, 'loginadmin.html')

# ------------------- TREASURER MAIN PAGE -------------------
def treasurer_mainpage(request):
    treasurer_id = request.session.get('treasurer_id')
    if not treasurer_id:
        return redirect('login_admin')

    try:
        treasurer = Treasurer.objects.get(treasurerid=treasurer_id)
    except Treasurer.DoesNotExist:
        messages.error(request, "Treasurer not found.")
        return redirect('login_admin')

    return render(request, 'treasurerpage.html', {'treasurer': treasurer})

# ------------------- DONOR LOGIN -------------------
def login_donor(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            donor = Donor.objects.get(username=username, password=password)
            request.session['donor_id'] = donor.donorid
            return redirect('donor_mainpage')
        except Donor.DoesNotExist:
            # ✅ Show red error message using 'error' tag
            messages.error(request, 'Invalid username or password.')
            return render(request, 'logindonor.html', {'is_donor_login': True})

    return render(request, 'logindonor.html', {'is_donor_login': True})

def forgot_password_donor(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        new_password = request.POST.get('new_password')

        try:
            donor = Donor.objects.get(email=email, username=username)
            donor.password = new_password
            donor.save()
            messages.success(request, "Password reset successfully. Please log in.")
            return redirect('login_donor')
        except Donor.DoesNotExist:
            messages.error(request, "No matching donor found with provided email and username.")

    return render(request, 'forgotpassword.html')
# ------------------- DONOR MAIN PAGE -------------------

def donor_mainpage(request):
    donor_id = request.session.get('donor_id')
    if not donor_id:
        return redirect('login_donor')

    try:
        donor = Donor.objects.get(donorid=donor_id)
    except Donor.DoesNotExist:
        messages.error(request, "Donor not found.")
        return redirect('login_donor')

    #Only show approved & ongoing campaigns (not completed)
    campaigns = Campaign.objects.filter(
        status='Approved',
        end_date__gte=date.today()
    ).exclude(current_amount__gte=models.F('goal_amount')).order_by('-start_date')[:4]

    for campaign in campaigns:
        campaign.image_url = campaign.campaignimage.url if campaign.campaignimage else ''
        campaign.donate_url = f"/donate/{escape(campaign.campaignid)}"

    #Calculate stats
    total_donations = Donation.objects.filter(donation_type__in=['General', 'Campaign']).aggregate(Sum('amount'))['amount__sum'] or 0
    total_donors = Donor.objects.count()
    total_campaigns = Campaign.objects.filter(status='Approved').count()

    return render(request, 'donorpage.html', {
        'donor': donor,
        'campaigns': campaigns,
        'total_donations': total_donations,
        'total_donors': total_donors,
        'total_campaigns': total_campaigns,
    })

# ------------------- DONOR SIGNUP -------------------
def signup_donor(request):
    if request.method == 'POST':
        fullname = request.POST.get('full_name')
        phone = request.POST.get('phone')
        dob = request.POST.get('dob')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        gender = request.POST.get('gender')

        if Donor.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.', extra_tags='signup')
            return render(request, 'signupdonor.html', {'is_signup': True})

        if Donor.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists.', extra_tags='signup')
            return render(request, 'signupdonor.html', {'is_signup': True})

        new_donor = Donor(
            fullname=fullname,
            phone=phone,
            dob=dob,
            email=email,
            username=username,
            password=password,
            gender=gender
        )
        new_donor.save()
        messages.success(request, 'Registration successful! Please log in.')
        return redirect('login_donor')

    return render(request, 'signupdonor.html', {'is_signup': True})

# ------------------- LOGOUT -------------------
def logout_view(request):
    request.session.flush()
    return redirect('login_page')

# ------------------- DONOR PROFILE -------------------
def donor_profile(request):
    donor_id = request.session.get('donor_id')
    if not donor_id:
        return redirect('login_donor')

    try:
        donor = Donor.objects.get(donorid=donor_id)
    except Donor.DoesNotExist:
        messages.error(request, "Donor not found.")
        return redirect('login_donor')

    return render(request, 'donorprofilepage.html', {'donor': donor})

# ------------------- DONOR EDIT PROFILE -------------------
def donor_edit_profile(request):
    donor_id = request.session.get('donor_id')
    if not donor_id:
        return redirect('login_donor')

    try:
        donor = Donor.objects.get(donorid=donor_id)
    except Donor.DoesNotExist:
        messages.error(request, "Donor not found.", extra_tags='edit_profile')
        return redirect('login_donor')

    if request.method == 'POST':
        donor.fullname = request.POST.get('fullname')
        donor.username = request.POST.get('username')
        donor.gender = request.POST.get('gender')
        donor.dob = request.POST.get('dob')
        donor.phone = request.POST.get('phone')
        donor.email = request.POST.get('email')
        donor.save()
        messages.success(request, 'Profile updated successfully!', extra_tags='edit_profile')
        return redirect('donorprofile')

    return render(request, 'donoreditprofilepage.html', {'donor': donor, 'is_edit_profile': True})

def manage_campaigns(request):
    treasurer_id = request.session.get('treasurer_id')
    if not treasurer_id:
        return redirect('login_admin')

    treasurer = get_object_or_404(Treasurer, treasurerid=treasurer_id)
    campaigns = Campaign.objects.all()

    today = date.today()
    for campaign in campaigns:
        # Approval status
        campaign.approval_status = campaign.status

        # Progress status based on date & goal
        if campaign.status == 'Approved':
            if campaign.end_date < today or campaign.current_amount >= campaign.goal_amount:
                campaign.progress_status = 'Completed'
            elif campaign.start_date <= today <= campaign.end_date:
                campaign.progress_status = 'Ongoing'
            elif campaign.start_date > today:
                campaign.progress_status = 'Upcoming'
            else:
                campaign.progress_status = '-'
        else:
            campaign.progress_status = '-'

    return render(request, 'managecampaign.html', {
        'treasurer': treasurer,
        'campaigns': campaigns
    })

def add_campaign(request):
    treasurer_id = request.session.get('treasurer_id')
    if not treasurer_id:
        return redirect('login_admin')

    try:
        treasurer = Treasurer.objects.get(treasurerid=treasurer_id)
    except Treasurer.DoesNotExist:
        messages.error(request, "Treasurer not found.")
        return redirect('login_admin')

    if request.method == 'POST':
        campaignid = request.POST.get('campaignid')
        title = request.POST.get('title')
        description = request.POST.get('description')
        goal_amount = request.POST.get('goal_amount')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        campaignimage = request.FILES.get('campaignimage')

        # Optional: Check if campaign ID already exists
        if Campaign.objects.filter(campaignid=campaignid).exists():
            messages.error(request, "Campaign ID already exists.")
            return render(request, 'addcampaign.html', {'treasurer': treasurer})

        Campaign.objects.create(
            campaignid=campaignid,
            title=title,
            description=description,
            goal_amount=goal_amount,
            start_date=start_date,
            end_date=end_date,
            campaignimage=campaignimage,
            status='Pending',
        )

        messages.success(request, "Campaign added successfully!")
        return redirect('manage_campaigns')

    return render(request, 'addcampaign.html', {'treasurer': treasurer})

# -------- Show Donate Page --------
def donate_page(request):
    donor = None
    donor_id = request.session.get('donor_id')
    if donor_id:
        donor = Donor.objects.filter(donorid=donor_id).first()
    return render(request, 'donatepage.html', {'donor': donor})


def submit_donation(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        date_str = request.POST.get('date_donated')
        anonymous = request.POST.get('anonymous') == 'on'
        receipt = request.FILES.get('receipt')

        # Validate required fields
        if not amount or not date_str:
            messages.error(request, "Please complete all required fields.")
            return redirect('donate_page')

        try:
            # Convert the string to datetime object
            donation_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messages.error(request, "Invalid date format.")
            return redirect('donate_page')

        donor_instance = None
        if not anonymous:
            donor_id = request.session.get('donor_id')
            donor_instance = Donor.objects.filter(donorid=donor_id).first()
            if not donor_instance:
                messages.error(request, "Donor not found.")
                return redirect('donate_page')

        # Save donation
        donation = Donation.objects.create(
            donorid=donor_instance,
            campaignid=None,  # General donation
            amount=amount,
            date_donated=donation_date,
            donation_type='General',
            receipt=receipt
        )

        messages.success(request, "Thank you for your donation!")
        return redirect('donor_mainpage')

    return redirect('donate_page')

# -------- Donation History Page --------
def donor_history(request):
    donor_id = request.session.get('donor_id')
    if not donor_id:
        messages.error(request, "Please log in to view your donation history.")
        return redirect('donor_login')

    donor = Donor.objects.filter(donorid=donor_id).first()

    general_donations = Donation.objects.filter(
        donorid=donor, donation_type='General', hidden_from_donor=False
    )
    campaign_donations = Donation.objects.filter(
        donorid=donor, donation_type='Campaign', hidden_from_donor=False
    )

    return render(request, 'history.html', {
        'donor': donor,
        'general_donations': general_donations,
        'campaign_donations': campaign_donations,
    })



# -------- Delete a Single Donation --------
@require_POST
def delete_donation(request, donation_id):
    donor_id = request.session.get('donor_id')
    donation = get_object_or_404(Donation, donationid=donation_id)

    if donation.donorid and donation.donorid.donorid == donor_id:
        donation.hidden_from_donor = True
        donation.save()
        messages.success(request, "Succesfully delete donation history.")
    else:
        messages.error(request, "Unsuccessful delete donation history.")

    return redirect('donor_history')


# -------- Clear All Donation History --------
@require_POST
def clear_donation_history(request):
    donor_id = request.session.get('donor_id')
    if not donor_id:
        messages.error(request, "Login required.")
        return redirect('donor_login')

    donor = Donor.objects.filter(donorid=donor_id).first()
    Donation.objects.filter(donorid=donor).update(hidden_from_donor=True)
    messages.success(request, "All donation history is clear.")
    return redirect('donor_history')


def record_donation_page(request):
    treasurer_id = request.session.get('treasurer_id')
    treasurer = get_object_or_404(Treasurer, treasurerid=treasurer_id)

    selected_year = request.GET.get('year')
    selected_month = request.GET.get('month')

    # Filtered querysets for totals and tables
    filtered_general = Donation.objects.filter(donation_type='General')
    filtered_campaign = Donation.objects.filter(donation_type='Campaign')
    filtered_tabung = TabungDonation.objects.all()

    if selected_year:
        filtered_general = filtered_general.filter(date_donated__year=selected_year)
        filtered_campaign = filtered_campaign.filter(date_donated__year=selected_year)
        filtered_tabung = filtered_tabung.filter(date__year=selected_year)

    if selected_month:
        filtered_general = filtered_general.filter(date_donated__month=selected_month)
        filtered_campaign = filtered_campaign.filter(date_donated__month=selected_month)
        filtered_tabung = filtered_tabung.filter(date__month=selected_month)

    # Filtered totals
    general_total = filtered_general.aggregate(Sum('amount'))['amount__sum'] or 0
    campaign_total = filtered_campaign.aggregate(Sum('amount'))['amount__sum'] or 0
    tabung_total = filtered_tabung.aggregate(Sum('amount'))['amount__sum'] or 0
    overall_total = general_total + campaign_total + tabung_total

    # For dropdown filters
    donation_years = Donation.objects.annotate(y=ExtractYear('date_donated')).values_list('y', flat=True)
    tabung_years = TabungDonation.objects.annotate(y=ExtractYear('date')).values_list('y', flat=True)
    years = sorted(set(donation_years).union(tabung_years), reverse=True)
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]

    context = {
        'treasurer': treasurer,
        'general_total': general_total,
        'campaign_total': campaign_total,
        'tabung_total': tabung_total,
        'overall_total': overall_total,
        'general_donations': filtered_general,
        'campaign_donations': filtered_campaign,
        'tabung_donations': filtered_tabung,
        'years': years,
        'months': months,
    }

    return render(request, 'recorddonation.html', context)

def submit_tabung_donation(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        amount = request.POST.get('amount')

        if not date or not amount:
            messages.error(request, "Please provide both date and amount.")
            return redirect('record_donation_page')

        TabungDonation.objects.create(
            date=date,
            amount=amount
        )
        messages.success(request, "Tabung donation added successfully.")
        return redirect('record_donation_page')

    return redirect('record_donation_page')

def delete_tabung_donation(request, donationid):
    donation = get_object_or_404(TabungDonation, donationid=donationid)
    donation.delete()
    messages.success(request, "Tabung donation deleted.")
    return redirect('record_donation_page')

def edit_tabung_donation(request, donationid):
    donation = get_object_or_404(TabungDonation, donationid=donationid)

    # Get treasurer info from session
    treasurer = None
    treasurer_id = request.session.get('treasurer_id')
    if treasurer_id:
        from .models import Treasurer
        treasurer = Treasurer.objects.filter(treasurerid=treasurer_id).first()

    if request.method == 'POST':
        date = request.POST.get('date')
        amount = request.POST.get('amount')

        if not date or not amount:
            messages.error(request, "Please fill in all required fields.")
            return redirect('edit_tabung_donation', donationid=donationid)

        donation.date = date
        donation.amount = amount
        donation.save()

        messages.success(request, "Tabung donation updated successfully.")
        return redirect('record_donation_page')

    return render(request, 'edittabung.html', {
        'donation': donation,
        'treasurer': treasurer
    })

# GENERAL DONATION EDIT & DELETE
def edit_general_donation(request, donationid):
    donation = get_object_or_404(Donation, donationid=donationid, donation_type='General')

    if request.method == 'POST':
        date = request.POST.get('date_donated')
        amount = request.POST.get('amount')

        if date and amount:
            donation.date_donated = date
            donation.amount = amount
            donation.save()
            messages.success(request, "General donation updated successfully.")
            return redirect('record_donation_page')
        else:
            messages.error(request, "All fields are required.")

    
    treasurer_id = request.session.get('treasurer_id')
    treasurer = None
    if treasurer_id:
        from .models import Treasurer
        treasurer = Treasurer.objects.filter(treasurerid=treasurer_id).first()

    return render(request, 'editgeneral.html', {
        'donation': donation,
        'treasurer': treasurer
    })
def delete_general_donation(request, donationid):
    donation = get_object_or_404(Donation, donationid=donationid, donation_type='General')
    donation.delete()
    messages.success(request, "General donation deleted successfully.")
    return redirect('record_donation_page')

# CAMPAIGN DONATION EDIT & DELETE
def edit_campaign_donation(request, donationid):
    # Get the donation object and ensure it's a Campaign donation
    donation = get_object_or_404(Donation, donationid=donationid, donation_type='Campaign')

    if request.method == 'POST':
        try:
            donation.amount = Decimal(request.POST.get('amount'))
            donation.date_donated = request.POST.get('date_donated')  # Corrected field name
            donation.save()
            messages.success(request, "Campaign donation updated successfully.")
            return redirect('record_donation_page')
        except Exception as e:
            messages.error(request, f"Error updating donation: {e}")

    context = {
        'donation': donation,
        'donor': donation.donorid,
        'campaign': donation.campaignid
    }
    return render(request, 'editcampaign.html', context)
def delete_campaign_donation(request, donationid):
    donation = get_object_or_404(Donation, donationid=donationid, donation_type='Campaign')
    donation.delete()
    messages.success(request, "Campaign donation deleted.")
    return redirect('record_donation_page')

def donor_campaigns(request):
    donor_id = request.session.get('donor_id')
    if not donor_id:
        return redirect('login_donor')

    try:
        donor = Donor.objects.get(donorid=donor_id)
    except Donor.DoesNotExist:
        return redirect('login_donor')

    #Only show approved and ongoing
    campaigns = Campaign.objects.filter(
        status='Approved',
        end_date__gte=date.today()
    ).exclude(current_amount__gte=models.F('goal_amount')).order_by('end_date')

    for campaign in campaigns:
        campaign.percentage = int((campaign.current_amount / campaign.goal_amount) * 100) if campaign.goal_amount > 0 else 0
        campaign.days_left = max((campaign.end_date - date.today()).days, 0)
        campaign.amount_raised = campaign.current_amount
        campaign.goal = campaign.goal_amount
        campaign.image_url = campaign.campaignimage.url if campaign.campaignimage else ""

    return render(request, 'campaign.html', {
        'donor': donor,
        'campaigns': campaigns
    })


def donate_campaign(request, campaign_id):
    donor_id = request.session.get('donor_id')
    donor = get_object_or_404(Donor, donorid=donor_id)
    campaign = get_object_or_404(Campaign, campaignid=campaign_id)

    if request.method == "POST":
        date_str = request.POST.get('date_donated')
        amount = request.POST.get('amount')
        receipt = request.FILES.get('receipt')
        anonymous = request.POST.get('anonymous') == 'on'

        try:
            donation_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messages.error(request, "Invalid donation date.")
            return redirect('donate_campaign', campaign_id=campaign_id)

        donor_instance = donor if not anonymous else None

        # Save donation
        Donation.objects.create(
            donorid=donor_instance,
            campaignid=campaign,
            date_donated=donation_date,
            amount=amount,
            receipt=receipt,
            donation_type='Campaign'
        )

        # Update campaign total
        campaign.current_amount += Decimal(amount)
        campaign.save()

        messages.success(request, "Thank you for your donation!")
        return redirect('donor_campaigns')

    context = {
        'donor': donor,
        'campaign': campaign,
        'percentage': int((campaign.current_amount / campaign.goal_amount) * 100) if campaign.goal_amount > 0 else 0,
        'days_left': max((campaign.end_date - date.today()).days, 0),
    }
    return render(request, 'donatecampaign.html', context)

def edit_campaign(request, campaignid):
    treasurer_id = request.session.get('treasurer_id')
    treasurer = get_object_or_404(Treasurer, treasurerid=treasurer_id)

    campaign = get_object_or_404(Campaign, campaignid=campaignid)

    if request.method == 'POST':
        campaign.title = request.POST.get('title')
        campaign.description = request.POST.get('description')
        campaign.goal_amount = request.POST.get('goal_amount')
        campaign.start_date = request.POST.get('start_date')
        campaign.end_date = request.POST.get('end_date')

        # Handle optional image update
        if request.FILES.get('campaignimage'):
            campaign.campaignimage = request.FILES['campaignimage']

        campaign.save()
        messages.success(request, 'Campaign updated successfully.')
        return redirect('manage_campaigns')

    return render(request, 'editcampaigndetails.html', {
        'campaign': campaign,
        'treasurer': treasurer
    })

def delete_campaign(request, campaignid):
    treasurer_id = request.session.get('treasurer_id')
    treasurer = get_object_or_404(Treasurer, treasurerid=treasurer_id)

    campaign = get_object_or_404(Campaign, campaignid=campaignid)

    if request.method == 'POST':
        campaign.delete()
        messages.success(request, 'Campaign deleted successfully.')
        return redirect('manage_campaigns')

    return render(request, 'confirm_delete_campaign.html', {'campaign': campaign, 'treasurer': treasurer})

def financial_page(request):
    treasurer_id = request.session.get('treasurer_id')
    treasurer = get_object_or_404(Treasurer, treasurerid=treasurer_id)

    selected_year = request.GET.get('year')
    selected_month = request.GET.get('month')
    financial_records = Financial.objects.all().order_by('-date')

    if selected_year:
        financial_records = financial_records.filter(date__year=selected_year)
    if selected_month:
        financial_records = financial_records.filter(date__month=selected_month)

    if request.method == 'POST':
        record_type = request.POST.get('type')
        date_value = request.POST.get('date')
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        source = request.POST.get('source') if record_type == 'Income' else None
        purpose = request.POST.get('purpose') if record_type == 'Expense' else None

        campaign_obj = None
        if purpose == 'Campaign':
            campaign_id = request.POST.get('campaign_id')
            if campaign_id:
                campaign_obj = get_object_or_404(Campaign, pk=campaign_id)

        Financial.objects.create(
            date=date_value,
            type=record_type,
            source=source,
            purpose=purpose,
            campaign=campaign_obj,  
            description=description,
            amount=amount,
            recorded_by=treasurer
        )
        messages.success(request, "Financial record added successfully.")
        return redirect('financial_page')

    # Summary (not filtered)
    total_income = Financial.objects.filter(type='Income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Financial.objects.filter(type='Expense').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense

    year_values = Financial.objects.annotate(y=ExtractYear('date')).values_list('y', flat=True).distinct()
    years = sorted(set(year_values), reverse=True)
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    campaigns = Campaign.objects.all()  

    context = {
        'treasurer': treasurer,
        'financial_records': financial_records,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'years': years,
        'months': months,
        'campaigns': campaigns  
    }

    return render(request, 'financial.html', context)

    
    total_income = Financial.objects.filter(type='Income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Financial.objects.filter(type='Expense').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense

    
    year_values = Financial.objects.annotate(y=ExtractYear('date')).values_list('y', flat=True).distinct()
    years = sorted(set(year_values), reverse=True)
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]

    # Campaigns (for dropdown)
    campaigns = Campaign.objects.all()

    context = {
        'treasurer': treasurer,
        'financial_records': financial_records,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'years': years,
        'months': months,
        'campaigns': campaigns,
    }

    return render(request, 'financial.html', context)

def edit_financial(request, financialid):
    treasurer_id = request.session.get('treasurer_id')
    treasurer = get_object_or_404(Treasurer, treasurerid=treasurer_id)
    financial = get_object_or_404(Financial, pk=financialid)
    campaigns = Campaign.objects.all()

    if request.method == 'POST':
        financial.date = request.POST.get('date')
        financial.type = request.POST.get('type')
        financial.source = request.POST.get('source') if financial.type == 'Income' else None
        financial.purpose = request.POST.get('purpose') if financial.type == 'Expense' else None
        campaign_id = request.POST.get('campaign_id') if financial.purpose == 'Campaign' else None
        financial.campaign_id = campaign_id  # Automatically handles None
        financial.description = request.POST.get('description')
        financial.amount = request.POST.get('amount')
        financial.save()
        messages.success(request, 'Financial record updated successfully.')
        return redirect('financial_page')

    return render(request, 'editfinancial.html', {
        'financial': financial,
        'treasurer': treasurer,
        'campaigns': campaigns
    })


def delete_financial(request, financialid):
    financial = get_object_or_404(Financial, financialid=financialid)
    financial.delete()
    messages.success(request, "Financial record deleted successfully.")
    return redirect('financial_page')

def allocate_fund_page(request):
    treasurer_id = request.session.get('treasurer_id')
    treasurer = get_object_or_404(Treasurer, treasurerid=treasurer_id)

    
    if request.method == 'POST':
        year = int(request.POST.get('year'))
        month = int(request.POST.get('month'))
        category = request.POST.get('category')
        amount = request.POST.get('amount')
        description = request.POST.get('description')

        allocation_date = date(year, month, 1)  

        AllocateFund.objects.create(
            date=allocation_date,
            category=category,
            amount=amount,
            description=description,
            recorded_by=treasurer
        )
        messages.success(request, "Fund allocated successfully.")
        return redirect('allocate_fund_page')

    
    selected_year = request.GET.get('year')
    selected_month = request.GET.get('month')

    allocations = AllocateFund.objects.all().order_by('-date')
    if selected_year:
        allocations = allocations.filter(date__year=selected_year)
    if selected_month:
        allocations = allocations.filter(date__month=selected_month)

    
    all_years = AllocateFund.objects.dates('date', 'year', order='DESC')
    years = [y.year for y in all_years]

    if not years:
        current_year = date.today().year
        years = [current_year, current_year - 1]

    months = [(i, calendar.month_name[i]) for i in range(1, 13)]

   
    filtered_allocations = AllocateFund.objects.all()
    if selected_year:
        filtered_allocations = filtered_allocations.filter(date__year=selected_year)
    if selected_month:
        filtered_allocations = filtered_allocations.filter(date__month=selected_month)

    category_totals = {
        cat[0]: filtered_allocations.filter(category=cat[0]).aggregate(Sum('amount'))['amount__sum'] or 0
        for cat in AllocateFund.CATEGORY_CHOICES
    }

    total_allocated = filtered_allocations.aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'treasurer': treasurer,
        'allocations': allocations,
        'years': years,
        'months': months,
        'total_allocated': total_allocated,
        'category_totals': category_totals,
    }

    return render(request, 'fund.html', context)

def edit_allocate_fund(request, allocateid):
    allocation = get_object_or_404(AllocateFund, pk=allocateid)
    treasurer_id = request.session.get('treasurer_id')
    treasurer_obj = get_object_or_404(Treasurer, treasurerid=treasurer_id)

    current_year = date.today().year  
    years = list(range(current_year, current_year - 10, -1))
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]  # [(1, 'January'), ...]

    if request.method == 'POST':
        year = int(request.POST['year'])
        month = int(request.POST['month'])
        fund_date = date(year, month, 1)  

        allocation.date = fund_date
        allocation.category = request.POST['category']
        allocation.amount = request.POST['amount']
        allocation.description = request.POST['description']
        allocation.save()

        messages.success(request, "Fund allocation updated successfully.")
        return redirect('allocate_fund_page')

    return render(request, 'editallocatefund.html', {
        'allocation': allocation,
        'treasurer': treasurer_obj,
        'years': years,
        'months': months,
    })

def delete_allocate_fund(request, allocateid):
    allocation = get_object_or_404(AllocateFund, pk=allocateid)
    allocation.delete()
    messages.success(request, "Allocation deleted successfully.")
    return redirect('allocate_fund_page')

def admin_mainpage(request):
    
    admin_id = request.session.get('admin_id')

    if not admin_id:
        return redirect('admin_login')  

    try:
        admin = Admin.objects.get(adminid=admin_id)
    except Admin.DoesNotExist:
        return redirect('admin_login')

    return render(request, 'adminpage.html', {'admin': admin})

def manage_donors(request):
    admin_id = request.session.get('admin_id')
    if not admin_id:
        return redirect('admin_login')

    admin = get_object_or_404(Admin, adminid=admin_id) 
    donors = Donor.objects.all()

    return render(request, 'managedonors.html', {
        'donors': donors,
        'admin': admin,  
    })


# Edit donor
def edit_donor(request, donorid):
    admin_id = request.session.get('admin_id')
    if not admin_id:
        return redirect('admin_login')

    admin = get_object_or_404(Admin, adminid=admin_id)  # ✅ Add this line
    donor = get_object_or_404(Donor, donorid=donorid)

    if request.method == 'POST':
        donor.fullname = request.POST.get('fullname')
        donor.email = request.POST.get('email')
        donor.phone = request.POST.get('phone')
        donor.save()
        messages.success(request, 'Donor profile updated successfully.')
        return redirect('manage_donors')

    return render(request, 'editdonor.html', {
        'donor': donor,
        'admin': admin,  
    })

def delete_donor(request, donorid):
    admin_id = request.session.get('admin_id')
    if not admin_id:
        return redirect('admin_login')

    
    donor = get_object_or_404(Donor, donorid=donorid)
    donor.delete()
    messages.success(request, 'Donor deleted successfully.')
    return redirect('manage_donors')

def manage_treasurers(request):
    admin_id = request.session.get('admin_id')
    if not admin_id:
        return redirect('admin_login')
    
    from .models import Admin
    admin = Admin.objects.get(adminid=admin_id)

    treasurers = Treasurer.objects.all()
    return render(request, 'managetreasurers.html', {'treasurers': treasurers, 'admin': admin})


# View: Edit Treasurer
def edit_treasurer(request, treasurerid):
    treasurer = get_object_or_404(Treasurer, treasurerid=treasurerid)
    
    if request.method == 'POST':
        treasurer.name = request.POST.get('name')
        treasurer.email = request.POST.get('email')
        treasurer.password = request.POST.get('password')
        treasurer.save()
        messages.success(request, 'Treasurer updated successfully!')
        return redirect('manage_treasurers')

    return render(request, 'edittreasurers.html', {'treasurer': treasurer})


# View: Delete Treasurer
def delete_treasurer(request, treasurerid):
    treasurer = get_object_or_404(Treasurer, treasurerid=treasurerid)
    treasurer.delete()
    messages.success(request, 'Treasurer deleted successfully!')
    return redirect('manage_treasurers')

def manage_campaigns_admin(request):
    admin_id = request.session.get('admin_id')
    if not admin_id:
        return redirect('admin_login')

    admin = get_object_or_404(Admin, adminid=admin_id)
    campaigns = Campaign.objects.all().order_by('-start_date')

    today = date.today()
    for campaign in campaigns:
        # Approval status
        campaign.approval_status = campaign.status

        # Progress status
        if campaign.status == 'Approved':
            if campaign.end_date < today or campaign.current_amount >= campaign.goal_amount:
                campaign.progress_status = 'Completed'
            elif campaign.start_date <= today <= campaign.end_date:
                campaign.progress_status = 'Ongoing'
            elif campaign.start_date > today:
                campaign.progress_status = 'Upcoming'
            else:
                campaign.progress_status = '-'
        else:
            campaign.progress_status = '-'

    return render(request, 'admincampaigns.html', {
        'admin': admin,
        'campaigns': campaigns,
    })


def approve_campaign(request, campaignid):
    if request.method == 'POST':
        campaign = get_object_or_404(Campaign, campaignid=campaignid)
        campaign.status = 'Approved'
        campaign.save()
        messages.success(request, f"Campaign '{campaign.title}' approved successfully.")
    return redirect('admin_manage_campaigns')


def reject_campaign(request, campaignid):
    if request.method == 'POST':
        campaign = get_object_or_404(Campaign, campaignid=campaignid)
        campaign.status = 'Rejected'
        campaign.save()
        messages.success(request, f"Campaign '{campaign.title}' rejected.")
    return redirect('admin_manage_campaigns')

def report_donation_view(request):
    admin_id = request.session.get('admin_id')
    if not admin_id:
        return redirect('admin_login')
    admin = get_object_or_404(Admin, adminid=admin_id)

    year = request.GET.get('year')
    month = request.GET.get('month')

    # Filter Donations
    donations = Donation.objects.all()
    if year:
        donations = donations.filter(date_donated__year=year)
    if month:
        donations = donations.filter(date_donated__month=month)

    # Filter Tabung Donations
    tabung_donations = TabungDonation.objects.all()
    if year:
        tabung_donations = tabung_donations.filter(date__year=year)
    if month:
        tabung_donations = tabung_donations.filter(date__month=month)

    # Breakdown
    general_donations = donations.filter(donation_type='General')
    campaign_donations = donations.filter(donation_type='Campaign')

    general_total = general_donations.aggregate(Sum('amount'))['amount__sum'] or 0
    campaign_total = campaign_donations.aggregate(Sum('amount'))['amount__sum'] or 0
    tabung_total = tabung_donations.aggregate(Sum('amount'))['amount__sum'] or 0

    total_donations = general_total + campaign_total + tabung_total

    # Campaign stats
    total_goals = Campaign.objects.filter(status='Approved').aggregate(Sum('goal_amount'))['goal_amount__sum'] or 0
    total_raised = Campaign.objects.aggregate(Sum('current_amount'))['current_amount__sum'] or 0

   
    total_income = Financial.objects.filter(type='Income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Financial.objects.filter(type='Expense').aggregate(Sum('amount'))['amount__sum'] or 0
    current_balance = total_income - total_expense

    # Report records
    reports = Report.objects.all().order_by('-generated_date')

    # Filter options
    donation_years = Donation.objects.annotate(y=ExtractYear('date_donated')).values_list('y', flat=True)
    tabung_years = TabungDonation.objects.annotate(y=ExtractYear('date')).values_list('y', flat=True)
    years = sorted(set(donation_years).union(tabung_years), reverse=True)
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]

    return render(request, 'reportdonation.html', {
        'admin': admin,
        'total_donations': total_donations,
        'general_total': general_total,
        'campaign_total': campaign_total,
        'tabung_total': tabung_total,
        'total_goals': total_goals,
        'total_raised': total_raised,
        'balance': current_balance, 
        'general_donations': general_donations,
        'campaign_donations': campaign_donations,
        'tabung_donations': tabung_donations,
        'reports': reports,
        'years': years,
        'months': months,
        'selected_year': year,
        'selected_month': month,
    })

import os
from io import BytesIO
from datetime import datetime
from django.conf import settings
from django.core.files.base import ContentFile
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

def generate_report_pdf(request):
    admin_id = request.session.get('admin_id')
    if not admin_id:
        return redirect('admin_login')
    admin = get_object_or_404(Admin, adminid=admin_id)

    year = request.GET.get('year')
    month = request.GET.get('month')

    donations = Donation.objects.all()
    tabung_donations = TabungDonation.objects.all()

    if year:
        donations = donations.filter(date_donated__year=year)
        tabung_donations = tabung_donations.filter(date__year=year)
    if month:
        donations = donations.filter(date_donated__month=month)
        tabung_donations = tabung_donations.filter(date__month=month)

    general_donations = donations.filter(donation_type='General')
    campaign_donations = donations.filter(donation_type='Campaign')

    general_total = general_donations.aggregate(Sum('amount'))['amount__sum'] or 0
    campaign_total = campaign_donations.aggregate(Sum('amount'))['amount__sum'] or 0
    tabung_total = tabung_donations.aggregate(Sum('amount'))['amount__sum'] or 0
    total_donations = general_total + campaign_total + tabung_total

    total_goals = Campaign.objects.aggregate(Sum('goal_amount'))['goal_amount__sum'] or 0
    total_raised = Campaign.objects.aggregate(Sum('current_amount'))['current_amount__sum'] or 0

    total_income = Financial.objects.filter(type='Income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Financial.objects.filter(type='Expense').aggregate(Sum('amount'))['amount__sum'] or 0
    current_balance = total_income - total_expense

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 60

    # ✅ Logo
    logo_path = os.path.join(settings.STATICFILES_DIRS[0], 'Sadaqahlogo.png')
    if os.path.exists(logo_path):
        try:
            p.drawImage(logo_path, 40, y, width=100, height=40, mask='auto')
        except Exception as e:
            print("Logo not shown:", e)
    y -= 60

    # Header
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width / 2, y, "Donation Report")
    y -= 25

    p.setFont("Helvetica", 10)
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    p.drawCentredString(width / 2, y, f"Generated by {admin.name} on {now}")
    y -= 30

    # Summary table
    summary = [
        ["Total Donations", f"RM {total_donations:.2f}"],
        ["General Donations", f"RM {general_total:.2f}"],
        ["Campaign Donations", f"RM {campaign_total:.2f}"],
        ["Tabung Donations", f"RM {tabung_total:.2f}"],
        ["Total Raised vs Goals", f"RM {total_raised:.2f} / RM {total_goals:.2f}"],
        ["Current Balance", f"RM {current_balance:.2f}"],
    ]
    table = Table(summary, colWidths=[200, 200])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    table.wrapOn(p, width, height)
    table.drawOn(p, 40, y - 120)
    y -= 160

    def draw_table(title, data, col_widths):
        nonlocal y
        if y < 200:  # move to next page if near bottom
            p.showPage()
            y = height - 80

        p.setFont("Helvetica-Bold", 12)
        p.drawString(40, y, title)
        y -= 15

        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        table.wrapOn(p, width, height)
        table.drawOn(p, 40, y - len(data) * 15)
        y -= len(data) * 15 + 30

    if general_donations.exists():
        data = [["No", "Donor", "Date", "Amount"]]
        for idx, d in enumerate(general_donations, 1):
            data.append([
                str(idx),
                d.donorid.fullname if d.donorid else "Anonymous",
                d.date_donated.strftime("%Y-%m-%d"),
                f"RM {d.amount:.2f}"
            ])
        draw_table("General Donations", data, [30, 180, 100, 80])

    if campaign_donations.exists():
        data = [["No", "Campaign", "Donor", "Date", "Amount"]]
        for idx, d in enumerate(campaign_donations, 1):
            data.append([
                str(idx),
                d.campaignid.title if d.campaignid else "-",
                d.donorid.fullname if d.donorid else "Anonymous",
                d.date_donated.strftime("%Y-%m-%d"),
                f"RM {d.amount:.2f}"
            ])
        draw_table("Campaign Donations", data, [30, 180, 100, 90, 70])  # Wider title

    if tabung_donations.exists():
        data = [["No", "Date", "Amount"]]
        for idx, d in enumerate(tabung_donations, 1):
            data.append([
                str(idx),
                d.date.strftime("%Y-%m-%d"),
                f"RM {d.amount:.2f}"
            ])
        draw_table("Tabung Donations", data, [30, 180, 100])

    p.showPage()
    p.save()
    buffer.seek(0)

    # Determine filename label
    month_label = calendar.month_name[int(month)] if month and month.isdigit() else "All Months"
    year_label = year if year else "All Years"
    filename = f"Donation Report - {month_label}, {year_label}.pdf"

    # Save report to DB
    report_file = ContentFile(buffer.read())
    report = Report(
        title=f"Donation Report - {month_label}, {year_label}",
        total_donations=total_donations,
        generated_by=admin
    )
    report.file.save(filename.replace(" ", "_"), report_file)
    report.save()

    return FileResponse(open(report.file.path, 'rb'), as_attachment=True, filename=filename)
