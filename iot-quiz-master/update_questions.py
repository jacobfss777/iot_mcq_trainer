import json
import copy

with open('questions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

topics = {t['topicId']: t for t in data}

def get_q(topic_id, q_id):
    for q in topics[topic_id]['questions']:
        if q['id'] == q_id:
            return copy.deepcopy(q)
    return None

def remove_q(topic_id, q_id):
    topics[topic_id]['questions'] = [q for q in topics[topic_id]['questions'] if q['id'] != q_id]

def add_q(topic_id, question):
    topics[topic_id]['questions'].append(question)

# ============================================================
# TOPIC 1: Remove t1q8 (2.4GHz) and t1q10 (bit rate)
#           Add 2 matching questions
#           Renumber t1q9 (Middleware) → t1q10
# ============================================================
saved_t1q8 = get_q(1, 't1q8')
saved_t1q10 = get_q(1, 't1q10')
remove_q(1, 't1q8')
remove_q(1, 't1q10')

matching_q1 = {
    "id": "t1q8",
    "type": "matching",
    "question": "Arrange the various layers for the IoT Reference Model, assuming the following sequence:\n7. Collaboration & Processes\n6. Application\n...",
    "items": ["Data Abstraction", "Data Accumulation", "Physical Devices & Controller", "Connectivity", "Edge Computing"],
    "options": ["1", "2", "3", "4", "5"],
    "correctAnswer": {
        "Data Abstraction": "5",
        "Data Accumulation": "4",
        "Physical Devices & Controller": "1",
        "Connectivity": "2",
        "Edge Computing": "3"
    },
    "explanation": "The IoT Reference Model layers from bottom to top: 1-Physical Devices & Controller, 2-Connectivity, 3-Edge Computing, 4-Data Accumulation, 5-Data Abstraction, 6-Application, 7-Collaboration & Processes."
}

matching_q2 = {
    "id": "t1q9",
    "type": "matching",
    "question": "Match the following terms to the most appropriate description.",
    "items": ["Cyber-Physical Systems", "Embedded Systems", "Real-time Systems", "Pervasive/Ubiquitous Computing"],
    "options": ["1", "2", "3", "4"],
    "descriptions": [
        "1. focus on anytime/anywhere computing",
        "2. focus on time constraints",
        "3. not necessarily connected",
        "4. focus on interaction between physical and cyber systems"
    ],
    "correctAnswer": {
        "Cyber-Physical Systems": "4",
        "Embedded Systems": "3",
        "Real-time Systems": "2",
        "Pervasive/Ubiquitous Computing": "1"
    },
    "explanation": "Cyber-Physical Systems focus on physical-cyber interaction; Embedded Systems are not necessarily connected; Real-time Systems focus on time constraints; Pervasive/Ubiquitous Computing focuses on anytime/anywhere computing."
}

add_q(1, matching_q1)
add_q(1, matching_q2)

# Renumber existing t1q9 (Middleware) to t1q10
for q in topics[1]['questions']:
    if q['id'] == 't1q9' and q['type'] == 'mcq':
        q['id'] = 't1q10'

# Sort Topic 1 by id
topics[1]['questions'].sort(key=lambda q: int(q['id'].replace('t1q', '')))

# ============================================================
# TOPIC 2: Remove t2q15 (HTTP not suitable) and t2q16 (SNR)
# ============================================================
saved_t2q15 = get_q(2, 't2q15')
saved_t2q16 = get_q(2, 't2q16')
remove_q(2, 't2q15')
remove_q(2, 't2q16')

# ============================================================
# TOPIC 3: Remove t3q26 (longest range duplicate of t5q18)
#           Add t2q15 (HTTP not suitable) as new t3q26
# ============================================================
remove_q(3, 't3q26')
saved_t2q15['id'] = 't3q26'
saved_t2q15['explanation'] = "HTTP has high overhead and power consumption, making it unsuitable for resource-constrained IoT devices. CoAP was designed as a lightweight alternative."
add_q(3, saved_t2q15)

# ============================================================
# TOPIC 6: Add 3 questions (from T1 and T10)
# ============================================================
saved_t1q8['id'] = 't6q19'
add_q(6, saved_t1q8)

saved_t1q10['id'] = 't6q20'
add_q(6, saved_t1q10)

saved_t10q17 = get_q(10, 't10q17')
saved_t10q17['id'] = 't6q21'
remove_q(10, 't10q17')
add_q(6, saved_t10q17)

# ============================================================
# TOPIC 7: Add 4 questions (1 new + 3 moved)
# ============================================================
ble_topology = {
    "id": "t7q18",
    "type": "multi-select",
    "question": "BLE supports which kind of communication topology?",
    "options": ["Point-to-Point", "Star", "Bus", "Mesh"],
    "correctAnswer": ["Point-to-Point", "Star", "Mesh"],
    "explanation": "BLE supports Point-to-Point, Star, and Mesh topologies. Bus is not supported."
}
add_q(7, ble_topology)

saved_t10q9 = get_q(10, 't10q9')
saved_t10q9['id'] = 't7q19'
remove_q(10, 't10q9')
add_q(7, saved_t10q9)

saved_t10q10 = get_q(10, 't10q10')
saved_t10q10['id'] = 't7q20'
remove_q(10, 't10q10')
add_q(7, saved_t10q10)

saved_t9q21 = get_q(9, 't9q21')
saved_t9q21['id'] = 't7q21'
remove_q(9, 't9q21')
add_q(7, saved_t9q21)

# ============================================================
# TOPIC 8: Add 3 questions (2 matching + 1 moved from T2)
# ============================================================
edge_matching = {
    "id": "t8q17",
    "type": "matching",
    "question": "Match the Edge computing platforms to how they perform inferencing on the device.",
    "items": ["GPU-centric", "CPU-centric"],
    "options": ["1", "2"],
    "descriptions": [
        "1. Raspberry Pi",
        "2. NVidia Jetson"
    ],
    "correctAnswer": {
        "GPU-centric": "2",
        "CPU-centric": "1"
    },
    "explanation": "GPU-centric platforms like NVidia Jetson use GPUs for inferencing, while CPU-centric platforms like Raspberry Pi use CPUs."
}
add_q(8, edge_matching)

cloud_matching = {
    "id": "t8q18",
    "type": "matching",
    "question": "Match the following services to the components that are NOT managed by the Cloud operator (e.g. Microsoft)?",
    "items": ["SaaS", "IaaS", "On Premises", "PaaS"],
    "options": ["1", "2", "3", "4"],
    "descriptions": [
        "1. Networking, Storage, Servers, Virtualization, OS, Middleware, Runtime, Data and Applications.",
        "2. OS, Middleware, Runtime, Data and Applications.",
        "3. Data and Applications.",
        "4. Nil"
    ],
    "correctAnswer": {
        "SaaS": "4",
        "IaaS": "2",
        "On Premises": "1",
        "PaaS": "3"
    },
    "explanation": "On Premises: everything managed by you. IaaS: you manage OS, middleware, runtime, data, apps. PaaS: you manage data and apps only. SaaS: nothing managed by you (Nil)."
}
add_q(8, cloud_matching)

saved_t2q16['id'] = 't8q19'
add_q(8, saved_t2q16)

# ============================================================
# TOPIC 9: Add t10q11 (DSSS 330 bits) to replace removed t9q21
# ============================================================
saved_t10q11 = get_q(10, 't10q11')
saved_t10q11['id'] = 't9q21'
remove_q(10, 't10q11')
add_q(9, saved_t10q11)

# ============================================================
# TOPIC 10: Remove duplicate t10q1 (keep t10q31 which has "None of the Above")
# ============================================================
remove_q(10, 't10q1')

# Renumber all questions in each topic
for topic in data:
    tid = topic['topicId']
    qs = topics[tid]['questions']
    for i, q in enumerate(qs):
        q['id'] = f"t{tid}q{i+1}"
    topics[tid]['questions'] = qs

# Rebuild data
result = []
for tid in sorted(topics.keys()):
    result.append(topics[tid])

with open('questions.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

# Verify counts
print("Question counts per topic:")
total = 0
expected = {1: 10, 2: 14, 3: 26, 4: 14, 5: 18, 6: 21, 7: 21, 8: 19, 9: 21, 10: 26, 11: 11}
all_match = True
for t in result:
    count = len(t['questions'])
    exp = expected[t['topicId']]
    status = "OK" if count == exp else f"MISMATCH (expected {exp})"
    if count != exp:
        all_match = False
    print(f"  {t['topicName']}: {count} {status}")
    total += count
print(f"\nTotal: {total} (expected 201)")
if all_match and total == 201:
    print("ALL COUNTS MATCH!")
else:
    print("WARNING: Some counts don't match!")
