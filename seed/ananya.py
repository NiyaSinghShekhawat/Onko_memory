"""
Second demo patient: Ananya Rao, 46, breast cancer on adjuvant chemotherapy.

Days are offsets from the day the loader runs (0 = today), keeping the demo
current while giving Hindsight a distinct longitudinal history from Rajesh.

Built-in patterns for the demo:
  - Tiredness and reduced appetite recur for a few days after treatment
  - Morning medicines are usually on time; one evening routine was late on travel
  - Sleep trouble appears before review appointments
  - Sister Kavya helps keep reports and appointment dates organised

These are recorded events only. The app should recall them, not infer diagnosis,
causality, progression, or treatment recommendations from them.
"""

from core.contracts import CarePlanItem, EntryType, ItemKind, Role

PATIENT = {
    "name": "Ananya Rao",
    "age": 46,
    "diagnosis": "Breast cancer, adjuvant chemotherapy",
}


def plan_items(d) -> list[CarePlanItem]:
    return [
        CarePlanItem(ItemKind.MEDICATION, "Ondansetron", "8 mg", ["morning"], d(-2), d(3), "as prescribed after treatment"),
        CarePlanItem(ItemKind.INSTRUCTION, "Drink 2 litres of water", "", ["daily"], d(-2), "", ""),
        CarePlanItem(ItemKind.INSTRUCTION, "Short daily walk", "", ["evening"], d(-2), "", "if comfortable"),
        CarePlanItem(ItemKind.TEST, "CBC blood test", "", [], d(5), "", "hospital lab, morning"),
        CarePlanItem(ItemKind.APPOINTMENT, "Review with Dr. Iyer", "", [], d(8), "", "bring latest CBC report"),
        CarePlanItem(ItemKind.TREATMENT, "Next scheduled chemotherapy session", "", [], d(15), "", "day-care unit"),
    ]


ENTRIES = [
    (-27, 10, Role.DOCTOR, EntryType.CARE_PLAN, "Adjuvant chemotherapy session completed today. Ondansetron 8 mg as prescribed after treatment. Maintain hydration and keep the next CBC and review dates."),
    (-27, 15, Role.NURSE, EntryType.DOCTOR_NOTE, "Session completed. Sister Kavya accompanied Ananya and helps organise reports and appointment dates."),
    (-26, 20, Role.PATIENT, EntryType.CHECKLIST, "Daily check-in:\n- Ondansetron 8 mg — morning: done\n- Drink 2 litres of water — daily: done"),
    (-25, 21, Role.PATIENT, EntryType.SYMPTOM, "Mood: 😐 Okay. Symptoms: Tiredness, No appetite. Ate smaller meals today."),
    (-24, 21, Role.PATIENT, EntryType.SYMPTOM, "Mood: 😟 Not good. Symptoms: Tiredness. Rested for most of the afternoon."),
    (-22, 20, Role.PATIENT, EntryType.DIARY, "Energy felt better today. Took a short walk near home in the evening."),
    (-20, 21, Role.PATIENT, EntryType.CHECKLIST, "Daily check-in:\n- Drink 2 litres of water — daily: done\n- Short daily walk — evening: done"),
    (-18, 11, Role.PATIENT, EntryType.REPORT, "CBC uploaded by sister Kavya: Hb 10.8 g/dL, WBC 5.2 x10^9/L, Platelets 214 x10^9/L."),
    (-16, 20, Role.PATIENT, EntryType.DIARY, "Had trouble sleeping because I was thinking about the upcoming review appointment."),
    (-14, 14, Role.PATIENT, EntryType.CHAT, "patient said: When is my next blood test and review appointment?"),
    (-12, 11, Role.DOCTOR, EntryType.DOCTOR_NOTE, "Reviewed uploaded CBC and recent check-ins. Upcoming dates were confirmed with the patient."),
    (-10, 20, Role.PATIENT, EntryType.SYMPTOM, "Mood: 😊 Good. Symptoms: none. Appetite felt normal today."),
    (-7, 21, Role.PATIENT, EntryType.DIARY, "Went to my cousin's house today. I want the app to remember that travel days can make my routine harder to follow."),
    (-6, 22, Role.PATIENT, EntryType.CHECKLIST, "Daily check-in:\n- Evening routine: late\n- Drink 2 litres of water — daily: done"),
    (-6, 22, Role.PATIENT, EntryType.DIARY, "Finished the evening routine late because we returned home late from my cousin's house."),
    (-2, 10, Role.DOCTOR, EntryType.CARE_PLAN, "Current cycle follow-up plan confirmed. CBC in one week, review after the report, and next scheduled chemotherapy session after the review."),
    (-2, 13, Role.DOCTOR, EntryType.REPORT, "Pre-follow-up CBC: Hb 10.5 g/dL, WBC 4.9 x10^9/L, Platelets 205 x10^9/L."),
    (-2, 18, Role.PATIENT, EntryType.VISIT_NOTE, "Patient's note after appointment: Doctor said keep the blood-test appointment and bring the report to the review."),
    (-1, 20, Role.PATIENT, EntryType.SYMPTOM, "Mood: 😐 Okay. Symptoms: Tiredness, No appetite. Had soup and a small dinner."),
    (-1, 21, Role.PATIENT, EntryType.CHECKLIST, "Daily check-in:\n- Ondansetron 8 mg — morning: done\n- Drink 2 litres of water — daily: done\n- Short daily walk — evening: missed"),
]
