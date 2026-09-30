# Secure AI Hackathon Day 2 & 3

Source: https://www.kaggle.com/competitions/secure-ai-hackathon

- Host: Nani Desmond
- Deadline: 2026-09-30T23:59:00Z
- Max daily submissions: 5
- Max team size: 10
- License: MIT

## Tracks

### Intermediate Track (prize: The Gallant Giant)

## Fix the non-IID problem

Client data is deliberately skewed (some banks see almost only one kind of traffic).
Naive averaging performs worse under this skew, your job is to design a better
aggregation strategy that closes the gap.


### Advanced (prize: The Wholesome Expert)

## Detect or resist a poisoning attack

Partway through, one of the five "banks" turns malicious and starts sending sabotaged
updates. Detect it, resist it, or both. This track is where CAIRLab's mission, securing
AI in adversarial, distributed settings, shows up most directly, and it's judged with
that in mind.


---

# Page: data-description

## About the Dataset

This hackathon uses **NSL-KDD**, a widely-used, well-documented network intrusion
detection dataset, an improved version of the original KDD Cup 1999 dataset with
duplicate records removed, which makes it fairer and harder to game than the original.
Each row is a single network connection record; the task is to tell **normal traffic**
from an **attack**.

We picked NSL-KDD deliberately: it's small enough to train on CPU in seconds, tabular
enough that feature engineering matters more than architecture, and realistic enough
that the class imbalance and non-IID issues you'll hit are the same ones real intrusion
detection systems face, not artifacts of a toy dataset.

## Files Provided

| File | What it is |
|---|---|
| `02_Beginner_Track_Day2` | The starter notebook — downloads, cleans, and partitions the data for you. Start here. |
| `client_0.csv` … `client_4.csv` (IID) | Training data split evenly across 5 simulated "banks" — use for the 🟢 Beginner track. |
| `client_0.csv` … `client_4.csv` (non-IID) | The same training pool, but skewed unevenly across the 5 banks — use for the 🟡 Intermediate track. |
| `test_public.csv` | Unlabeled features for the held-out evaluation set — this is what your final model should predict on. |
| `sample_submission.csv` | The exact format your predictions should follow. |

You won't need to download or clean NSL-KDD yourself,  the starter notebook does this
automatically from a public source and produces all of the files above with a fixed
random seed, so everyone starts from the identical baseline.

## Data Dictionary

Every row is one network connection, described by 41 features plus a label. Categorical
features are label-encoded and all features are standardized (zero mean, unit variance)
before you see them — you're working with model-ready numeric data from the start.

**Basic connection features** — properties of the raw TCP/IP connection itself:
`duration`, `protocol_type`, `service`, `flag`, `src_bytes`, `dst_bytes`, `land`,
`wrong_fragment`, `urgent`

**Content features** — derived from inspecting the connection's payload for
suspicious behavior:
`hot`, `num_failed_logins`, `logged_in`, `num_compromised`, `root_shell`,
`su_attempted`, `num_root`, `num_file_creations`, `num_shells`, `num_access_files`,
`num_outbound_cmds`, `is_host_login`, `is_guest_login`

**Traffic features** — computed over a 2-second window of recent connections to
the same host/service (useful for spotting scans and floods):
`count`, `srv_count`, `serror_rate`, `srv_serror_rate`, `rerror_rate`,
`srv_rerror_rate`, `same_srv_rate`, `diff_srv_rate`, `srv_diff_host_rate`

**Host-based traffic features** — the same idea, computed over the last 100
connections to the same destination host (catches slower, low-and-slow attacks that a
2-second window would miss):
`dst_host_count`, `dst_host_srv_count`, `dst_host_same_srv_rate`,
`dst_host_diff_srv_rate`, `dst_host_same_src_port_rate`, `dst_host_srv_diff_host_rate`,
`dst_host_serror_rate`, `dst_host_srv_serror_rate`, `dst_host_rerror_rate`,
`dst_host_srv_rerror_rate`

**Label:** `binary_label` — `0` = normal traffic, `1` = attack (originally over 20
distinct attack types — normal, DoS, probe, and rare R2L/U2R attacks — collapsed to
binary here so the leaderboard rewards catching *any* intrusion, not memorizing attack
names). Roughly balanced overall (~53% normal / ~47% attack) in the public data, though
individual client partitions may look very different — that's intentional, see the
🟡 Intermediate track.

## A note on the held-out evaluation set

Your final score is computed against a separate slice of data that was set aside
*before* any of the client files above were created — no client, and no team, ever
trains on it. This is what makes the leaderboard score meaningful rather than just a
measure of how well you memorized your own training data.


---

# Page: Description

## The Story

You're a consortium of five banks. You all want to catch the same fraud and
network-intrusion patterns, but you're legally forbidden from pooling your customer
traffic data into one place. Federated learning (FL) is the answer: each bank trains a
model **locally** on its own data, and only the trained *model updates*, never the raw
data, get shared and averaged into one global model.

That single idea is why CAIRLab exists: securing AI models in exactly this kind of
distributed, don't-trust-everyone setting is a live, unsolved research problem, not a
classroom exercise.

## The Problem

Day 1 already ran as a separate automated leaderboard (the Beginner track — if you
haven't done it yet, find that link in the announcement channel first). Today, two more
tracks unlock, and you're free to attempt either or both:

- 🟡 **Intermediate** — the "banks" don't all see the same kind of traffic in real life,
  and that breaks the simple version of federated learning. Fix it.
- 🔴 **Advanced (optional)** — what happens when one of the banks can't be trusted?
  Detect it, or make your system resist it anyway.

Full technical detail, a working baseline, and a new notebook are provided , you're
extending a real system, not building one from scratch.

## Getting Started

1. Copy the Day 2 extension notebook (linked in **Data**) into your own Kaggle Notebook
   or Colab, it's self-contained, you don't need yesterday's notebook open.
2. Run every cell top to bottom once.
3. Read the track descriptions below and pick where your team wants to focus.
4. Every section marked `🔧 YOUR TURN` is a hook, that's where your work goes.

## Scoring

Unlike Day 1, these two tracks aren't on a live leaderboard, a single number can't
capture "how your defense holds up under attack" the way it can capture "did you flag
this connection correctly." Instead:

- An **objective component**: the before/after F1 comparison you report yourself,
  independently verified by organizers against your exported model.
- A **Writeup + video**, judged by CAIRLab mentors on understanding and creativity,
  explaining *why* your approach works is the most transferable skill of the week.

Full rubric is in the **Evaluation** tab.

## Timeline

- **Day 0:** Kickoff + primer session (FL fundamentals, security angle, starter kit
  walkthrough)
- **Day 1:** 🟢 Beginner track — separate automated leaderboard (already run)
- **Days 2–3:** 🟡 Intermediate and 🔴 Advanced tracks unlock together, here
- **Day 4:** Submission deadline (Writeup + all attachments)
- **Day 6:** Demo day, judging, awards, and an invitation for top teams into ongoing
  CAIRLab research


---

# Page: Submission Requirements

A valid submission must contain all of the following. Incomplete submissions will not be
considered by the Judges. Unlike Day 1, this is not automatically scored, a Writeup and
its attachments are what judges review.

### 1. Kaggle Writeup
Your project report. Include a title, subtitle, and which track(s) you're submitting, 
Intermediate, Advanced, or both. **Max 1,500 words**, submissions over this limit may be
penalized.

Since there's no live leaderboard for these tracks, your Writeup is also where your
automated score comes from: report your F1 **before and after** your change (naive
FedAvg vs. your aggregation for Intermediate; under-attack vs. your defense for
Advanced) on the same held-out test set. This comparison is the single most important
number in your submission, make it easy to find.

Recommended structure: what you tried, what worked, what didn't, and why.

### 2. Media Gallery
A cover image is required. Good things to include: your F1-over-rounds chart showing the
before/after comparison, a diagram of your aggregation or defense strategy, or a
confusion matrix on the held-out set.

### 3. Public Notebook
Attach your final, fully-run copy of the Day 2 extension notebook (or your modified
version). Every cell should execute top to bottom with outputs visible. If it started as
a private Kaggle Notebook, that's fine, it will be made public automatically after the
deadline.

### 4. Public Video
**3 minutes or less**, published to YouTube (unlisted is fine). Walk through your
approach and your results, treat this as your elevator pitch to the judges.

### 5. Public Project Link
A link to your public GitHub repo containing your code, with clear setup instructions in
the README (how to reproduce your aggregation/defense results). Your repo must also
include:
- `model_scripted.pt` — your final exported model (the notebook's submission cell
  produces this for you)
- `submission.json` — the metrics file produced alongside it

These two files are what the organizers use to independently verify your reported
numbers before judging, a repo missing them can't be scored on the automated component,
regardless of what your Writeup claims.

If your repo is just the notebook and these two files, that's fine, the point is judges
can find and re-run your work without asking you for access.


---

# Page: rules

##ENTRY IN THIS COMPETITION CONSTITUTES YOUR ACCEPTANCE OF THESE OFFICIAL COMPETITION RULES.

**[See Section 3.18 for defined terms](rules#18.-terms)**

*The Competition named below is a skills-based competition to promote and further the field of data science. You must register via the Competition Website to enter. To enter the Competition, you must agree to these Official Competition Rules, which incorporate by reference the provisions and content of the Competition Website and any Specific Competition Rules herein (collectively, the "Rules"). Please read these Rules carefully before entry to ensure you understand and agree. You further agree that Submission in the Competition constitutes agreement to these Rules. You may not submit to the Competition and are not eligible to receive the prizes associated with this Competition unless you agree to these Rules. These Rules form a binding legal agreement between you and the Competition Sponsor with respect to the Competition. Your competition Submissions  must conform to the requirements stated on the Competition Website. Your Submissions will be scored based on the evaluation metric described on the Competition Website. Subject to compliance with the Competition Rules, Prizes, if any, will be awarded to Participants with the best scores, based on the merits of the data science models submitted. See below for the complete Competition Rules. For Competitions designated as hackathons by the Competition Sponsor (“Hackathons”), your Submissions will be judged by the Competition Sponsor based on the evaluation rubric set forth on the Competition Website (“Evaluation Rubric”).  The Prizes, if any, will be awarded to Participants with the highest ranking(s) as determined by the Competition Sponsor based on such rubric.*

**You cannot sign up to Kaggle from multiple accounts and therefore you cannot enter or submit from multiple accounts.**

<h3>1. COMPETITION-SPECIFIC TERMS</h3>
<h4>1. COMPETITION TITLE</h4> SECURE AI HACKATHON
<h4>2. COMPETITION SPONSOR</h4>  CAIRLab
<h4>3. COMPETITION SPONSOR ADDRESS</h4> COLLEGE OF SCIENCE, KNUST
<h4>4. COMPETITION WEBSITE</h4> https://www.kaggle.com/competitions/[INSERT]
<h4>5. TOTAL PRIZES AVAILABLE: $[INSERT]</h4> 
First Prize: $[INSERT]
Second Prize: $[INSERT]
Third Prize: $[INSERT]
[INSERT NON-MONETARY PRIZES AS APPLICABLE]
<h4>6. WINNER LICENSE TYPE</h4> [INSERT]
<h4>7. DATA ACCESS AND USE</h4> [INSERT]


###2. COMPETITION-SPECIFIC RULES 
In addition to the provisions of the General Competition Rules below, you understand and agree to these Competition-Specific Rules required by the Competition Sponsor:

####1. TEAM LIMITS
a. The maximum Team size is five (5).</h5>
b. Team mergers are allowed and can be performed by the Team leader. In order to merge, the combined Team must have a total Submission count less than or equal to the maximum allowed as of the Team Merger Deadline. The maximum allowed is the number of Submissions per day multiplied by the number of days the competition has been running.  For Hackathons, each team is allowed one (1) Submission; any Submissions submitted by Participants before merging into a Team will be unsubmitted.</h5>

####2. SUBMISSION LIMITS
a. You may submit a maximum of five (5) Submissions per day.</h5>
b. You may select up to two (2) Final Submissions for judging.</h5>
c. For Hackathons, each Team may submit one (1) Submission only.</h5>

####3. COMPETITION TIMELINE
a. Competition Timeline dates (including Entry Deadline, Final Submission Deadline, Start Date, and Team Merger Deadline, as applicable) are reflected on the competition’s Overview > Timeline page.</h5>

#### 4. COMPETITION DATA

a. Data Access and Use. [CHOOSE ONE OF THE 3 OPTIONS BELOW BASED ON WHAT THE SPONSOR CHOOSES IN THE SOW.]</h5>

1. [*Competition Use only is checked*: You may access and use the Competition Data only for participating in the Competition and on Kaggle.com forums. The Competition Sponsor reserves the right to disqualify any Participant who uses the Competition Data other than as permitted by the Competition Website and these Rules.].</h6>

2. [*Competition Use and Non-Commercial & Academic Research is checked*: You may access and use the Competition Data for non-commercial purposes only, including for participating in the Competition and on Kaggle.com forums, and for academic research and education. The Competition Sponsor reserves the right to disqualify any Participant who uses the Competition Data other than as permitted by the Competition Website and these Rules.].</h6>

3. [*Competition Use and Commercial are checked*: You may access and use the Competition Data for any purpose, whether commercial or non-commercial, including for participating in the Competition and on Kaggle.com forums, and for academic research and education. The Competition Sponsor reserves the right to disqualify any Participant who uses the Competition Data other than as permitted by the Competition Website and these Rules. </h6>

4. [*ADD IN THE FOLLOWING, IN ADDITION TO THE CHOSEN SECTION ABOVE, IF SPECIFIC LICENSE IS CHECKED*: The Competition Data is also subject to the following terms and conditions: [INSERT URL].</h6>

5. None. [COMPETITION DATA MAY NOT BE NEEDED FOR HACKATHONS] Competition Data will not be provided by Competition Sponsor for this Competition.</h6>

b. Data Security.</h5>

1. You agree to use reasonable and suitable measures to prevent persons who have not formally agreed to these Rules from gaining access to the Competition Data. You agree not to transmit, duplicate, publish, redistribute or otherwise provide or make available the Competition Data to any party not participating in the Competition. You agree to notify Kaggle immediately upon learning of any possible unauthorized transmission of or unauthorized access to the Competition Data and agree to work with Kaggle to rectify any unauthorized transmission or access.</h6>

####5. WINNER LICENSE [INSERT ONLY THE RELEVANT LICENSE LANGUAGE FOR THE COMPETITION.]

a. Under Section 2.8 (Winners Obligations) of the General Rules below, you hereby grant and will grant the Competition Sponsor the following license(s) with respect to your Submission if you are a Competition winner:</h5>

1. [*Non-Exclusive*: You hereby grant and will grant to Competition Sponsor and its designees a worldwide, non-exclusive, sub-licensable, transferable, fully paid-up, royalty-free, perpetual, irrevocable right to use, reproduce, distribute, create derivative works of, publicly perform, publicly display, digitally perform, make, have made, sell, offer for sale and import your winning Submission and the source code used to generate the Submission, in any media now known or developed in the future, for any purpose whatsoever, commercial or otherwise, without further approval by or payment to you.] </h6>
 
2. [*Open Source: You hereby license and will license your winning Submission and the source code used to generate the Submission under an Open Source Initiative-approved license (see [www.opensource.org] (http://www.opensource.org)) that in no event limits commercial use of such code or model containing or depending on such code. </h6>

3. For generally commercially available software that you used to generate your Submission that is not owned by you, but that can be procured by the Competition Sponsor without undue expense, you do not need to grant the license in the preceding Section for that software. </h6>

4. In the event that input data or pretrained models with an incompatible license are used to generate your winning solution, you do not need to grant an open source license in the preceding Section for that data and/or model(s). </h6>

b. You may be required by the Sponsor to provide a detailed description of how the winning Submission was generated, to the Competition Sponsor’s specifications, as outlined in Section 2.8, Winner’s Obligations. This may include a detailed description of methodology, where one must be able to reproduce the approach by reading the description, and includes a detailed explanation of the architecture, preprocessing, loss function, training details, hyper-parameters, etc. The description should also include a link to a code repository with complete and detailed instructions so that the results obtained can be reproduced.</h7>
 
####6. EXTERNAL DATA AND TOOLS

a. You may use data other than the Competition Data (“External Data”) to develop and test your Submissions. However, you will ensure the External Data is either publicly available and equally accessible to use by all Participants of the Competition for purposes of the competition at no cost to the other Participants, or satisfies the Reasonableness criteria as outlined in Section 2.6.b below. The ability to use External Data under this Section does not limit your other obligations under these Competition Rules, including but not limited to Section 2.8 (Winners Obligations). </h5>

b. The use of external data and models is acceptable unless specifically prohibited by the Host. Because of the potential costs or restrictions (e.g., “geo restrictions”) associated with obtaining rights to use external data or certain software and associated tools, their use must be “reasonably accessible to all” and of “minimal cost”. Also, regardless of the cost challenges as they might affect all Participants during the course of the competition, the costs of potentially procuring a license for software used to generate a Submission, must also be considered. The Host will employ an assessment of whether or not the following criteria can exclude the use of the particular LLM, data set(s), or tool(s):</h5>

1. Are Participants being excluded from a competition because of the "excessive" costs for access to certain LLMs, external data, or tools that might be used by other Participants. The Host will assess the excessive cost concern by applying a “Reasonableness” standard (the “Reasonableness Standard”). The Reasonableness Standard will be determined and applied by the Host in light of things like cost thresholds and accessibility.</h6>

2. By way of example only, a small subscription charge to use additional elements of a large language model such as Gemini Advanced are acceptable if meeting the Reasonableness Standard of Sec. 8.2. Purchasing a license to use a proprietary dataset that exceeds the cost of a prize in the competition would not be considered reasonable.</h6>

c. Automated Machine Learning Tools (“AMLT”)</h5>

1. Individual Participants and Teams may use automated machine learning tool(s) (“AMLT”) (e.g., Google toML, H2O Driverless AI, etc.) to create a Submission, provided that the Participant or Team ensures that they have an appropriate license to the AMLT such that they are able to comply with the Competition Rules. </h6>

####7. ELIGIBILITY

a. Unless otherwise stated in the Competition-Specific Rules above or prohibited by internal policies of the Competition Entities, employees, interns, contractors, officers and directors of Competition Entities may enter and participate in the Competition, but are not eligible to win any Prizes. "Competition Entities" means the Competition Sponsor, Kaggle Inc., and their respective parent companies, subsidiaries and affiliates. If you are such a Participant from a Competition Entity, you are subject to all applicable internal policies of your employer with respect to your participation.</h5>

####8. WINNER’S OBLIGATIONS

a. As a condition to being awarded a Prize, a Prize winner must fulfill the following obligations:</h5>

1. Deliver to the Competition Sponsor the final model's software code as used to generate the winning Submission and associated documentation. The delivered software code should follow [these documentation guidelines](https://www.kaggle.com/WinningModelDocumentationGuidelines), must be capable of generating the winning Submission, and contain a description of resources required to build and/or run the executable code successfully. For avoidance of doubt, delivered software code should include training code, inference code, and a description of the required computational environment. For Hackathons, the Submission deliverables will be as described on the Competition Website, which may be information or materials that are not software code.

a. To the extent that the final model’s software code includes generally commercially available software that is not owned by you, but that can be procured by the Competition Sponsor without undue expense, then instead of delivering the code for that software to the Competition Sponsor, you must identify that software, method for procuring it, and any parameters or other information necessary to replicate the winning Submission; Individual Participants and Teams who create a Submission using an AMLT may win a Prize. However, for clarity, the potential winner’s Submission must still meet the requirements of these Rules, including but not limited to Section 2.5 (Winners License), Section 2.8 (Winners Obligations), and Section 3.14 (Warranty, Indemnity, and Release).” </h6>

b. Individual Participants and Teams who create a Submission using an AMLT may win a Prize. However, for clarity, the potential winner’s Submission must still meet the requirements of these Rules,</h6>

2. Grant to the Competition Sponsor the license to the winning Submission stated in the Competition Specific Rules above, and represent that you have the unrestricted right to grant that license;

3. Sign and return all Prize acceptance documents as may be required by Competition Sponsor or Kaggle, including without limitation: (a) eligibility certifications; (b) licenses, releases and other agreements required under the Rules; and (c) U.S. tax forms (such as IRS Form W-9 if U.S. resident, IRS Form W-8BEN if foreign resident, or future equivalents).

####9. GOVERNING LAW

a. Unless otherwise provided in the Competition Specific Rules above, all claims arising out of or relating to these Rules will be governed by California law, excluding its conflict of laws rules, and will be litigated exclusively in the Federal or State courts of Santa Clara County, California, USA. The parties consent to personal jurisdiction in those courts. If any provision of these Rules is held to be invalid or unenforceable, all remaining provisions of the Rules will remain in full force and effect.


---

# Page: abstract

Five banks, one shared enemy: build a federated model that catches fraud and network intrusions without ever pooling customer data, then find out what happens when one of your "banks" turns malicious.


---

# Page: foundational-rules

The following Kaggle Competition Foundational Rules (“ Foundational Rules ”) apply to every competition regardless of whether the Sponsor creates competition-specific rules. Any competition-specific rules provided by the Sponsor are in addition to these rules, and in the case of any conflict or inconsistency, these Foundational Rules control and nullify contrary competition-specific rules.
###GENERAL COMPETITION RULES - BINDING AGREEMENT
####1. ELIGIBILITY
a. To be eligible to enter the Competition, you must be:</h5>
1. a registered account holder at Kaggle.com; </h6>
2. the older of 18 years old or the age of majority in your jurisdiction of residence (unless otherwise agreed to by Competition Sponsor and appropriate parental/guardian consents have been obtained by Competition Sponsor); </h6>
3. not a resident of Crimea, so-called Donetsk People's Republic (DNR) or Luhansk People's Republic (LNR), Cuba, Iran, or North Korea; and</h6>
4. not a person or representative of an entity under U.S. export controls or sanctions (see: [https://www.treasury.gov/resourcecenter/sanctions/Programs/Pages/Programs.aspx][1]).</h6>

b. Competitions are open to residents of the United States and worldwide, except that if you are a resident of Crimea, so-called Donetsk People's Republic (DNR) or Luhansk People's Republic (LNR), Cuba, Iran, North Korea, or are subject to U.S. export controls or sanctions, you may not enter the Competition. Other local rules and regulations may apply to you, so please check your local laws to ensure that you are eligible to participate in skills-based competitions. The Competition Host reserves the right to forego or award alternative Prizes where needed to comply with local laws. If a winner is located in a country where prizes cannot be awarded, then they are not eligible to receive a prize.</h5>

c. If you are entering as a representative of a company, educational institution or other legal entity, or on behalf of your employer, these rules are binding on you, individually, and the entity you represent or where you are an employee. If you are acting within the scope of your employment, or as an agent of another party, you warrant that such party or your employer has full knowledge of your actions and has consented thereto, including your potential receipt of a Prize. You further warrant that your actions do not violate your employer's or entity's policies and procedures.</h5>   

d. The Competition Sponsor reserves the right to verify eligibility and to adjudicate on any dispute at any time. If you provide any false information relating to the Competition concerning your identity, residency, mailing address, telephone number, email address, ownership of right, or information required for entering the Competition, you may be immediately disqualified from the Competition.</h5>

####2. SPONSOR AND HOSTING PLATFORM

a. The Competition is sponsored by Competition Sponsor named above. The Competition is hosted on behalf of Competition Sponsor by Kaggle Inc. ("Kaggle"). Kaggle is an independent contractor of Competition Sponsor, and is not a party to this or any agreement between you and Competition Sponsor. You understand that Kaggle has no responsibility with respect to selecting the potential Competition winner(s) or awarding any Prizes. Kaggle will perform certain administrative functions relating to hosting the Competition, and you agree to abide by the provisions relating to Kaggle under these Rules. As a Kaggle.com account holder and user of the Kaggle competition platform, remember you have accepted and are subject to the Kaggle Terms of Service at [www.kaggle.com/terms][2] in addition to these Rules.</h5>

####3. COMPETITION PERIOD
a. For the purposes of Prizes, the Competition will run from the Start Date and time to the Final Submission Deadline (such duration the “Competition Period”). The Competition Timeline is subject to change, and Competition Sponsor may introduce additional hurdle deadlines during the Competition Period. Any updated or additional deadlines will be publicized on the Competition Website. It is your responsibility to check the Competition Website regularly to stay informed of any deadline changes. YOU ARE RESPONSIBLE FOR DETERMINING THE CORRESPONDING TIME ZONE IN YOUR LOCATION.</h5>

####4. COMPETITION ENTRY
a. NO PURCHASE NECESSARY TO ENTER OR WIN. To enter the Competition, you must register on the Competition Website prior to the Entry Deadline, and follow the instructions for developing and entering your Submission through the Competition Website. Your Submissions must be made in the manner and format, and in compliance with all other requirements, stated on the Competition Website (the "Requirements"). Submissions must be received before any Submission deadlines stated on the Competition Website. Submissions not received by the stated deadlines will not be eligible to receive a Prize.</h5>
b. Submissions may not use or incorporate information from hand labeling or human prediction of the validation dataset or test data records.</h5>
c. If the Competition is a multi-stage competition with temporally separate training and/or test data, one or more valid Submissions may be required during each Competition stage in the manner described on the Competition Website in order for the Submissions to be Prize eligible.</h5>
d. Submissions are void if they are in whole or part illegible, incomplete, damaged, altered, counterfeit, obtained through fraud, or late. Competition Sponsor reserves the right to disqualify any entrant who does not follow these Rules, including making a Submission that does not meet the Requirements. </h5>

####5. INDIVIDUALS AND TEAMS
a. Individual Account. You may make Submissions only under one, unique Kaggle.com account. You will be disqualified if you make Submissions through more than one Kaggle account, or attempt to falsify an account to act as your proxy. You may submit up to the maximum number of Submissions per day as specified on the Competition Website. </h5>
b. Teams. If permitted under the Competition Website guidelines, multiple individuals may collaborate as a Team; however, you may join or form only one Team. Each Team member must be a single individual with a separate Kaggle account. You must register individually for the Competition before joining a Team. You must confirm your Team membership to make it official by responding to the Team notification message sent to your Kaggle account. Team membership may not exceed the Maximum Team Size stated on the Competition Website.</h5>
c. Team Merger. Teams may request to merge via the Competition Website. Team mergers may be allowed provided that: (i) the combined Team does not exceed the Maximum Team Size; (ii) the number of Submissions made by the merging Teams does not exceed the number of Submissions permissible for one Team at the date of the merger request; (iii) the merger is completed before the earlier of: any merger deadline or the Competition deadline; and (iv) the proposed combined Team otherwise meets all the requirements of these Rules. </h5>
d. Private Sharing. No private sharing outside of Teams. Privately sharing code or data outside of Teams is not permitted. It's okay to share code if made available to all Participants on the forums.</h5>

####6. SUBMISSION CODE REQUIREMENTS
a. Private Code Sharing. Unless otherwise specifically permitted under the Competition Website or Competition Specific Rules above, during the Competition Period, you are not allowed to privately share source or executable code developed in connection with or based upon the Competition Data or other source or executable code relevant to the Competition (“Competition Code”). This prohibition includes sharing Competition Code between separate Teams, unless a Team merger occurs. Any such sharing of Competition Code is a breach of these Competition Rules and may result in disqualification.</h5>
b. Public Code Sharing. You are permitted to publicly share Competition Code, provided that such public sharing does not violate the intellectual property rights of any third party. If you do choose to share Competition Code or other such code, you are required to share it on Kaggle.com on the discussion forum or notebooks associated specifically with the Competition for the benefit of all competitors. By so sharing, you are deemed to have licensed the shared code under an Open Source Initiative-approved license (see [www.opensource.org][3]) that in no event limits commercial use of such Competition Code or model containing or depending on such Competition Code.</h5>
c. Use of Open Source. Unless otherwise stated in the Specific Competition Rules above, if open source code is used in the model to generate the Submission, then you must only use open source code licensed under an Open Source Initiative-approved license (see [www.opensource.org][4]) that in no event limits commercial use of such code or model containing or depending on such code.</h5>

####7. DETERMINING WINNERS
a. Each Submission will be scored and ranked by the evaluation metric stated on the Competition Website. During the Competition Period, the current ranking will be visible on the Competition Website's Public Leaderboard. The potential winner(s) are determined solely by the leaderboard ranking on the Private Leaderboard, subject to compliance with these Rules. The Public Leaderboard will be based on the public test set and the Private Leaderboard will be based on the private test set.</h5>
b. In the event of a tie, the Submission that was entered first to the Competition will be the winner. In the event a potential winner is disqualified for any reason, the Submission that received the next highest score rank will be chosen as the potential winner.</h5>

####8. NOTIFICATION OF WINNERS & DISQUALIFICATION
a. The potential winner(s) will be notified by email.</h5> 
b. If a potential winner (i) does not respond to the notification attempt within one (1) week from the first notification attempt or (ii) notifies Kaggle within one week after the Final Submission Deadline that the potential winner does not want to be nominated as a winner or does not want to receive a Prize, then, in each case (i) and (ii) such potential winner will not receive any Prize, and an alternate potential winner will be selected from among all eligible entries received based on the Competition’s judging criteria.</h5>
c. In case (i) and (ii) above Kaggle may disqualify the Participant.  However, in case (ii) above, if requested by Kaggle, such potential winner may provide code and documentation to verify the Participant’s compliance with these Rules. If the potential winner provides code and documentation to the satisfaction of Kaggle, the Participant will not be disqualified pursuant to this paragraph.</h5>
d. Competition Sponsor reserves the right to disqualify any Participant from the Competition if the Competition Sponsor reasonably believes that the Participant has attempted to undermine the legitimate operation of the Competition by cheating, deception, or other unfair playing practices or abuses, threatens or harasses any other Participants, Competition Sponsor or Kaggle.</h5>
e. A disqualified Participant may be removed from the Competition leaderboard, at Kaggle's sole discretion. If a Participant is removed from the Competition Leaderboard, additional winning features associated with the Kaggle competition platform, for example Kaggle points or medals, may also not be awarded.</h5>
f. The final leaderboard list will be publicly displayed at Kaggle.com. Determinations of Competition Sponsor are final and binding.</h5>

####9. PRIZES
a. Prize(s) are as described on the Competition Website and are only available for winning during the time period described on the Competition Website. The odds of winning any Prize depends on the number of eligible Submissions received during the Competition Period and the skill of the Participants. </h5>
b. All Prizes are subject to Competition Sponsor's review and verification of the Participant’s eligibility and compliance with these Rules, and the compliance of the winning Submissions with the Submissions Requirements. In the event that the Submission demonstrates non-compliance with these Competition Rules, Competition Sponsor may at its discretion take either of the following actions: (i) disqualify the Submission(s); or (ii) require the potential winner to remediate within one week after notice all issues identified in the Submission(s) (including, without limitation, the resolution of license conflicts, the fulfillment of all obligations required by software licenses, and the removal of any software that violates the software restrictions).</h5>
c. A potential winner may decline to be nominated as a Competition winner in accordance with Section 3.8.</h5>
d. Potential winners must return all required Prize acceptance documents within two (2) weeks following notification of such required documents, or such potential winner will be deemed to have forfeited the prize and another potential winner will be selected. Prize(s) will be awarded within approximately thirty (30) days after receipt by Competition Sponsor or Kaggle of the required Prize acceptance documents. Transfer or assignment of a Prize is not allowed. </h5>
e. You are not eligible to receive any Prize if you do not meet the Eligibility requirements in Section 2.7 and Section 3.1 above.</h5>
f. If a Team wins a monetary Prize, the Prize money will be allocated in even shares between the eligible Team members, unless the Team unanimously opts for a different Prize split and notifies Kaggle before Prizes are issued.</h5>

####10. TAXES
a. ALL TAXES IMPOSED ON PRIZES ARE THE SOLE RESPONSIBILITY OF THE WINNERS. Payments to potential winners are subject to the express requirement that they submit all documentation requested by Competition Sponsor or Kaggle for compliance with applicable state, federal, local and foreign (including provincial) tax reporting and withholding requirements. Prizes will be net of any taxes that Competition Sponsor is required by law to withhold. If a potential winner fails to provide any required documentation or comply with applicable laws, the Prize may be forfeited and Competition Sponsor may select an alternative potential winner. Any winners who are U.S. residents will receive an IRS Form-1099 in the amount of their Prize.</h5>

####11. GENERAL CONDITIONS
a. All federal, state, provincial and local laws and regulations apply.</h5>

####12. PUBLICITY
a. You agree that Competition Sponsor, Kaggle and its affiliates may use your name and likeness for advertising and promotional purposes without additional compensation, unless prohibited by law.</h5>

####13. PRIVACY
a. You acknowledge and agree that Competition Sponsor and Kaggle may collect, store, share and otherwise use personally identifiable information provided by you during the Kaggle account registration process and the Competition, including but not limited to, name, mailing address, phone number, and email address (“Personal Information”). Kaggle acts as an independent controller with regard to its collection, storage, sharing, and other use of this Personal Information, and will use this Personal Information in accordance with its Privacy Policy <[www.kaggle.com/privacy][6]>, including for administering the Competition. As a Kaggle.com account holder, you have the right to request access to, review, rectification, portability or deletion of any personal data held by Kaggle about you by logging into your account and/or contacting Kaggle Support at <[www.kaggle.com/contact][7]>.</h5>
b. As part of Competition Sponsor performing this contract between you and the Competition Sponsor, Kaggle will transfer your Personal Information to Competition Sponsor, which acts as an independent controller with regard to this Personal Information. As a controller of such Personal Information, Competition Sponsor agrees to comply with all U.S. and foreign data protection obligations with regard to your Personal Information. Kaggle will transfer your Personal Information to Competition Sponsor in the country specified in the Competition Sponsor Address listed above, which may be a country outside the country of your residence. Such country may not have privacy laws and regulations similar to those of the country of your residence.</h5>

####14. WARRANTY, INDEMNITY AND RELEASE 
a. You warrant that your Submission is your own original work and, as such, you are the sole and exclusive owner and rights holder of the Submission, and you have the right to make the Submission and grant all required licenses.  You agree not to make any Submission that: (i) infringes any third party proprietary rights, intellectual property rights, industrial property rights, personal or moral rights or any other rights, including without limitation, copyright, trademark, patent, trade secret, privacy, publicity or confidentiality obligations, or defames any person; or (ii) otherwise violates any applicable U.S. or foreign state or federal law.</h5>
b. To the maximum extent permitted by law, you indemnify and agree to keep indemnified Competition Entities at all times from and against any liability, claims, demands, losses, damages, costs and expenses resulting from any of your acts, defaults or omissions and/or a breach of any warranty set forth herein. To the maximum extent permitted by law, you agree to defend, indemnify and hold harmless the Competition Entities from and against any and all claims, actions, suits or proceedings, as well as any and all losses, liabilities, damages, costs and expenses (including reasonable attorneys fees) arising out of or accruing from: (a) your Submission or other material uploaded or otherwise provided by you that infringes any third party proprietary rights, intellectual property rights, industrial property rights, personal or moral rights or any other rights, including without limitation, copyright, trademark, patent, trade secret, privacy, publicity or confidentiality obligations, or defames any person; (b) any misrepresentation made by you in connection with the Competition; (c) any non-compliance by you with these Rules or any applicable U.S. or foreign state or federal law; (d) claims brought by persons or entities other than the parties to these Rules arising from or related to your involvement with the Competition; and (e) your acceptance, possession, misuse or use of any Prize, or your participation in the Competition and any Competition-related activity.</h5>
c. You hereby release Competition Entities from any liability associated with: (a) any malfunction or other problem with the Competition Website; (b) any error in the collection, processing, or retention of any Submission; or (c) any typographical or other error in the printing, offering or announcement of any Prize or winners.</h5>

####15. INTERNET
a. Competition Entities are not responsible for any malfunction of the Competition Website or any late, lost, damaged, misdirected, incomplete, illegible, undeliverable, or destroyed Submissions or entry materials due to system errors, failed, incomplete or garbled computer or other telecommunication transmission malfunctions, hardware or software failures of any kind, lost or unavailable network connections, typographical or system/human errors and failures, technical malfunction(s) of any telephone network or lines, cable connections, satellite transmissions, servers or providers, or computer equipment, traffic congestion on the Internet or at the Competition Website, or any combination thereof, which may limit a Participant’s ability to participate.</h5>

####16. RIGHT TO CANCEL, MODIFY OR DISQUALIFY
a. If for any reason the Competition is not capable of running as planned, including infection by computer virus, bugs, tampering, unauthorized intervention, fraud, technical failures, or any other causes which corrupt or affect the administration, security, fairness, integrity, or proper conduct of the Competition, Competition Sponsor reserves the right to cancel, terminate, modify or suspend the Competition. Competition Sponsor further reserves the right to disqualify any Participant who tampers with the submission process or any other part of the Competition or Competition Website.  Any attempt by a Participant to deliberately damage any website, including the Competition Website, or undermine the legitimate operation of the Competition is a violation of criminal and civil laws. Should such an attempt be made, Competition Sponsor and Kaggle each reserves the right to seek damages from any such Participant to the fullest extent of the applicable law.</h5>

####17. NOT AN OFFER OR CONTRACT OF EMPLOYMENT
a. Under no circumstances will the entry of a Submission, the awarding of a Prize, or anything in these Rules be construed as an offer or contract of employment with Competition Sponsor or any of the Competition Entities. You acknowledge that you have submitted your Submission voluntarily and not in confidence or in trust. You acknowledge that no confidential, fiduciary, agency, employment or other similar relationship is created between you and Competition Sponsor or any of the Competition Entities by your acceptance of these Rules or your entry of your Submission.</h5>

####18. DEFINITIONS
a. "Competition Data" are the data or datasets available from the Competition Website for the purpose of use in the Competition, including any prototype or executable code provided on the Competition Website. The Competition Data will contain private and public test sets. Which data belongs to which set will not be made available to Participants. </h5>
b. An “Entry” is when a Participant has joined, signed up, or accepted the rules of a competition. Entry is required to make a Submission to a competition.</h5>
c. A “Final Submission” is the Submission selected by the user, or automatically selected by Kaggle in the event not selected by the user, that is/are used for final placement on the competition leaderboard.</h5>
d. A “Participant” or “Participant User” is an individual who participates in a competition by entering the competition and making a Submission.</h5>
e. The “Private Leaderboard” is a ranked display of Participants’ Submission scores against the private test set. The Private Leaderboard determines the final standing in the competition.</h5>
f. The “Public Leaderboard” is a ranked display of Participants’ Submission scores against a representative sample of the test data. This leaderboard is visible throughout the competition.</h5>
g. A “Sponsor” is responsible for hosting the competition, which includes but is not limited to providing the data for the competition, determining winners, and enforcing competition rules.</h5>
h. A “Submission” is anything provided by the Participant to the Sponsor to be evaluated for competition purposes and determine leaderboard position. A Submission may be made as a model, notebook, prediction file, or other format as determined by the Sponsor.</h5>
i. A “Team” is one or more Participants participating together in a Kaggle competition, by officially merging together as a Team within the competition platform.</h5>

  [1]: https://www.treasury.gov/resource-center/sanctions/Programs/Pages/Programs.aspx
  [2]: http://www.kaggle.com/terms
  [3]: http://www.opensource.org
  [4]: http://www.opensource.org
  [5]: https://www.kaggle.com/WinningModelDocumentationGuidelines
  [6]: http://www.kaggle.com/privacy
  [7]: http://www.kaggle.com/contact



---

# Page: tracks-and-awards

This is placeholder content. This will not be displayed, but exists to satisfy launch checklist conditions.


---

# Page: Evaluation

## CAIRLab Secure AI Hackathon — Evaluation Rubric, Days 2–3 (100 points total)

Submissions are scored on four criteria: how well your approach performs, how well you
explain what you did, how you present it live, and how creatively you engaged with the
security angle. The table below is the exact breakdown every judge uses.

| Criterion | Weight | Points | What it measures |
|---|---|---|---|
| **Automated Detection Score** | 40% | 40 pts | Objective F1 improvement, measured from your own before/after comparison and verified by organizers |
| **Writeup Quality** | 30% | 30 pts | Do you understand *why* your approach works, not just that it does |
| **Live Demo & Presentation** | 20% | 20 pts | Can you explain and defend your work under questions |
| **Creativity & Security Mindset** | 10% | 10 pts | Novelty of approach, and depth of engagement with the security angle |

---

### 1. Automated Detection Score (40 points)

How this is measured depends on your track, pick the row that matches your submission.
Unlike Day 1, there's no live leaderboard for these tracks: the number comes from the
before/after comparison you report in your Writeup, on the same public held-out NSL-KDD
test split used throughout the Day 2 notebook.

| Track | Scored on | Points |
|---|---|---|
| 🟡 Intermediate | F1 improvement of your custom aggregation over the naive FedAvg baseline, on the same non-IID split | 0–40 |
| 🔴 Advanced | F1 recovered by your defense, measured as (your defended F1 − naive FedAvg-under-attack F1), on the same attack scenario | 0–40 |

Organizers verify this number independently: your GitHub repo must include your final
exported model (`model_scripted.pt`) and metrics file (`submission.json`) exactly as the
Day 2 notebook produces them. A repo missing these cannot be scored on this section,
regardless of what your Writeup reports.

If you attempted both tracks, report both comparisons in your Writeup and select
whichever is your stronger result as your primary track,  judges score your primary
track's number here, with the other mentioned as supporting work under Creativity.

### 2. Writeup Quality (30 points)

| Criteria | Points Possible |
|---|---|
| **Technical Understanding:** explains *why* the approach works (or doesn't), not just what was tried | 0–15 |
| **Clarity:** writeup is well-organized and readable by someone outside your team | 0–10 |
| **Reproducibility:** another team could re-run your notebook and get your reported numbers | 0–5 |

### 3. Live Demo & Presentation (20 points)

| Criteria | Points Possible |
|---|---|
| **Presentation quality:** clear, confident walkthrough of approach and results within the time limit | 0–10 |
| **Q&A handling:** thoughtful, honest answers to judges' questions — including "we tried X and it didn't work" | 0–10 |

### 4. Creativity & Security Mindset (10 points)

| Criteria | Points Possible |
|---|---|
| **Novelty:** approach goes beyond the obvious first idea suggested in the notebook | 0–5 |
| **Security relevance:** genuine engagement with the adversarial/security angle, not just raw model performance (this is where 🔴 Advanced-track work is expected to shine, but 🟡 Intermediate work can score here too) | 0–5 |

---

### Required Elements (Yes/No — must all be "Yes" to be eligible)

| Requirement | Yes / No |
|---|---|
| Kaggle Writeup submitted before the deadline, with Track set to Intermediate and/or Advanced | |
| Writeup is 1,500 words or fewer | |
| Writeup includes a clear before/after F1 comparison | |
| Cover image attached in Media Gallery | |
| Public Notebook (Day 2 extension) attached and runs top-to-bottom without errors | |
| Video attached, 3 minutes or less, publicly viewable | |
| Public Project Link (GitHub repo) includes `model_scripted.pt` and `submission.json`, accessible without login | |

A submission missing any "Required Element" will not be scored by judges regardless of
technical quality, please check this table yourself before you submit.


---

# Page: judges

This is placeholder content. This will not be displayed, but exists to satisfy launch checklist conditions.
