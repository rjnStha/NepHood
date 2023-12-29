import os

with open('Firebase.env') as f:
    for line in f:
        if 'export' not in line:
            continue
        if line.startswith('#'):
            continue
        # Remove leading `export `
        # then, split name / value pair
        key, value = line.replace('export ', '', 1).strip().split('=', 1)
        os.environ[key] = value