import pandas as pd

print("""
===============================================================================

CDR Analysis by Anthony Holloway (anhollow@cisco.com)

We start with a CDR file spanning ~90 days and containing ~400k records.

I filter for only calls from/to the PSTN.

I classified PSTN calls as those involving one of the following devices:

    REDACTED

I then remove calls from the PSTN to REDACTED, as these were skewing
the percentages, and it appeared to be an Auto Attendant in Unity Connection.

I now split up the calls in the inbound/outbound direction from/to the PSTN.
This is because I need to report on the originalcalledpartynumber field for 
calls from the PSTN, while reporting on callingpartynumber for calls to the 
PSTN.

Finally, I pulled a Top N report off each direction

For calls to the PSTN, I pulled just enough to follow the 80/20 rule, which 
resulted in a Top 300.

For calls from the PSTN, I pulled the Top 100, which captures ~90% of calls.

===============================================================================
""")

# past 90 days of call detail records from cucm
cdr = pd.read_csv("cdr.csv", low_memory=False)

# lower case all of the column names (my preference)
cdr.columns = cdr.columns.str.lower()

# print total number of records from file
print(f"Total Records in File: {len(cdr):,}")

# exclude calls to this number, as it seems to be an autoattendant
cdr = cdr[cdr["originalcalledpartynumber"] != "REDACTED"]

# horizontal rule
print(f"\n{'=' * 79}\n")

# only process records which have a minimum duration (in seconds)
min_duration = 30
cdr_min_duration = cdr[cdr["duration"] >= min_duration]
print(f"Records with Duration > {min_duration}sec: {len(cdr_min_duration):,} ({len(cdr_min_duration) / len(cdr) * 100:.0f}%)")

# horizontal rule
print(f"\n{'=' * 79}\n")

# define our possible pstn voice gateway devices
pstn_devices = [
    "REDACTED",
]

# find calls to/from pstn devices
pstn_calls = cdr_min_duration[(cdr_min_duration["origdevicename"].isin(pstn_devices)) | (cdr_min_duration["destdevicename"].isin(pstn_devices))]
print(f"PSTN Calls: {len(pstn_calls):,} ({len(pstn_calls) / len(cdr_min_duration) * 100:.0f}%)")

# sort out just calls to the pstn
to_pstn = pstn_calls[~pstn_calls["origdevicename"].isin(pstn_devices)]
print(f"\tTo PSTN: {len(to_pstn):,} ({len(to_pstn) / len(pstn_calls) * 100:.0f}%)")

# and those just from the pstn
from_pstn = pstn_calls[~pstn_calls["destdevicename"].isin(pstn_devices)]
print(f"\tFrom PSTN: {len(from_pstn):,} ({len(from_pstn) / len(pstn_calls) * 100:.0f}%)")

# horizontal rule
print(f"\n{'=' * 79}\n")

# top N records which are calling out to the pstn
n = 300
top_n_to_pstn = to_pstn["callingpartynumber"].value_counts().head(n)
print(f"Top {n} to PSTN - Totals {top_n_to_pstn.sum():,} ({top_n_to_pstn.sum() / len(to_pstn) * 100:.0f}% of calls made to PSTN)\n")
print(f"{'Phone Number':<20}{'Count':<20}")
print(f"{'-' * 79}")
for phone_number, count in top_n_to_pstn.to_dict().items():
    print(f"{phone_number:<20}{count:<20}")

# horizontal rule
print(f"\n{'=' * 79}\n")

# top N records which are being called from the pstn
n = 100
top_n_from_pstn = from_pstn["originalcalledpartynumber"].value_counts().head(n)
print(f"Top {n} from PSTN - Totals {top_n_from_pstn.sum():,} ({top_n_from_pstn.sum() / len(from_pstn) * 100:.0f}% of calls received from PSTN)\n")
print(f"{'Phone Number':<20}{'Count':<20}")
print(f"{'-' * 79}")
for phone_number, count in top_n_from_pstn.to_dict().items():
    print(f"{phone_number:<20}{count:<20}")

# horizontal rule
print(f"\n{'=' * 79}\n")
