"""
Official Irish immigration sources.

Saved as local HTML files in data/raw_html/
fetched manually from official government websites.
Every answer the system gives is grounded in these sources.
"""
from pathlib import Path

RAW_HTML_DIR = Path("data/raw_html")

IMMIGRATION_SOURCES = [
    # ── Citizens Information ──────────────────────────────
    {
        "filename": "visa_requirements.html",
        "url": "https://www.citizensinformation.ie/en/moving-country/visas-for-ireland/visa-requirements-for-entering-ireland/",
        "title": "Visa requirements for entering Ireland",
        "category": "visas",
    },
    {
        "filename": "employment_permits.html",
        "url": "https://www.citizensinformation.ie/en/moving-country/working-in-ireland/employment-permits/work-permits/",
        "title": "Employment permits overview",
        "category": "employment_permits",
    },
    {
        "filename": "critical_skills_permit.html",
        "url": "https://www.citizensinformation.ie/en/moving-country/working-in-ireland/employment-permits/critical-skills-employment-permit/",
        "title": "Critical Skills Employment Permit",
        "category": "employment_permits",
    },
    {
        "filename": "general_employment_permit.html",
        "url": "https://www.citizensinformation.ie/en/moving-country/working-in-ireland/employment-permits/general-employment-permit/",
        "title": "General Employment Permit",
        "category": "employment_permits",
    },
    {
        "filename": "student_visa.html",
        "url": "https://www.citizensinformation.ie/en/moving-country/moving-to-ireland/studying-in-ireland/student-visa-ireland/",
        "title": "Student visa Ireland",
        "category": "student",
    },
    {
        "filename": "Immigration_rules_for_full_time_non_EEA_students.html",
        "url": "https://www.citizensinformation.ie/en/moving-country/moving-to-ireland/studying-in-ireland/immigration-nonEEA-students/",
        "title": "Immigration rules for full-time non-EEA students",
        "category": "student",
    },
    {
        "filename": "Moving_to_Ireland_for_third_level_education.html",
        "url": "https://www.citizensinformation.ie/en/moving-country/moving-to-ireland/studying-in-ireland/third-level-education/",
        "title": "Moving to Ireland for third-level education",
        "category": "student",
    },
    {
        "filename": "citizenship_birth_descent.html",
        "url": "https://www.citizensinformation.ie/en/moving-country/irish-citizenship/irish-citizenship-through-birth-or-descent/",
        "title": "Irish citizenship through birth or descent",
        "category": "citizenship",
    },
    {
        "filename": "naturalisation.html",
        "url": "https://www.citizensinformation.ie/en/moving-country/irish-citizenship/becoming-an-irish-citizen-through-naturalisation/",
        "title": "Becoming an Irish citizen through naturalisation",
        "category": "citizenship",
    },
    {
        "filename": "residence_permission.html",
        "url": "https://www.citizensinformation.ie/en/moving-country/moving-to-ireland/rights-of-residence-in-ireland/types-residence-permission-non-eea-nationals/",
        "title": "Types of residence permission for non-EEA nationals",
        "category": "residence",
    },
    {
        "filename": "Residence_rights_of_EU_citizens_and_their_families_in_Ireland.html",
        "url": "https://www.citizensinformation.ie/en/moving-country/moving-to-ireland/rights-of-residence-in-ireland/residence-rights-eu-national/",
        "title": "Residence rights of EU citizens and their families in Ireland",
        "category": "residence",
    },
    {
        "filename": "family_reunion.html",
        "url": "https://www.citizensinformation.ie/en/moving-country/moving-to-ireland/coming-to-live-in-ireland/bringing-your-family/",
        "title": "Bringing your family to Ireland",
        "category": "family",
    },

    # ── Irish Immigration Service ─────────────────────────
    {
        "filename": "inis_work_options.html",
        "url": "https://www.irishimmigration.ie/coming-to-work-in-ireland/what-are-my-options-for-working-in-ireland/coming-to-work-for-more-than-90-days/",
        "title": "Coming to work for more than 90 days",
        "category": "employment_permits",
    },
    {
        "filename": "inis_study.html",
        "url": "https://www.irishimmigration.ie/coming-to-study-in-ireland/",
        "title": "Coming to study in Ireland",
        "category": "student",
    },
    {
        "filename": "inis_registration.html",
        "url": "https://www.irishimmigration.ie/registering-your-immigration-permission/",
        "title": "Registering your immigration permission",
        "category": "registration",
    },
    {
        "filename": "inis_situation_changed.html",
        "url": "https://www.irishimmigration.ie/my-situation-has-changed-since-i-arrived-in-ireland/",
        "title": "My situation has changed since I arrived in Ireland",
        "category": "changes",
    },
]

CATEGORIES = [
    "visas",
    "employment_permits",
    "student",
    "citizenship",
    "residence",
    "family",
    "registration",
    "changes",
]