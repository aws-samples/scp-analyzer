import pandas as pd
import boto3
import logging
import json
import numpy as np
import click

## Setup logging
logging.basicConfig()
logger = logging.getLogger("discover-scps")

# Setup orgs client
session = boto3.Session()
orgs = session.client("organizations")


@click.command()
@click.argument("outfile", default='scps.csv')
def main(outfile):
    """Discover scps applied to accounts in an organization."""
    # Get the account list
    df = list_accounts(orgs)

    # List the scps
    scps = list_scps(orgs)

    # Get the policy documenst for all scps
    policies = get_policies(orgs, scps)

    # Get the targets for each scp
    targets = get_targets_for_scps(orgs, scps)

    # Convert the outputs to dataframes for analysis
    scps = pd.DataFrame(scps)
    targets = pd.DataFrame(targets)
    targets = targets.explode("Targets")
    scps = scps.merge(targets, on="Id")

    ## Extract account id and target type from target
    scps = scps.loc[scps["Targets"].notna()].copy()
    if scps.empty:
        raise SystemExit("SCPs disabled or not applied")

    # Split target Id and Type from the targets
    scps[["TargetId", "TargetType"]] = (
        scps["Targets"].apply(get_target_id).apply(pd.Series)
    )

    # Get parents for each node
    scps["Parents"] = scps["TargetId"].apply(list_parents)

    # For each parent explode the item into the dataframe to get 1 parent per row
    scps = (
        scps["Parents"]
        .explode()
        .apply(pd.Series)
        .rename(columns={"Id": "ParentId", "Type": "ParentType"})
        .drop(columns=[0])
        .join(scps)
    )

    ## Clean up SCPS not applied
    scps.dropna(subset=["TargetId"], inplace=True)
    df["Path"] = df["Id"].apply(consolidate_path, dataframe=scps)
    df["Scps"] = df["Path"].apply(get_scps, scps=scps, policies=policies)

    df_scps = (
        df["Scps"]
        .explode()
        .apply(pd.Series)
        .join(df)
        .astype(str)
        .drop_duplicates()
        .drop(columns="Scps")
    )

    ## Save dataset
    df_scps.to_csv(outfile, index=False)


def get_targets_for_scps(orgs: boto3.client, scps: pd.DataFrame) -> pd.DataFrame:
    """Regurn targets for each SCP."""
    paginator = orgs.get_paginator("list_targets_for_policy")
    targets = []
    for policy in scps:
        options = dict(PolicyId=policy["Id"])
        for page in paginator.paginate(**options):
            targets.append({"Id": policy["Id"], "Targets": page["Targets"]})
    return targets


def get_policies(orgs, scps):
    policies = {}
    for policy in scps:
        policy_doc = orgs.describe_policy(PolicyId=policy["Id"])
        policies[policy["Id"]] = json.loads(policy_doc["Policy"]["Content"])
    return policies


def list_scps(orgs: boto3.client) -> list:
    """List scps for the organization."""
    paginator = orgs.get_paginator("list_policies")
    options = dict(Filter="SERVICE_CONTROL_POLICY")
    scps = []
    for page in paginator.paginate(**options):
        scps.extend(page["Policies"])
    return scps


def list_accounts(orgs):
    accounts = []
    paginator = orgs.get_paginator("list_accounts")
    for page in paginator.paginate():
        accounts.extend(page["Accounts"])
    df = pd.DataFrame(accounts)
    return df


def get_target_id(x):
    try:
        return x["TargetId"], x["Type"]
    except:
        return


def list_parents(child_id):
    try:
        paginator = orgs.get_paginator("list_parents")
        options = {"ChildId": child_id}
        results = []
        for page in paginator.paginate(**options):
            results.extend(page["Parents"])
        return results
    except Exception as err:
        return err


def consolidate_path(target_id, dataframe):
    """Given a target and a dataframe of accounts and SCPs, traverse the account to the root and return a list of hops."""
    hops = [target_id]

    try:
        parent = dataframe.loc[dataframe["TargetId"] == target_id, "ParentId"].values[0]
    except Exception as err:
        logger.error(f"Unable to traverse node: {err}")
        return

    if parent is not np.NaN:
        hops.extend(consolidate_path(parent, dataframe))
    return hops


def get_scps(targets, scps, policies):
    """Return policies for given target list."""
    policy_statements = []

    if not targets:
        return
    for target in targets:
        policy_ids = scps.loc[scps["TargetId"] == target]["Id"].values
        for pid in policy_ids:
            policy_statements.extend(policies[pid]["Statement"])

    return policy_statements
