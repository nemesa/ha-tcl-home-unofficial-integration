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
tcl_things = data.get("tcl", {}).get("tcl_things", [])
conter = 1
for tcl_thing in tcl_things:
    tcl_thing["device_id"] = "******"+str(conter)
    logging.info("%s", json.dumps(obj=tcl_thing, indent=2))
    conter+=1

logging.info("************************************")
logging.info("aws_things")

aws_things = data.get("aws_init",{}).get("aws_things",[])
conter = 1
for aws_thing in aws_things:
    logging.info("--------------------------------")
    logging.info("%s","******"+str(conter))
    logging.info("--------------------------------")
    logging.info("%s", json.dumps(obj=aws_thing.get("reported",{}), indent=2, sort_keys=True))
    conter+=1

logging.info("************************************")
logging.info("manual_state_dump_data")
manual_state_dump_data = data.get("manual_state_dump_data", {})
if manual_state_dump_data:
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
