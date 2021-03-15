import pandas as pd

# past 90 days of call detail records from cucm
cdr = pd.read_csv("cdr.csv", low_memory=False)

# lower case all of the column names (my preference)
cdr.columns = cdr.columns.str.lower()

# define what we think are pstn devices
pstn_devices = [
    "REDACTED"
]

# pstn outbound
to_cols = [
    "callingpartynumber",
    "duration",
]
to_pstn = cdr.loc[cdr["destdevicename"].isin(pstn_devices), to_cols]
to_pstn.rename(columns={"callingpartynumber":"phone_number"}, inplace=True)

# pstn inbound
fr_cols = [
    "originalcalledpartynumber",
    "duration",
]
fr_pstn = cdr.loc[cdr["origdevicename"].isin(pstn_devices), fr_cols]
fr_pstn.rename(columns={"originalcalledpartynumber":"phone_number"}, inplace=True)

# combine pstn outbound and inbound into a single dataframe
pstn = pd.concat([to_pstn, fr_pstn])

# save report to excel document
with pd.ExcelWriter('report.xlsx') as writer:

    # save off a "by call count" sheet
    pstn["phone_number"].value_counts().rename_axis("phone_number").reset_index(name="call_count").to_excel(writer, sheet_name="By Call Count", index=False)

    # save off a "by duration" sheet
    pstn.groupby("phone_number", sort=True).sum().reset_index().sort_values("duration", ascending=False).to_excel(writer, sheet_name="By Call Duration", index=False)
