
import argparse
from testguardian.feedback import save_feedback

parser = argparse.ArgumentParser()

parser.add_argument("--test")
parser.add_argument("--actual_label")

args = parser.parse_args()

entry = {
    "test_name": args.test,
    "actual_label": args.actual_label
}

save_feedback(entry)

print("Feedback saved:", entry)
