#imports/mview
from django.shortcuts import render, redirect, get_object_or_404
import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Import, Package
import pandas as pd
from .models import Import, Package, ImportDetail
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from .models import ImportDetail, Import
from .models import Import, Package, ImportDetail, PACKAGE_TYPE_CHOICES
from .forms import ImportForm, PackageForm
from django.contrib.auth import authenticate
from django.contrib import messages
from django.http import HttpResponse





@login_required
def register_import(request):
    if request.method == 'POST':
        import_form = ImportForm(request.POST)

        if import_form.is_valid():
            new_import = import_form.save()

            # Retrieve import number
            import_number = new_import.unique_number  

            # Save package data
            package_data_json = request.POST.get('packages', '[]')
            package_data = json.loads(package_data_json) if package_data_json else []

            for package in package_data:
                Package.objects.create(
                    import_instance=new_import,
                    package_type=package['packageType'],
                    length=float(package['length']),
                    width=float(package['width']),
                    height=float(package['height']),
                    gross_weight=float(package['grossWeight'])
                )

            # Save excel data
            excel_data_json = request.POST.get('excel_data', '[]')
            excel_data = json.loads(excel_data_json) if excel_data_json else []

            for record in excel_data:
                ImportDetail.objects.create(
                    import_instance=new_import,
                    po_number=record['poNumber'],
                    line_number=int(record['lineNumber']),
                    item_number=record['itemNumber'],
                    description_eng=record['descriptionEng'],
                    quantity=int(record['quantity']),
                    unit_cost=float(record['unitCost']),
                    line_cost=float(record['lineCost']),
                )

            return redirect('import_list')

    else:
        import_form = ImportForm()

        # Generate new Import Number
        last_import = Import.objects.all().order_by('id').last()
        new_number = int(last_import.unique_number.replace("IMP", "")) + 1 if last_import else 1
        import_number = f"IMP{str(new_number).zfill(5)}"

    return render(request, 'imports/register_import.html', {
        'import_form': import_form,
        'import_number': import_number,  # ✅ Pass import number to the template
        'package_type_choices': PACKAGE_TYPE_CHOICES  # ✅ Fix variable name
    })




@login_required
def import_list(request):
    imports = Import.objects.all().order_by('-date_created')  # Order by most recent
    return render(request, 'imports/import_list.html', {'imports': imports})

@login_required
def import_detail(request, unique_number):
    import_instance = get_object_or_404(Import, unique_number=unique_number)
    packages = Package.objects.filter(import_instance=import_instance)
    import_details = ImportDetail.objects.filter(import_instance=import_instance)  # ✅ Fetch Excel data

    return render(request, 'imports/import_detail.html', {
        'import': import_instance,
        'packages': packages,
        'import_details': import_details  # ✅ Pass Excel data to the template
    })





@login_required
def edit_import(request, unique_number):
    import_instance = get_object_or_404(Import, unique_number=unique_number)

    if request.method == "POST":
        form = ImportForm(request.POST, instance=import_instance)
        if form.is_valid():
            form.save()
            return redirect('import_list')
    else:
        form = ImportForm(instance=import_instance)

    return render(request, 'imports/edit_import.html', {'form': form, 'import': import_instance})





@login_required
def delete_import(request, unique_number):
    import_instance = get_object_or_404(Import, unique_number=unique_number)

    if request.method == "POST":
        password = request.POST.get("password")

        # Authenticate user before deleting
        user = authenticate(username=request.user.username, password=password)
        if user is not None:
            import_instance.delete()
            messages.success(request, "Import deleted successfully!")
            return redirect("import_list")
        else:
            messages.error(request, "Incorrect password! Import was NOT deleted.")

    return render(request, "imports/delete_import.html", {"import": import_instance})







@login_required
def finish_import(request, unique_number):
    import_instance = get_object_or_404(Import, unique_number=unique_number)
    import_instance.status = 'Finished'
    import_instance.save()
    return JsonResponse({'success': True, 'status': import_instance.status})









@login_required
def upload_excel(request):
    if request.method == "POST" and request.FILES.get("excel_file"):
        excel_file = request.FILES["excel_file"]
        
        # ✅ Save the file temporarily
        fs = FileSystemStorage()
        filename = fs.save(excel_file.name, excel_file)
        file_path = fs.path(filename)

        try:
            # ✅ Read Excel file
            df = pd.read_excel(file_path)

            # ✅ Ensure required columns exist
            required_columns = ["PO Number", "Line Number", "Item Number", "Description Eng", "Quantity", "Unit Cost", "Line Cost"]
            if not all(col in df.columns for col in required_columns):
                return JsonResponse({"error": "Invalid file format. Please upload an Excel file with the correct columns."}, status=400)

            # ✅ Get the latest Import instance (or adjust logic as needed)
            latest_import = Import.objects.last()
            if not latest_import:
                return JsonResponse({"error": "No Import record found! Register an import first."}, status=400)

            # ✅ Save each row to the database
            records = []
            for _, row in df.iterrows():
                record = ImportDetail.objects.create(
                    import_instance=latest_import,
                    po_number=row["PO Number"],
                    line_number=int(row["Line Number"]),
                    item_number=row["Item Number"],
                    description_eng=row["Description Eng"],
                    quantity=int(row["Quantity"]),
                    unit_cost=float(row["Unit Cost"]),
                    line_cost=float(row["Line Cost"]),
                )
                records.append(record)

            return JsonResponse({"success": f"{len(records)} records uploaded successfully!"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "No file uploaded!"}, status=400)






def export_import_excel(request, unique_number):
    try:
        # Fetch import instance
        import_instance = Import.objects.get(unique_number=unique_number)
        details = ImportDetail.objects.filter(import_instance=import_instance)

        # Create an HTTP response with an Excel content type
        output = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        output['Content-Disposition'] = f'attachment; filename="{import_instance.unique_number}_export.xlsx"'

        # Create a Pandas Excel writer
        writer = pd.ExcelWriter(output, engine='xlsxwriter')

        # ✅ Prepare data for single sheet
        data = []

        # Fetching Import Information (First Row)
        base_info = [
            import_instance.unique_number,
            import_instance.vendor_name,
            import_instance.status,
            import_instance.country,
            import_instance.get_incoterms_display(),
            import_instance.get_operation_display(),
            import_instance.pickup_address,
            import_instance.date_created.strftime('%Y-%m-%d'),
            import_instance.updated_at.strftime('%Y-%m-%d'),
        ]

        # If no import details, export only basic import info
        if not details.exists():
            data.append(base_info + ["", "", "", "", "", "", ""])  # Fill remaining columns with empty values
        else:
            # Fetching Import Details
            for detail in details:
                data.append(base_info + [
                    detail.po_number,
                    detail.line_number,
                    detail.item_number,
                    detail.description_eng,
                    detail.quantity,
                    detail.unit_cost,
                    detail.line_cost
                ])

        # Define column names
        columns = [
            "Import Number", "Vendor Name", "Status", "Country", "Incoterms", "Operation", 
            "Pickup Address", "Date Created", "Last Updated",
            "PO Number", "Line Number", "Item Number", "Description", "Quantity", "Unit Cost", "Line Cost"
        ]

        # Create DataFrame and Export to Excel
        df = pd.DataFrame(data, columns=columns)
        df.to_excel(writer, sheet_name="Import Data", index=False)

        # Save the Excel file and return response
        writer.close()
        return output

    except Import.DoesNotExist:
        return HttpResponse("Import not found", status=404)




import pandas as pd
from django.http import HttpResponse
from .models import Import, ImportDetail

def export_all_imports_excel(request):
    # Fetch all import records with related details
    imports = Import.objects.all().prefetch_related("import_details")

    # Prepare Data
    data = []
    
    for import_instance in imports:
        details = ImportDetail.objects.filter(import_instance=import_instance)

        # Base Import Data
        base_info = [
            import_instance.unique_number,
            import_instance.vendor_name,
            import_instance.status,
            import_instance.country,
            import_instance.get_incoterms_display(),
            import_instance.get_operation_display(),
            import_instance.pickup_address,
            import_instance.date_created.strftime('%Y-%m-%d %H:%M:%S'),
            import_instance.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        ]

        # If no details, add a row with empty detail columns
        if not details.exists():
            data.append(base_info + ["", "", "", "", "", "", ""])
        else:
            for detail in details:
                data.append(base_info + [
                    detail.po_number,
                    detail.line_number,
                    detail.item_number,
                    detail.description_eng,
                    detail.quantity,
                    detail.unit_cost,
                    detail.line_cost,
                ])

    # Define column headers
    columns = [
        "Import Number", "Vendor Name", "Status", "Country", "Incoterms", "Operation",
        "Pickup Address", "Date Created", "Last Updated",
        "PO Number", "Line Number", "Item Number", "Description", "Quantity", "Unit Cost", "Line Cost"
    ]

    # Create DataFrame
    df = pd.DataFrame(data, columns=columns)

    # Create HTTP Response for Excel File
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="All_Imports.xlsx"'

    # Write DataFrame to Excel
    with pd.ExcelWriter(response, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="All Imports", index=False)

        # Formatting for readability
        worksheet = writer.sheets["All Imports"]
        for col_num, value in enumerate(df.columns):
            worksheet.set_column(col_num, col_num, max(15, len(value) + 2))

    return response
