#imports/mview
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate
from django.core.files.storage import FileSystemStorage
import json
import pandas as pd
import xlsxwriter
from .models import Import, Package, ImportDetail, PACKAGE_TYPE_CHOICES
from .forms import ImportForm, PackageForm
from .models import Item



@login_required
def register_import(request):
    import_number = None  # ✅ Define import_number at the start

    if request.method == 'POST':
        import_form = ImportForm(request.POST)

        if import_form.is_valid():
            new_import = import_form.save()

            # ✅ Assign import_number after successful form submission
            import_number = new_import.unique_number  

            try:
                # ✅ Save package data
                package_data_json = request.POST.get('packages', '[]')
                package_data = json.loads(package_data_json) if package_data_json else []

                for package in package_data:
                    Package.objects.create(
                        import_instance=new_import,
                        package_type=package.get('packageType', ''),
                        length=float(package.get('length', 0)),
                        width=float(package.get('width', 0)),
                        height=float(package.get('height', 0)),
                        gross_weight=float(package.get('grossWeight', 0))
                    )

                # ✅ Save Excel data
                excel_data_json = request.POST.get('excel_data', '[]')
                excel_data = json.loads(excel_data_json) if excel_data_json else []

                for record in excel_data:
                    ImportDetail.objects.create(
                        import_instance=new_import,
                        po_number=record.get('poNumber', ''),
                        line_number=int(record.get('lineNumber', 0)),
                        item_number=record.get('itemNumber', ''),
                        description_eng=record.get('descriptionEng', ''),
                        quantity=int(record.get('quantity', 0)),
                        unit_cost=float(record.get('unitCost', 0)),
                        line_cost=float(record.get('unitCost', 0)) * int(record.get('quantity', 0)),
                    )

                messages.success(request, "✅ Import registered successfully!")
                return redirect('import_list')

            except Exception as e:
                print(f"🚨 Error saving import details: {e}")  # ✅ Debugging log
                messages.error(request, "🚨 Import registration failed due to an internal error!")

        else:
            print("🚨 Form Errors:", import_form.errors)  # ✅ Debugging log
            messages.error(request, "🚨 Form submission failed! Please check required fields.")

    else:
        import_form = ImportForm()

        # ✅ Generate new Import Number Safely
        last_import = Import.objects.all().order_by('id').last()
        if last_import:
            new_number = int(last_import.unique_number.replace("IMP", "")) + 1
        else:
            new_number = 1

        import_number = f"IMP{str(new_number).zfill(5)}"

    return render(request, 'imports/register_import.html', {
        'import_form': import_form,
        'import_number': import_number,  # ✅ import_number is always assigned
        'package_type_choices': PACKAGE_TYPE_CHOICES
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
    import_details = ImportDetail.objects.filter(import_instance=import_instance)

    if request.method == "POST":
        form = ImportForm(request.POST, instance=import_instance)
        if form.is_valid():
            updated_import = form.save()

            # ✅ Delete old ImportDetail records
            ImportDetail.objects.filter(import_instance=updated_import).delete()

            # ✅ Save new Excel data
            excel_data_json = request.POST.get("excel_data", "[]")
            excel_data = json.loads(excel_data_json) if excel_data_json else []

            for record in excel_data:
                ImportDetail.objects.create(
                    import_instance=updated_import,
                    po_number=record.get("poNumber", ""),
                    line_number=int(record.get("lineNumber", 0)),
                    item_number=record.get("itemNumber", ""),
                    description_eng=record.get("descriptionEng", ""),
                    quantity=int(record.get("quantity", 0)),
                    unit_cost=float(record.get("unitCost", 0)),
                    line_cost=float(record['unitCost']) * int(record['quantity']), 
                )

            return redirect('import_list')

    else:
        form = ImportForm(instance=import_instance)

    return render(request, "imports/edit_import.html", {
        "form": form,
        "import": import_instance,
        "import_details": list(import_details.values()),  # ✅ Send existing Excel data
    })







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







@login_required
def export_import_excel(request, unique_number):
    try:
        # Fetch import instance
        import_instance = Import.objects.get(unique_number=unique_number)
        details = ImportDetail.objects.filter(import_instance=import_instance)
        packages = Package.objects.filter(import_instance=import_instance)

        # Create an HTTP response with an Excel content type
        output = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        output['Content-Disposition'] = f'attachment; filename="{import_instance.unique_number}_export.xlsx"'

        # Create a Pandas Excel writer
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            workbook = writer.book

            # ✅ Prepare Import Details Data
            data = []
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

            if not details.exists():
                data.append(base_info + ["", "", "", "", "", "", ""])  # Fill empty fields
            else:
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

            columns = [
                "Import Number", "Vendor Name", "Status", "Country", "Incoterms", "Operation",
                "Pickup Address", "Date Created", "Last Updated",
                "PO Number", "Line Number", "Item Number", "Description", "Quantity", "Unit Cost", "Line Cost"
            ]

            # ✅ Create Import Details Sheet
            df_import = pd.DataFrame(data, columns=columns)
            df_import.to_excel(writer, sheet_name="Import Data", index=False)

            # ✅ Format Import Data Sheet
            worksheet_import = writer.sheets["Import Data"]
            for col_num, col_name in enumerate(columns):
                worksheet_import.set_column(col_num, col_num, max(len(col_name) + 2, 15))

            # ✅ Prepare Package Data
            package_data = []

            for package in packages:
                package_data.append([
                    import_instance.unique_number,
                    package.package_type,
                    package.length,
                    package.width,
                    package.height,
                    package.gross_weight
                ])

            package_columns = [
                "Import Number", "Package Type", "Length (cm)", "Width (cm)", "Height (cm)", "Gross Weight (kg)"
            ]

            # ✅ Create Package Information Sheet
            if package_data:
                df_package = pd.DataFrame(package_data, columns=package_columns)
            else:
                df_package = pd.DataFrame(columns=package_columns)  # Empty sheet if no packages

            df_package.to_excel(writer, sheet_name="Package Information", index=False)

            # ✅ Format Package Information Sheet
            worksheet_package = writer.sheets["Package Information"]
            for col_num, col_name in enumerate(package_columns):
                worksheet_package.set_column(col_num, col_num, max(len(col_name) + 2, 15))

        return output

    except Import.DoesNotExist:
        return HttpResponse("Import not found", status=404)






@login_required
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





import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from .models import Item
from django.contrib.auth.decorators import login_required

@login_required
def upload_items(request):
    if request.method == "POST" and request.FILES.get("item_file"):
        item_file = request.FILES["item_file"]

        try:
            df = pd.read_excel(item_file)

            required_columns = ["Item Number", "Description Eng", "Description Geo", "HS Code", "Net Weight"]
            if not all(col in df.columns for col in required_columns):
                return JsonResponse({"error": "Invalid file format. Please upload an Excel file with the correct columns."}, status=400)

            existing_items = {item.item_number: item for item in Item.objects.all()}  
            new_items = []
            updated_items = []

            for _, row in df.iterrows():
                item_number = str(row["Item Number"]).strip()
                description_eng = str(row["Description Eng"]).strip()
                description_geo = str(row.get("Description Geo", "")).strip()
                hs_code = str(row.get("HS Code", "")).strip()
                net_weight = float(row["Net Weight"])

                if item_number in existing_items:
                    existing_item = existing_items[item_number]
                    if existing_item.description_eng != description_eng or existing_item.net_weight != net_weight:
                        updated_items.append({
                            "item_number": item_number,
                            "old_data": {
                                "description_eng": existing_item.description_eng,
                                "net_weight": existing_item.net_weight
                            },
                            "new_data": {
                                "description_eng": description_eng,
                                "net_weight": net_weight
                            }
                        })
                else:
                    new_items.append(Item(
                        item_number=item_number,
                        description_eng=description_eng,
                        description_geo=description_geo,
                        hs_code=hs_code,
                        net_weight=net_weight
                    ))

            Item.objects.bulk_create(new_items)

            return JsonResponse({
                "success": f"{len(new_items)} new items added!",
                "updates": updated_items
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return render(request, "imports/upload_items.html")


@login_required
def export_items_excel(request):
    # Fetch all items
    items = Item.objects.all()

    # Create HTTP Response for Excel file
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="Items_List.xlsx"'

    # Write DataFrame to Excel
    with pd.ExcelWriter(response, engine="xlsxwriter") as writer:
        df = pd.DataFrame(list(items.values()), columns=["item_number", "description_eng", "description_geo", "hs_code", "net_weight"])
        df.columns = ["Item Number", "Description Eng", "Description Geo", "HS Code", "Net Weight"]
        df.to_excel(writer, sheet_name="Items", index=False)

    return response
