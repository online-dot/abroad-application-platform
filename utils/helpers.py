def generate_registration_number(application_id):
    year = datetime.now().year
    return f"CVE-{year}-{str(application_id).zfill(7)}"
