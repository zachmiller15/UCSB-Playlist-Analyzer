import csv

ALL_TRACK_IDS_FILE = "track_ids.txt"
OUTPUT_CSV_FILE = "song_info.csv"
MISSING_IDS_FILE = "missing_ids.txt"


def load_ids_from_txt(path):
    ids = set()

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            track_id = line.strip()

            if track_id:
                ids.add(track_id)

    return ids


def load_processed_ids_from_csv(path):
    ids = set()

    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            track_id = row["track_id"].strip()

            if track_id:
                ids.add(track_id)

    return ids


all_scraped_ids = load_ids_from_txt(ALL_TRACK_IDS_FILE)
processed_ids = load_processed_ids_from_csv(OUTPUT_CSV_FILE)

missing_ids = all_scraped_ids - processed_ids

with open(MISSING_IDS_FILE, "w", encoding="utf-8") as f:
    for track_id in missing_ids:
        f.write(track_id + "\n")

print(f"All scraped unique IDs: {len(all_scraped_ids)}")
print(f"Already in CSV: {len(processed_ids)}")
print(f"Missing IDs: {len(missing_ids)}")
print(f"Wrote missing IDs to {MISSING_IDS_FILE}")