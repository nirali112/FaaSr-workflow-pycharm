# FaaSr-workflow-pycharm

This is a [FaaSr](https://faasr.io/) **workflow repository** — the control center where serverless workflows are registered, invoked, and executed on GitHub Actions. It is a fork of [renatof/FaaSr-workflow](https://github.com/renatof/FaaSr-workflow), extended with the workflows below.

## How this repository works

FaaSr workflows are defined as JSON files (one DAG per file). Two repository actions drive everything:

- **(FAASR REGISTER)** — reads a workflow JSON and generates one GitHub Action per DAG node, named `{WorkflowName}-{ActionName}` (you can see these in the [Actions tab](../../actions) and in [.github/workflows](./.github/workflows))
- **(FAASR INVOKE)** — triggers the workflow's entry action; FaaSr then chains the remaining actions per the JSON's `InvokeNext` definitions

Function code is fetched at runtime from the repositories named in each JSON's `FunctionGitRepo`. State between actions is passed exclusively through S3-compatible storage (MinIO Play) via `faasr_get_file` / `faasr_put_file` — actions are stateless containers.

## Registered workflows

### 1. NASAPowerVisualization

Pulls satellite-derived daily climate data from the open (keyless) NASA POWER API, processes three parameters in parallel, and plots this year against the 10-year average.

```text
GetData ──► ProcessPrecipitation ──┐
        ├─► ProcessTemperatureMin ─┼──► PlotData
        └─► ProcessTemperatureMax ─┘
```

- Workflow file: [NASAPowerVisualization.json](./NASAPowerVisualization.json)
- Function code + full tutorial: [nirali112/FaaSr-NASA-Functions](https://github.com/nirali112/FaaSr-NASA-Functions)
- Demonstrates: parallel fan-out, duplicated functions, fan-in, keyless REST APIs, pandas/matplotlib packages
- Output: `faasr/NASAPowerVisualization/NASAPowerComparison.png` on MinIO Play

### 2. pychamp-workflow

A serverless implementation of [PyCHAMP](https://github.com/philip928lin/PyCHAMP) (Crop-Hydrological-Agent Modeling Platform) simulation steps, chained as a FaaSr DAG:

```text
start ──► init ──► aquifer ──► field ──► finance ──► results
```

- Workflow file: [pychamp_workflow.json](./pychamp_workflow.json)
- Function code: the `*_step_faasr.py` files in this repository (initialization, aquifer, field, finance, and results steps; behavior/optimization steps are present but not in the active DAG due to a proprietary Gurobi dependency)
- Each step downloads the shared state payload from S3, reinitializes PyCHAMP components, runs its simulation step, and uploads the updated state

### 3. tutorialRpy

The standard FaaSr tutorial workflow (`start → sum`) used to validate the environment setup. See the [FaaSr tutorial](https://faasr.io/tutorial/).

## Running a workflow

1. **Actions** tab → **(FAASR REGISTER)** → *Run workflow* → enter the JSON filename (e.g., `NASAPowerVisualization.json`) → wait for completion
2. **Actions** tab → **(FAASR INVOKE)** → *Run workflow* → enter the same filename
3. Watch the per-action workflows execute in DAG order
4. Outputs land in the `faasr` bucket on [MinIO Play](https://play.min.io:9443/login) under the folder named in the JSON's `folder_name` arguments

Re-run **(FAASR REGISTER)** after any change to a workflow JSON.

## Required repository secrets

| Secret | Purpose |
|---|---|
| `GH_PAT` | GitHub personal access token (classic; `workflow` + `read:org` scopes) — lets registration write action files |
| `S3_AccessKey` | Data store access key (MinIO Play public sandbox key) |
| `S3_SecretKey` | Data store secret key |

Secret names are derived from the JSON's compute-server and data-store names (`GH` and `S3`): `{ServerName}_PAT`, `{StoreName}_AccessKey` / `_SecretKey`.

## Notes

- **MinIO Play wipes data periodically** — it is a public sandbox. Re-invoke a workflow to regenerate its outputs
- Workflow JSONs are independent: registering or editing one never affects the others
- `scripts/` contains the registration/invocation logic the repository actions call; `faasr_data.json`, `faasr_output.json`, and `payload` are runtime artifacts
