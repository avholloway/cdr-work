import pandas as pd

# past 90 days of call detail records from cucm
cdr = pd.read_csv("cdr.csv", low_memory=False)

# combine in and out bound calls into a single metric
in_and_out = False

# lower case all of the column names (my preference)
cdr.columns = cdr.columns.str.lower()

# define what we think are pstn devices
pstn_devices = [
    "REDACTED",
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


# save report to excel document
with pd.ExcelWriter('report.xlsx') as writer:

    if in_and_out:
        pstn = pd.concat([to_pstn, fr_pstn])
        pstn["phone_number"].value_counts().rename_axis("phone_number").reset_index(name="call_count").to_excel(writer, sheet_name="By Call Count", index=False)
        pstn.groupby("phone_number", sort=True).sum().reset_index().sort_values("duration", ascending=False).to_excel(writer, sheet_name="By Call Duration", index=False)
    else:
        fr_pstn["phone_number"].value_counts().rename_axis("phone_number").reset_index(name="call_count").to_excel(writer, sheet_name="In - By Call Count", index=False)
        to_pstn["phone_number"].value_counts().rename_axis("phone_number").reset_index(name="call_count").to_excel(writer, sheet_name="Out - By Call Count", index=False)
        fr_pstn.groupby("phone_number", sort=True).sum().reset_index().sort_values("duration", ascending=False).to_excel(writer, sheet_name="In - By Call Duration", index=False)
        to_pstn.groupby("phone_number", sort=True).sum().reset_index().sort_values("duration", ascending=False).to_excel(writer, sheet_name="Out - By Call Duration", index=False)
