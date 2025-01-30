#imports/mview
from django.shortcuts import render, redirect, get_object_or_404
import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Import, Package
from .forms import ImportForm

import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Import, Package
from .forms import ImportForm

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Import, Package
from .forms import ImportForm

@login_required
def register_import(request):
    if request.method == 'POST':
        import_form = ImportForm(request.POST)

        if import_form.is_valid():
            new_import = import_form.save()  # ✅ Save Import First

            # ✅ Extract package data from hidden field
            package_data_json = request.POST.get('packages', '[]')  # Default to empty list if missing
            print(f"🔍 Received JSON: {package_data_json}")  # Debugging

            try:
                package_data = json.loads(package_data_json)  # Convert JSON string to Python dictionary

                if package_data:  # ✅ Check if packages exist
                    for package in package_data:
                        Package.objects.create(
                            import_instance=new_import,
                            package_type=package['packageType'],
                            length=float(package['length']),
                            width=float(package['width']),
                            height=float(package['height']),
                            gross_weight=float(package['grossWeight'])
                        )
                    print(f"✅ {len(package_data)} Packages saved!")  # Debugging
                else:
                    print("⚠️ No packages received!")  # Debugging
            except json.JSONDecodeError as e:
                print(f"🚨 JSON Error: {e}")  # Debugging

            return redirect('import_list')

    else:
        import_form = ImportForm()

    return render(request, 'imports/register_import.html', {
        'import_form': import_form,
        'PACKAGE_TYPE_CHOICES': Import.PACKAGE_TYPE  # ✅ Pass package type choices to the template
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

