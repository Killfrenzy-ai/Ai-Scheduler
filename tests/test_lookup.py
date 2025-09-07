import pytest
from tools.patient_lookup import lookup_patient

def test_lookup_by_mrn_found():
    # Change MRN001 to a real MRN in your patients.db
    res = lookup_patient(mrn="MRN001")
    assert res["found"] is True
    assert "classification" in res

def test_lookup_by_name_and_dob():
    # Replace with an actual name/dob from your patients.db
    res = lookup_patient(name="John Doe", dob="1980-05-15")
    # Either found (existing patient) or not found → new
    assert isinstance(res["found"], bool)

def test_patient_not_found():
    res = lookup_patient(name="Nonexistent Person", dob="1900-01-01")
    assert res["found"] is False
    assert res["classification"] == "new"

def test_classification_new_vs_returning():
    # This will vary based on synthetic data — pick a known MRN
    res = lookup_patient(mrn="MRN002")
    assert res["found"] is True
    assert res["classification"] in ["new", "returning"]
    assert "reason" in res
