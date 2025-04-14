from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import EmailMessage
from django.urls import path
from .models import NotificationEmail
from .forms import NotificationEmailForm
from imports.models import Import, ImportDetail
from io import BytesIO
import pandas as pd
import xlsxwriter

@login_required
def scan_tracking_view(request):
    message = None

    if request.method == 'POST':
        tracking_number = request.POST.get('tracking_number', '').strip()
        action = request.POST.get('action')

        if tracking_number:
            try:
                shipment = Import.objects.get(tracking_number=tracking_number)

                if shipment.status == 'Delivered':
                    message = f"⚠️ Shipment {shipment.unique_number} is already marked as Delivered. Please try another."
                else:
                    shipment.status = 'Delivered'
                    shipment.save()

                    excel_file = generate_import_excel(shipment)

                    email_list = [n.email for n in NotificationEmail.objects.all()]

                    email = EmailMessage(
                        subject=f"📦 Shipment {shipment.unique_number} Delivered",
                        body=f"The shipment {shipment.unique_number} has been delivered.\nVendor: {shipment.vendor_name}",
                        from_email='logistics@shipment.com',
                        to=email_list,
                    )
                    email.attach(
                        f"{shipment.unique_number}.xlsx",
                        excel_file.read(),
                        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    )
                    email.send()

                    message = f"✅ Shipment {shipment.unique_number} marked as Delivered and email sent."

            except Import.DoesNotExist:
                message = "❌ Shipment with this tracking number was not found."
        else:
            message = "⚠️ Please enter a tracking number."

    return render(request, 'warehouse/scan_tracking.html', {'message': message})

def generate_import_excel(import_instance):
    details = ImportDetail.objects.filter(import_instance=import_instance)
    output = BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        data = []
        for detail in details:
            data.append([
                detail.po_number,
                detail.line_number,
                detail.item_number,
                detail.description_eng,
                detail.quantity,
            ])

        columns = ["PO Number", "Line Number", "Item Number", "Description Eng", "Quantity"]
        df = pd.DataFrame(data, columns=columns)
        df.to_excel(writer, sheet_name="Import Summary", index=False)

    output.seek(0)
    return output

@staff_member_required
def add_notification_email(request):
    form = NotificationEmailForm()
    message = None

    if request.method == 'POST':
        form = NotificationEmailForm(request.POST)
        if form.is_valid():
            form.save()
            message = "✅ Email added successfully."

    return render(request, 'warehouse/add_email.html', {'form': form, 'message': message})

@staff_member_required
def manage_notification_emails(request):
    form = NotificationEmailForm()
    message = None

    if request.method == 'POST':
        form = NotificationEmailForm(request.POST)
        if form.is_valid():
            form.save()
            message = "✅ Email added successfully."

    emails = NotificationEmail.objects.all()
    return render(request, 'warehouse/manage_emails.html', {
        'form': form,
        'emails': emails,
        'message': message,
    })

@staff_member_required
def delete_notification_email(request, email_id):
    email = get_object_or_404(NotificationEmail, id=email_id)
    email.delete()
    return redirect('manage_notification_emails')