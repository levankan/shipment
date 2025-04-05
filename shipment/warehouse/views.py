from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from imports.models import Import
from django.core.mail import EmailMessage
from io import BytesIO
from imports.models import Import, ImportDetail, Package
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

                # ✅ თუ უკვე Delivered-ია
                if shipment.status == 'Delivered':
                    message = f"⚠️ Shipment {shipment.unique_number} is already marked as Delivered. Please try another."
                else:
                    # შეცვალე სტატუსი
                    shipment.status = 'Delivered'
                    shipment.save()

                    # გენერაცია + გაგზავნა
                    excel_file = generate_import_excel(shipment)
                    email = EmailMessage(
                        subject=f"📦 Shipment {shipment.unique_number} Delivered",
                        body=f"The shipment {shipment.unique_number} has been delivered.\nVendor: {shipment.vendor_name}",
                        from_email='logistics@shipment.com',
                        to=['warehouse@yourcompany.com'],
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
        # Only selected columns
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
