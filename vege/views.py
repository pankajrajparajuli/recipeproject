from django.shortcuts import render, redirect, get_object_or_404
from .models import Recipe
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


# View to list recipes and add new ones
# Only accessible by logged-in users
@login_required(login_url='login')
def recipes(request):
    if request.method == "POST":
        # Get form data from POST request
        name = request.POST.get("recipe_name")
        description = request.POST.get("recipe_description")
        image = request.FILES.get("recipe_image")

        # Create new recipe linked to logged-in user
        Recipe.objects.create(
            recipe_name=name,
            recipe_description=description,
            recipe_image=image,
            user=request.user  # Assign current user as owner
        )
        # Redirect to refresh the recipe list page
        return redirect('/recipes/')

    # Handle search queries - filter recipes by current user only
    query = request.GET.get('search')
    if query:
        # Filter user's recipes containing the search term (case-insensitive)
        recipes = Recipe.objects.filter(user=request.user, recipe_name__icontains=query)
    else:
        # If no search, show all recipes owned by current user
        recipes = Recipe.objects.filter(user=request.user)

    # Render the recipes page and pass filtered recipes
    return render(request, 'recipes.html', {'recipes': recipes})


# View to delete a recipe
# Ensures only the owner can delete their recipe
@login_required(login_url='login')
def delete_recipe(request, id):
    if request.method == "POST":
        # Safely get the recipe owned by the user or return 404
        recipe = get_object_or_404(Recipe, id=id, user=request.user)
        recipe.delete()
    return redirect('/recipes/')


# View to update/edit a recipe
# Only allows owners to edit their recipes
@login_required(login_url='login')
def update_recipe(request, id):
    # Retrieve the recipe owned by the logged-in user or 404 if not found
    recipe = get_object_or_404(Recipe, id=id, user=request.user)

    if request.method == "POST":
        data = request.POST
        # Update fields from the form
        recipe.recipe_name = data.get("recipe_name")
        recipe.recipe_description = data.get("recipe_description")
        # Update image if a new one is uploaded; else keep existing
        recipe.recipe_image = request.FILES.get("recipe_image", recipe.recipe_image)
        recipe.save()
        # Redirect back to recipe list after update
        return redirect('/recipes/')

    # Render the update form pre-filled with the recipe data
    return render(request, "update_recipe.html", {"recipe": recipe})


# User registration view
def register_user(request):
    if request.method == 'POST':
        # Grab registration form data
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # Check password confirmation
        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect('register')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        # Create the new user
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        messages.success(request, "Account created! You can now log in.")
        return redirect('login')

    # Render registration page for GET requests
    return render(request, 'register.html')


# User login view
def login_user(request):
    if request.method == 'POST':
        # Get login credentials from form
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Login and redirect to recipes page on success
            login(request, user)
            return redirect('/recipes/')
        else:
            # Show error if credentials are invalid
            messages.error(request, "Invalid username or password")

    # Render login page for GET requests or failed POST
    return render(request, 'login.html')


# User logout view
def logout_user(request):
    # Log out the user and clear session
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')
