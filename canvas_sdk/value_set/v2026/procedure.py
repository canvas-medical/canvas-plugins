from ..value_set import ValueSet


class Colonoscopy(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a colonoscopy.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent a screening or diagnostic colonoscopy.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS130v14
    """

    VALUE_SET_NAME = "Colonoscopy"
    OID = "2.16.840.1.113883.3.464.1003.108.12.1020"
    DEFINITION_VERSION = "20171219"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "44388",  # Colonoscopy through stoma; diagnostic, including collection of specimen(s) by brushing or washing...
        "44389",  # Colonoscopy through stoma; with biopsy, single or multiple
        "44390",  # Colonoscopy through stoma; with removal of foreign body(s)
        "44391",  # Colonoscopy through stoma; with control of bleeding, any method
        "44392",  # Colonoscopy through stoma; with removal of tumor(s), polyp(s), or other lesion(s) by hot biopsy f...
        "44394",  # Colonoscopy through stoma; with removal of tumor(s), polyp(s), or other lesion(s) by snare technique
        "44401",  # Colonoscopy through stoma; with ablation of tumor(s), polyp(s), or other lesion(s) (includes pre-...
        "44402",  # Colonoscopy through stoma; with endoscopic stent placement (including pre- and post-dilation and ...
        "44403",  # Colonoscopy through stoma; with endoscopic mucosal resection
        "44404",  # Colonoscopy through stoma; with directed submucosal injection(s), any substance
        "44405",  # Colonoscopy through stoma; with transendoscopic balloon dilation
        "44406",  # Colonoscopy through stoma; with endoscopic ultrasound examination, limited to the sigmoid, descen...
        "44407",  # Colonoscopy through stoma; with transendoscopic ultrasound guided intramural or transmural fine n...
        "44408",  # Colonoscopy through stoma; with decompression (for pathologic distention) (eg, volvulus, megacolo...
        "45378",  # Colonoscopy, flexible; diagnostic, including collection of specimen(s) by brushing or washing, wh...
        "45379",  # Colonoscopy, flexible; with removal of foreign body(s)
        "45380",  # Colonoscopy, flexible; with biopsy, single or multiple
        "45381",  # Colonoscopy, flexible; with directed submucosal injection(s), any substance
        "45382",  # Colonoscopy, flexible; with control of bleeding, any method
        "45384",  # Colonoscopy, flexible; with removal of tumor(s), polyp(s), or other lesion(s) by hot biopsy forceps
        "45385",  # Colonoscopy, flexible; with removal of tumor(s), polyp(s), or other lesion(s) by snare technique
        "45386",  # Colonoscopy, flexible; with transendoscopic balloon dilation
        "45388",  # Colonoscopy, flexible; with ablation of tumor(s), polyp(s), or other lesion(s) (includes pre- and...
        "45389",  # Colonoscopy, flexible; with endoscopic stent placement (includes pre- and post-dilation and guide...
        "45390",  # Colonoscopy, flexible; with endoscopic mucosal resection
        "45391",  # Colonoscopy, flexible; with endoscopic ultrasound examination limited to the rectum, sigmoid, des...
        "45392",  # Colonoscopy, flexible; with transendoscopic ultrasound guided intramural or transmural fine needl...
        "45393",  # Colonoscopy, flexible; with decompression (for pathologic distention) (eg, volvulus, megacolon), ...
        "45398",  # Colonoscopy, flexible; with band ligation(s) (eg, hemorrhoids)
    }

    HCPCSLEVELII = {
        "G0105",  # Colorectal cancer screening; colonoscopy on individual at high risk
        "G0121",  # Colorectal cancer screening; colonoscopy on individual not meeting criteria for high risk
    }

    SNOMEDCT = {
        "1209098000",  # Fiberoptic colonoscopy with biopsy of lesion of colon (procedure)
        "1217313001",  # Biopsy of colon using endoscopic ultrasonography guidance (procedure)
        "12350003",  # Colonoscopy with rigid sigmoidoscope through colotomy (procedure)
        "1304042004",  # Colonoscopy and suturing of rectum (procedure)
        "1304043009",  # Colonoscopy and suturing of colon (procedure)
        "1304044003",  # Colonoscopy and suturing of small intestine (procedure)
        "1304045002",  # Colonoscopy and full thickness resection of rectum (procedure)
        "1304049008",  # Colonoscopy and full thickness resection of colon (procedure)
        "1304050008",  # Colonoscopy and full thickness resection of small intestine (procedure)
        "174158000",  # Open colonoscopy (procedure)
        "174173004",  # Fiberoptic endoscopic laser destruction of lesion of colon (procedure)
        "174179000",  # Fiberoptic endoscopic dilation of colon (procedure)
        "174185007",  # Diagnostic fiberoptic endoscopic examination of colon and biopsy of lesion of colon (procedure)
        "235150006",  # Total colonoscopy (procedure)
        "25732003",  # Fiberoptic colonoscopy with biopsy (procedure)
        "302052009",  # Endoscopic biopsy of lesion of colon (procedure)
        "367535003",  # Fiberoptic colonoscopy (procedure)
        "443998000",  # Colonoscopy through colostomy with endoscopic biopsy of colon (procedure)
        "444783004",  # Screening colonoscopy (procedure)
        "446521004",  # Colonoscopy and excision of mucosa of colon (procedure)
        "446745002",  # Colonoscopy and biopsy of colon (procedure)
        "447021001",  # Colonoscopy and tattooing (procedure)
        "48021000087103",  # Colonoscopy using cecal retroflexion technique (procedure)
        "48031000087101",  # Colonoscopy using rectal retroflexion technique (procedure)
        "609197007",  # Endoscopic surgical procedure on colon using laser (procedure)
        "709421007",  # Colonoscopy and dilation of stricture of colon (procedure)
        "710293001",  # Colonoscopy using fluoroscopic guidance (procedure)
        "711307001",  # Colonoscopy using plain X-ray guidance (procedure)
        "73761001",  # Colonoscopy (procedure)
        "771568007",  # Fiberoptic endoscopic excision of lesion of colonic mucous membrane (procedure)
        "789778002",  # Colonoscopy and fecal microbiota transplantation (procedure)
        "8180007",  # Fiberoptic colonoscopy through colostomy (procedure)
    }

class FlexibleSigmoidoscopy(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a flexible sigmoidoscopy.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent a flexible sigmoidoscopy.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS130v14
    """

    VALUE_SET_NAME = "Flexible Sigmoidoscopy"
    OID = "2.16.840.1.113883.3.464.1003.198.12.1010"
    DEFINITION_VERSION = "20171219"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "45330",  # Sigmoidoscopy, flexible; diagnostic, including collection of specimen(s) by brushing or washing, ...
        "45331",  # Sigmoidoscopy, flexible; with biopsy, single or multiple
        "45332",  # Sigmoidoscopy, flexible; with removal of foreign body(s)
        "45333",  # Sigmoidoscopy, flexible; with removal of tumor(s), polyp(s), or other lesion(s) by hot biopsy for...
        "45334",  # Sigmoidoscopy, flexible; with control of bleeding, any method
        "45335",  # Sigmoidoscopy, flexible; with directed submucosal injection(s), any substance
        "45337",  # Sigmoidoscopy, flexible; with decompression (for pathologic distention) (eg, volvulus, megacolon)...
        "45338",  # Sigmoidoscopy, flexible; with removal of tumor(s), polyp(s), or other lesion(s) by snare technique
        "45340",  # Sigmoidoscopy, flexible; with transendoscopic balloon dilation
        "45341",  # Sigmoidoscopy, flexible; with endoscopic ultrasound examination
        "45342",  # Sigmoidoscopy, flexible; with transendoscopic ultrasound guided intramural or transmural fine nee...
        "45346",  # Sigmoidoscopy, flexible; with ablation of tumor(s), polyp(s), or other lesion(s) (includes pre- a...
        "45347",  # Sigmoidoscopy, flexible; with placement of endoscopic stent (includes pre- and post-dilation and ...
        "45349",  # Sigmoidoscopy, flexible; with endoscopic mucosal resection
        "45350",  # Sigmoidoscopy, flexible; with band ligation(s) (eg, hemorrhoids)
    }

    HCPCSLEVELII = {
        "G0104",  # Colorectal cancer screening; flexible sigmoidoscopy
    }

    SNOMEDCT = {
        "1217117008",  # Endoscopic examination of lower bowel and sampling for bacterial overgrowth (procedure)
        "396226005",  # Flexible fiberoptic sigmoidoscopy with biopsy (procedure)
        "44441009",  # Flexible fiberoptic sigmoidoscopy (procedure)
    }

class TotalColectomy(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a total colectomy.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent a total colectomy.

    **Exclusion Criteria:** Excludes concepts that represent partial colectomies.

    ** Used in:** CMS130v14
    """

    VALUE_SET_NAME = "Total Colectomy"
    OID = "2.16.840.1.113883.3.464.1003.198.12.1019"
    DEFINITION_VERSION = "20240112"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "44150",  # Colectomy, total, abdominal, without proctectomy; with ileostomy or ileoproctostomy
        "44151",  # Colectomy, total, abdominal, without proctectomy; with continent ileostomy
        "44152",  # Colectomy, total, abdominal, without proctectomy; with rectal mucosectomy, ileoanal anastomosis, ...
        "44153",  # Colectomy, total, abdominal, without proctectomy; with rectal mucosectomy, ileoanal anastomosis, ...
        "44155",  # Colectomy, total, abdominal, with proctectomy; with ileostomy
        "44156",  # Colectomy, total, abdominal, with proctectomy; with continent ileostomy
        "44157",  # Colectomy, total, abdominal, with proctectomy; with ileoanal anastomosis, includes loop ileostomy...
        "44158",  # Colectomy, total, abdominal, with proctectomy; with ileoanal anastomosis, creation of ileal reser...
        "44210",  # Laparoscopy, surgical; colectomy, total, abdominal, without proctectomy, with ileostomy or ileopr...
        "44211",  # Laparoscopy, surgical; colectomy, total, abdominal, with proctectomy, with ileoanal anastomosis, ...
        "44212",  # Laparoscopy, surgical; colectomy, total, abdominal, with proctectomy, with ileostomy
    }

    ICD10PCS = {
        "0DTE0ZZ",  # Resection of Large Intestine, Open Approach
        "0DTE4ZZ",  # Resection of Large Intestine, Percutaneous Endoscopic Approach
        "0DTE7ZZ",  # Resection of Large Intestine, Via Natural or Artificial Opening
        "0DTE8ZZ",  # Resection of Large Intestine, Via Natural or Artificial Opening Endoscopic
    }

    SNOMEDCT = {
        "26390003",  # Total colectomy (procedure)
        "303401008",  # Parks panproctocolectomy, anastomosis of ileum to anus and creation of pouch (procedure)
        "307666008",  # Total colectomy and ileostomy (procedure)
        "307667004",  # Total colectomy, ileostomy and rectal mucous fistula (procedure)
        "307669001",  # Total colectomy, ileostomy and closure of rectal stump (procedure)
        "31130001",  # Total abdominal colectomy with proctectomy and ileostomy (procedure)
        "36192008",  # Total abdominal colectomy with ileoproctostomy (procedure)
        "44751009",  # Total abdominal colectomy with proctectomy and continent ileostomy (procedure)
        "456004",  # Total abdominal colectomy with ileostomy (procedure)
        "713165008",  # Laparoscopic total colectomy with ileo-rectal anastomosis (procedure)
        "787108001",  # Laparoscopic restorative proctocolectomy with ileal pouch anal anastomosis (procedure)
        "787109009",  # Excision of entire colon and entire rectum (procedure)
        "787874000",  # Laparoscopic total colectomy (procedure)
        "787875004",  # Laparoscopic total colectomy and loop ileostomy (procedure)
        "787876003",  # Laparoscopic total colectomy and ileostomy (procedure)
        "80294005",  # Total abdominal colectomy with rectal mucosectomy and ileoanal anastomosis (procedure)
        "858579005",  # Excision of entire colon, entire rectum and entire anal canal (procedure)
    }


__exports__ = (
    "Colonoscopy",
    "FlexibleSigmoidoscopy",
    "TotalColectomy",
)
