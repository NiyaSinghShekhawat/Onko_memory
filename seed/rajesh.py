"""
Demo patient: Rajesh Kumar, 58, colon cancer on CAPOX. Owner: Shreyan.

Days are offsets from the day you run the loader (0 = today), so the demo
always looks "current". Cycle 3 started on day -24, Cycle 4 on day -3.

Built-in patterns for Hindsight to discover (nobody states them outright):
  • Nausea on days 2–3 after each oxaliplatin infusion
  • Evening Capecitabine missed/late on travel or tired days
  • Tingling fingers when touching cold things (recurring diary mentions)
  • Daughter Priya handles reports and appointments
Enrich freely — more realistic detail = better demo.
"""

from core.contracts import CarePlanItem, EntryType, ItemKind, Role

PATIENT = {"name": "Rajesh Kumar", "age": 58, "diagnosis": "Colon cancer (stage III), adjuvant CAPOX"}


def plan_items(d) -> list[CarePlanItem]:
    """Current (Cycle 4) plan. `d(offset)` → ISO date string."""
    return [
        CarePlanItem(ItemKind.MEDICATION, "Capecitabine", "1500 mg", ["morning", "evening"], d(-3), d(10), "after food, days 1–14"),
        CarePlanItem(ItemKind.MEDICATION, "Ondansetron", "8 mg", [], d(-3), d(10), "only if nausea, before meals"),
        CarePlanItem(ItemKind.INSTRUCTION, "Drink 2 litres of water", "", ["daily"], d(-3), "", ""),
        CarePlanItem(ItemKind.TEST, "CBC + LFT blood test", "", [], d(4), "", "at hospital lab, 9 AM"),
        CarePlanItem(ItemKind.APPOINTMENT, "Review with Dr. Mehta", "", [], d(11), "", "bring CBC report"),
        CarePlanItem(ItemKind.TREATMENT, "CAPOX Cycle 5 — Oxaliplatin infusion", "", [], d(18), "", "day-care, 10 AM"),
    ]


# (day_offset, hour, source, type, content)
ENTRIES = [
    # ── Cycle 3 ──
    (-24, 10, Role.DOCTOR, EntryType.CARE_PLAN, "Cycle 3 of CAPOX started. Oxaliplatin infusion given today at day-care. Capecitabine 1500 mg twice daily after food, days 1–14. Ondansetron 8 mg before meals if nausea."),
    (-24, 16, Role.NURSE, EntryType.DOCTOR_NOTE, "Infusion completed without issues. Daughter Priya accompanied the patient and will handle report uploads and appointment bookings."),
    (-23, 20, Role.PATIENT, EntryType.CHECKLIST, "Daily check-in:\n- Capecitabine 1500 mg — morning: done\n- Capecitabine 1500 mg — evening: done"),
    (-22, 21, Role.PATIENT, EntryType.SYMPTOM, "Mood: 😟 Not good. Symptoms: Nausea, No appetite. Nausea started after lunch, took Ondansetron."),
    (-21, 21, Role.PATIENT, EntryType.SYMPTOM, "Mood: 😐 Okay. Symptoms: Nausea, Tiredness. Still queasy in the morning, better by evening."),
    (-21, 21, Role.PATIENT, EntryType.DIARY, "Fingers tingle when I take water bottles out of the fridge."),
    (-19, 20, Role.PATIENT, EntryType.CHECKLIST, "Daily check-in:\n- Capecitabine 1500 mg — morning: done\n- Capecitabine 1500 mg — evening: late"),
    (-19, 20, Role.PATIENT, EntryType.DIARY, "Took the evening tablet late because I was travelling to my brother's house in Warangal."),
    (-18, 21, Role.PATIENT, EntryType.SYMPTOM, "Mood: 😊 Good. Symptoms: none."),
    (-16, 21, Role.PATIENT, EntryType.CHECKLIST, "Daily check-in:\n- Capecitabine 1500 mg — morning: done\n- Capecitabine 1500 mg — evening: missed"),
    (-16, 21, Role.PATIENT, EntryType.DIARY, "Felt very tired and slept early, forgot the evening tablet."),
    (-14, 11, Role.PATIENT, EntryType.CHAT, "patient said: Can I eat mangoes while on this medicine?"),
    (-12, 21, Role.PATIENT, EntryType.DIARY, "Cold water feels like needles in my throat. Drinking warm water instead."),
    (-10, 13, Role.PATIENT, EntryType.REPORT, "CBC (uploaded by daughter Priya): Hb 10.1 g/dL, WBC 4.8 x10^9/L, Platelets 182 x10^9/L, ANC 2.6 x10^9/L."),
    (-8, 21, Role.PATIENT, EntryType.SYMPTOM, "Mood: 😊 Good. Symptoms: Sleep trouble. Hard to sleep because of worry about the next cycle."),
    (-6, 21, Role.PATIENT, EntryType.DIARY, "Walked 20 minutes in the colony park. Appetite is back to normal."),
    # ── Cycle 4 ──
    (-3, 10, Role.DOCTOR, EntryType.CARE_PLAN, "Cycle 4 of CAPOX started. Oxaliplatin infusion given. Same Capecitabine dose 1500 mg twice daily after food, days 1–14. CBC + LFT in one week. Review in two weeks."),
    (-3, 12, Role.DOCTOR, EntryType.DOCTOR_NOTE, "Patient reports tingling in fingers with cold. Advised to avoid cold drinks and cold objects. Patient prefers short, simple explanations; family speaks Telugu at home."),
    (-3, 13, Role.DOCTOR, EntryType.REPORT, "CBC pre-cycle 4: Hb 9.2 g/dL, WBC 4.1 x10^9/L, Platelets 156 x10^9/L, ANC 2.1 x10^9/L."),
    (-3, 18, Role.PATIENT, EntryType.VISIT_NOTE, "Patient's note after appointment: Doctor said eat smaller meals, avoid cold things, and come back if fever goes above 100."),
    (-2, 21, Role.PATIENT, EntryType.SYMPTOM, "Mood: 😟 Not good. Symptoms: Nausea, Tiredness. Nausea again after breakfast, same as last time."),
    (-1, 21, Role.PATIENT, EntryType.SYMPTOM, "Mood: 😐 Okay. Symptoms: Nausea, No appetite. Took Ondansetron twice."),
    (-1, 21, Role.PATIENT, EntryType.CHECKLIST, "Daily check-in:\n- Capecitabine 1500 mg — morning: done\n- Capecitabine 1500 mg — evening: late\n- Drink 2 litres of water — daily: missed"),
]
