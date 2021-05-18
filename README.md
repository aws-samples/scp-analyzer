# SCP analyzer

This tool collects and presents all the SCPs applicable to each account in an AWS Organization. It writes the data to a csv formatted file.

## Why do we need this tool?

Developers often get stuck deploying in large organizations that have both SCPs and restrictive IAM policies. This tool allows a security team to catalog the existing applicable SCPs at any given time and use that to help developers understand if their actions are being restricted by an SCP. It also helps understand if planned future actions will be restricted by existing SCPs. 

## How to install & use

```
1. Clone the repo
2. pip install --user . or make install
3. scps --help for help
4. scps to just execute
```

## Use requirements

You will need to be in the Organizations Management account or in a delegated administration account with Read Only permissions to the Organizations API to run this.