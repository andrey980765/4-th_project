# contacts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .forms import ContactForm
from .models import Contact
from .utils_storage import read_json_contacts, write_json_contacts, read_xml_contacts, write_xml_contacts
from django.core import serializers
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models import Q

@ensure_csrf_cookie
def contact_create(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            save_to = form.cleaned_data.pop('save_to')
            cdata = {
                'name': form.cleaned_data['name'],
                'email': form.cleaned_data['email'],
                'phone': form.cleaned_data.get('phone', ''),
                'notes': form.cleaned_data.get('notes', '')
            }
            if save_to == 'db':
                # проверка дубликата: по name+email
                exists = Contact.objects.filter(name__iexact=cdata['name'], email__iexact=cdata['email']).exists()
                if exists:
                    messages.warning(request, 'Такая запись уже есть в базе — дубликат не добавлен.')
                else:
                    Contact.objects.create(**cdata)
                    messages.success(request, 'Запись добавлена в базу данных.')
            elif save_to == 'json':
                arr = read_json_contacts()
                arr.append(cdata)
                write_json_contacts(arr)
                messages.success(request, 'Запись сохранена в JSON файл.')
            elif save_to == 'xml':
                arr = read_xml_contacts()
                arr.append(cdata)
                write_xml_contacts(arr)
                messages.success(request, 'Запись сохранена в XML файл.')
            return redirect('contacts:list')
    else:
        form = ContactForm()
    return render(request, 'contacts/contact_form.html', {'form': form})

def contact_list(request):
    # выбор источника: ?source=db/json/xml
    source = request.GET.get('source', 'db')
    if source == 'db':
        contacts = Contact.objects.order_by('-created_at').all()
        from_db = True
    elif source == 'json':
        contacts = read_json_contacts()
        from_db = False
    elif source == 'xml':
        contacts = read_xml_contacts()
        from_db = False
    else:
        contacts = []
        from_db = False
    return render(request, 'contacts/contact_list.html', {'contacts': contacts, 'from_db': from_db, 'source': source})

# AJAX search for DB
def ajax_search_contacts(request):
    q = request.GET.get('q','').strip()
    if q == '':
        qs = Contact.objects.order_by('-created_at').all()[:50]
    else:
        qs = Contact.objects.filter(
            Q(name__icontains=q) | Q(email__icontains=q) | Q(phone__icontains=q) | Q(notes__icontains=q)
        ).order_by('-created_at')[:200]
    data = []
    for c in qs:
        data.append({
            'id': c.id,
            'name': c.name,
            'email': c.email,
            'phone': c.phone,
            'notes': c.notes,
        })
    return JsonResponse({'results': data})

# AJAX delete
@require_POST
def ajax_delete_contact(request, pk):
    c = get_object_or_404(Contact, pk=pk)
    c.delete()
    return JsonResponse({'ok': True})

# AJAX update (PUT via fetch)
@require_POST
def ajax_update_contact(request, pk):
    c = get_object_or_404(Contact, pk=pk)
    name = request.POST.get('name','').strip()
    email = request.POST.get('email','').strip()
    phone = request.POST.get('phone','').strip()
    notes = request.POST.get('notes','').strip()

    # простая валидация
    errors = {}
    if not name:
        errors['name'] = 'Имя не может быть пустым.'
    if not email:
        errors['email'] = 'Email не может быть пустым.'
    if errors:
        return JsonResponse({'ok': False, 'errors': errors}, status=400)

    # проверка на дубликат (если меняем имя/email на уже существующие другого pk)
    dup = Contact.objects.filter(name__iexact=name, email__iexact=email).exclude(pk=c.pk).exists()
    if dup:
        return JsonResponse({'ok': False, 'errors': {'__all__': 'Другая запись с таким именем и email уже существует.'}}, status=400)

    c.name = name
    c.email = email
    c.phone = phone
    c.notes = notes
    c.save()
    return JsonResponse({'ok': True, 'contact': {'id': c.pk, 'name': c.name, 'email': c.email, 'phone': c.phone, 'notes': c.notes}})
