#imports/mview
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Import
from .forms import ImportForm

@login_required
def register_import(request):
    if request.method == 'POST':
        form = ImportForm(request.POST)
        if form.is_valid():
            form.save()  # Save the form data to the database
            return redirect('import_list')  # Redirect to the import list page
    else:
        form = ImportForm()

    return render(request, 'imports/register_import.html', {'form': form})

@login_required
def import_list(request):
    imports = Import.objects.all().order_by('-date_created')  # Order by most recent
    return render(request, 'imports/import_list.html', {'imports': imports})

@login_required
def import_detail(request, unique_number):
    import_instance = get_object_or_404(Import, unique_number=unique_number)
    return render(request, 'imports/import_detail.html', {'import': import_instance})
