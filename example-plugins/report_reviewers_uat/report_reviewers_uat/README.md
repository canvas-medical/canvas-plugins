report_reviewers_uat
====================

UAT plugin for how `LabReport`, `ImagingReport`, `ReferralReport`, `UncategorizedClinicalDocument` and `PatientAdministrativeDocument` are assigned for review: to staff members (`reviewers`) or to a team (`team`, from the shared `Report` base).

All endpoints use staff session auth, so open them in a browser tab while logged in to the instance. Responses carry document IDs, assignment dates, review state, reviewer names and team names only.

## Install

The instance must run a home-app build with the `canvas_sdk_data_api_*_reviewers_001` views and the team columns on the lab and imaging report views, and an SDK that includes `reviewers` and the `Report` base.

```sh
canvas install example-plugins/report_reviewers_uat/report_reviewers_uat --host <instance>
```

## Endpoints

| Endpoint | What it does |
| --- | --- |
| `GET /plugin-io/api/report_reviewers_uat/run` | For each document type: total documents, how many have a reviewer, a sample of up to 5 with their reviewers, and a check that `filter(reviewers__id=...)` returns each sampled document for each of its reviewers. `all_passed` is true when every type reads without error and the filter agrees. `types_without_assigned_documents` lists types with no assigned documents to check. |
| `GET /plugin-io/api/report_reviewers_uat/queue` | Documents assigned to the logged-in staff member, grouped by type. Pass `?staff_id=<staff id>` to look at someone else's queue. |
| `GET /plugin-io/api/report_reviewers_uat/document?type=<type>&id=<document id>` | The reviewers and team of one document. `type` is one of `lab_report`, `imaging_report`, `referral_report`, `uncategorized_clinical_document`, `patient_administrative_document`. |

## UAT script

1. Install the plugin and open `/run`. Every type should read without an error.
2. From the Data Integration queue, file documents as a lab report, an imaging report, a specialist report and an uncategorized clinical document, choosing yourself as the reviewer each time.
3. Open `/queue`. The documents assigned to you are listed under their type, with you among their reviewers.
4. Open the uncategorized clinical document's review, click Delegate and delegate it to a colleague. Open `/document?type=uncategorized_clinical_document&id=<document id>`: the reviewer list shows the colleague and not you, and the document drops out of your `/queue`.
5. In the Lab review panel, click "No team assigned" on the lab report's card and pick a team. Open `/document?type=lab_report&id=<document id>`: `team` names that team and `team_assigned_date` is set. Repeat for the imaging report in the Imaging panel.
6. Open `/run` again. `all_passed` is `true`, and the types you assigned documents for no longer appear in `types_without_assigned_documents`.
