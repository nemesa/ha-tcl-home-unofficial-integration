#!/usr/bin/python3
import logging
import json
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)

logging.info("Starting to generate notes from diagnostics...")

logging.info("************************************")
logging.info("Tcl_thing")
if len(sys.argv) < 2:
    logging.error("No diagnostics file provided as the first argument of the command.")
    logging.info("usage: generate_notes_from_diagnostics.py ~/Downloads/tcl_home.json")
    sys.exit(1)

fileContent = open(sys.argv[1], "r", encoding="utf-8").read()

diagnostics_obj = json.loads(fileContent)

data = diagnostics_obj.get("data", {})
tcl_things = data.get("tcl_thing", [])
for tcl_thing in tcl_things:
    tcl_thing["device_id"] = "******"
    logging.info("%s", json.dumps(obj=tcl_thing, indent=2))

logging.info("************************************")
logging.info("aws_thing")

aws_thing_reported = data.get("aws_thing", {}).get("state", {}).get("reported", {})
logging.info("%s", json.dumps(obj=aws_thing_reported, indent=2, sort_keys=True))

logging.info("************************************")
logging.info("manual_state_dump_data")
manual_state_dump_data = data.get("manual_state_dump_data", {})
steps = manual_state_dump_data.get("steps", [])
for step in steps:
    logging.info("################################")
    logging.info("--------------------------------")
    logging.info("Step: %s", step["actionDescription"])
    logging.info("--------------------------------")
    logging.info("DesiredKeys: %s", step["changedDesiredKeys"])
    for key in step["changedDesiredKeys"]:
        change = step["changedDesiredData"].get(key, {})
        change_from = change.get("from", "")
        change_to = change.get("to", "")
        logging.info("   %s:(%s)->(%s)", key, change_from, change_to)
    logging.info("ReportedKeys: %s", step["changedReportedKeys"])
    for key in step["changedReportedKeys"]:
        change = step["changedReportedData"].get(key, {})
        change_from = change.get("from", "")
        change_to = change.get("to", "")
        logging.info("   %s:(%s)->(%s)", key, change_from, change_to)
