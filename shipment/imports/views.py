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
        'PACKAGE_TYPE_CHOICES': PACKAGE_TYPE_CHOICES  # ✅ Pass package type choices
    })




@login_required
def import_list(request):
    imports = Import.objects.all().order_by('-date_created')  # Order by most recent
    return render(request, 'imports/import_list.html', {'imports': imports})

@login_required
def import_detail(request, unique_number):
    import_instance = get_object_or_404(Import, unique_number=unique_number)
    return render(request, 'imports/import_detail.html', {'import': import_instance})


@login_required
def import_detail(request, unique_number):
    import_instance = get_object_or_404(Import, unique_number=unique_number)
    packages = Package.objects.filter(import_instance=import_instance)  # Fetch packages
    return render(request, 'imports/import_detail.html', {'import': import_instance, 'packages': packages})







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
        import_instance.delete()
        return redirect('import_list')

    return render(request, 'imports/delete_import.html', {'import': import_instance})












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
