from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import RegisterForm, VaultEntryForm
from .models import VaultEntry
from .utils import decrypt_password, encrypt_password


def home(request):
    if request.user.is_authenticated:
        return redirect("vault_list")
    return render(request, "vault/home.html")


def register(request):
    if request.user.is_authenticated:
        return redirect("vault_list")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()          # Django hashes the master password
            login(request, user)        # log the new user straight in
            return redirect("vault_list")
    else:
        form = RegisterForm()

    return render(request, "vault/register.html", {"form": form})


@login_required
def vault_list(request):
    entries = VaultEntry.objects.filter(user=request.user)
    return render(request, "vault/list.html", {"entries": entries})


@login_required
def vault_create(request):
    if request.method == "POST":
        form = VaultEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.encrypted_password = encrypt_password(form.cleaned_data["password"])
            entry.save()
            messages.success(request, f"Saved credentials for {entry.website}.")
            return redirect("vault_list")
    else:
        form = VaultEntryForm()

    return render(request, "vault/form.html", {"form": form, "title": "ADD NEW ENTRY"})


@login_required
def vault_detail(request, pk):
    entry = get_object_or_404(VaultEntry, pk=pk, user=request.user)
    plain = decrypt_password(entry.encrypted_password)
    return render(request, "vault/detail.html", {"entry": entry, "password": plain})


@login_required
def vault_update(request, pk):
    entry = get_object_or_404(VaultEntry, pk=pk, user=request.user)

    if request.method == "POST":
        form = VaultEntryForm(request.POST)
        if form.is_valid():
            entry.website = form.cleaned_data["website"]
            entry.username = form.cleaned_data["username"]
            entry.notes = form.cleaned_data["notes"]
            entry.encrypted_password = encrypt_password(form.cleaned_data["password"])
            entry.save()
            messages.success(request, f"Updated {entry.website}.")
            return redirect("vault_list")
    else:
        form = VaultEntryForm(
            initial={
                "website": entry.website,
                "username": entry.username,
                "notes": entry.notes,
                "password": decrypt_password(entry.encrypted_password),
            }
        )

    return render(request, "vault/form.html", {"form": form, "title": "EDIT ENTRY"})


@login_required
def vault_delete(request, pk):
    entry = get_object_or_404(VaultEntry, pk=pk, user=request.user)

    if request.method == "POST":
        name = entry.website
        entry.delete()
        messages.success(request, f"Deleted {name}.")
        return redirect("vault_list")

    return render(request, "vault/confirm_delete.html", {"entry": entry})