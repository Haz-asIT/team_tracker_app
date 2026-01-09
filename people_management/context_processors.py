def inject_person(request):
    user = request.user
    current_person = getattr(user, "person", None) if user.is_authenticated else None
    return {"current_person": current_person}
