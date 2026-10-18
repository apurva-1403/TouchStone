"""Layer 7 - Baseline/noise artifacts not tied to a curated event.

~1,200 routine ServiceNow tickets (password resets, laptop issues, standard access, HR/Finance queries,
compensation and leave requests, contract reviews, security alerts...) for a 1,000-person company, and
~200 Slack conversations of ordinary chatter. Template-driven, deterministic (seeded), and every
requester/assignee is a real employee who had already joined on the ticket date.
"""
from __future__ import annotations

from common import rng, random_date, random_time, add_business_days, add_days, ts, d
from events.dsl import T, S

NOISE_START, NOISE_END = "2025-03-03", "2026-09-22"

# ---------------------------------------------------------------- assignee pools (by group)
POOLS = {
    "IT Service Desk": ["Deepak Verma", "Shruti Joshi", "Anjali Gupta"],
    "Endpoint": ["Mohammed Irfan", "Deepak Verma"],
    "IAM": ["Kavya Reddy", "Lakshmi Narayanan"],
    "Cloud Infrastructure": ["Nandini Rajan", "Siddharth Jain", "Harish Gowda"],
    "HR Ops": ["Rakesh Nair", "Ayesha Khan", "Swati Kulkarni", "Fatima Sheikh"],
    "Payroll": ["Vijay Kumar"],
    "Finance AP": ["Ramesh Babu", "Alok Mishra"],
    "Procurement": ["Kritika Jain", "Zara Ahmed"],
    "Finance Systems": ["Payal Shah"],
    "Sales Ops": ["Megha Patil"],
    "Data Engineering": ["Ananya Chatterjee", "Manish Tiwari"],
    "Platform Backend": ["Karthik Iyer", "Daniel Fernandes"],
    "Customer Success": ["Preeti Nambiar", "Kunal Shah"],
}

# Teams whose generated (EMP-101+) members also work each assignment group's queue.
GROUP_TEAMS = {
    "IT Service Desk": ["IT Service Desk & Endpoint"], "Endpoint": ["IT Service Desk & Endpoint"],
    "IAM": ["Identity & Access Management"], "Cloud Infrastructure": ["Cloud Infrastructure & Security"],
    "HR Ops": ["People Operations"], "Payroll": ["Billing, Payroll & Compliance"],
    "Finance AP": ["Accounts Payable & Procurement"], "Procurement": ["Accounts Payable & Procurement"],
    "Finance Systems": ["Financial Planning & Analysis"], "Sales Ops": ["Sales Operations & Deal Desk"],
    "Data Engineering": ["Data & Analytics Engineering"], "Platform Backend": ["Platform Backend"],
    "Customer Success": ["Customer Success & Support"], "Total Rewards": ["Total Rewards & Compensation"],
    "Commercial Legal": ["Commercial Legal"], "Security Operations": ["Security Operations"],
    "Product": ["Core Product", "Platform Product"], "IT GRC": ["IT Governance & Risk"],
}
TICKET_SCALE = 8  # routine volume multiplier for the 1,000-person company (templates below are per-100-people)

APPS = ["Salesforce", "Zendesk", "HubSpot", "Metabase", "Jira", "Confluence", "Darwinbox", "Zoho Expense", "LearnHub", "GitHub"]
SOFTWARE = ["Docker Desktop", "Postman", "DBeaver", "Adobe Acrobat Pro", "Zoom desktop client", "Python 3.12", "Node.js 22",
            "Visual Studio Code", "Figma desktop app", "OBS Studio", "Tableau Reader", "WhatsApp Desktop", "Notion", "Miro desktop"]
LAPTOP_ISSUES = [
    ("battery drains in under 2 hours", "Battery health reported at 71%; replaced battery under warranty (Apple/Lenovo service, 2 days). Loaner issued meanwhile."),
    ("keyboard - several keys (E, R, space) intermittently not registering", "Keyboard replaced under warranty; device returned in 3 business days. Loaner issued."),
    ("screen flickers when the lid is at certain angles", "Display cable fault; repaired by vendor service centre (4 days). Loaner issued."),
    ("fan runs constantly and the laptop is very hot", "Runaway process (Defender full scan stuck) and dust; cleaned, Defender re-installed, fan curve normal. No hardware fault."),
    ("charger stopped working - no light, laptop not charging", "USB-C charger faulty; replaced from stock same day."),
    ("trackpad clicks register as right-clicks", "Trackpad settings reset and firmware updated; resolved. Advised to raise again if it recurs (hardware)."),
    ("laptop randomly shuts down without warning", "Kernel panic logs pointed to a failing SSD; SSD replaced under warranty, data restored from OneDrive backup. 5 business days; loaner issued."),
    ("very slow since the last OS update - takes 5 minutes to boot", "Disk 98% full (Docker images and downloads); cleaned up 120 GB, disabled 6 login items. Boot time back to ~20s."),
    ("Wi-Fi drops every few minutes in the office but fine at home", "Stale Wi-Fi profile with old RADIUS cert; removed and re-joined AlgoWorks-Corp via Intune profile. Resolved."),
    ("external monitor not detected through the dock", "Dock firmware updated and display cable reseated; second port on the dock was dead - dock replaced from stock."),
]
PERIPHERALS = ["a second 27\" monitor", "a USB-C dock", "an external keyboard and mouse", "a noise-cancelling headset for customer calls",
               "a laptop stand and external keyboard (ergonomic)", "a webcam (built-in one is failing)", "an HDMI adapter for the meeting rooms"]
SPACES = ["the Finance Confluence space", "the SALES Confluence space", "the ENG Confluence space", "the HR-Restricted Confluence space",
          "the 'Customer Contracts' SharePoint site", "the 'Board Pack' SharePoint library", "the 'Marketing Assets' SharePoint site",
          "the Jira SUP project", "the Jira PLAT project (view only)", "the Jira MKT project", "the Metabase 'Support Metrics' collection",
          "the Metabase 'Finance Reporting' collection", "the algoworks-docs GitHub repo", "the 'Sales Enablement' Confluence space"]
ROOMS = ["Falcon (3rd floor)", "Heron (2nd floor)", "AlgoWorks (4th floor boardroom)", "Osprey (3rd floor)", "Kite (Pune, 1st floor)", "Eagle (Hyderabad)"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
VENDORS = ["Pixelcraft Studio", "TalentBridge Consulting", "CloudNine Facilities", "Zenith Office Supplies", "BrightWave Events", "Nexus Print Solutions"]


def _emp_filter(reg, *, depts=None, exclude_depts=None, tiers=None):
    def ok(e):
        if e["status"] == "exited":
            return False
        code = reg.by_id[e["department_id"]]["code"]
        if depts and code not in depts:
            return False
        if exclude_depts and code in exclude_depts:
            return False
        if tiers and e["tier"] not in tiers:
            return False
        return True
    return [e for e in reg.employees if ok(e)]


def _pick_person(r, reg, candidates, date, exclude=()):
    pool = [e for e in candidates if e["join_date"] <= date and e["name"] not in exclude
            and not (e.get("exit_date") and e["exit_date"] <= date)
            and not (e.get("leave_from") and e["leave_from"] <= date <= e.get("leave_until", "9999"))]
    return r.choice(pool)["name"]


def _pick_assignee(r, reg, group, date):
    names = list(POOLS.get(group, []))
    teams = set(GROUP_TEAMS.get(group, []))
    names += [e["name"] for e in reg.employees if int(e["employee_id"][4:]) > 100 and e["employment_type"] == "employee"
              and e["tier"] == "ic" and reg.by_id[e["team_id"]]["name"] in teams]
    pool = [n for n in names if reg.emp(n)["join_date"] <= date and reg.emp(n)["status"] != "exited"
            and not (reg.emp(n).get("exit_date") and reg.emp(n)["exit_date"] <= date)
            and not (reg.emp(n).get("leave_from") and reg.emp(n)["leave_from"] <= date <= reg.emp(n).get("leave_until", "9999"))]
    return r.choice(pool)


# ---------------------------------------------------------------- ticket templates
# Each: (count, kind, category, group, requester_filter_kwargs, priority, resolve_days (lo, hi), sensitivity, builder)
# builder(r, first_name, ctx) -> (subject, description, resolution)

def t_password(r, first, ctx):
    app = r.choice(["Okta", "Okta", "Okta", "my laptop (macOS login)", "my laptop (Windows login)"])
    v = r.choice([
        (f"Locked out of {app} after too many attempts",
         f"I've locked myself out of {app} after mistyping the new password a few times. I need to get back in for a customer call at {r.choice(['11:00', '14:30', '16:00'])}.",
         "Verified identity (video call + manager name check), unlocked the account and sent a password reset link. User reminded that Okta self-service unlock works if a second factor is enrolled."),
        (f"Password reset needed - {app}",
         f"Forgot my {app} password after returning from leave. Self-service reset isn't offering me the option.",
         "Self-service was blocked because only one factor was enrolled. Reset the password after identity verification and helped the user enrol Touch ID as a second factor."),
        ("Okta asks me to change my password but the new one is rejected",
         "Every password I try is rejected with 'does not meet requirements' even at 16 characters. The rules aren't shown.",
         "Password contained the user's surname, which the policy blocks (Password & MFA Standard 1.2). Explained the rules; user set a compliant passphrase."),
    ])
    return v


def t_mfa(r, first, ctx):
    return r.choice([
        ("New phone - need to move Okta Verify",
         "I've got a new phone and Okta Verify on the old one is gone (factory reset). I can't log in to anything.",
         "Identity verified via video call; reset the Okta Verify factor and guided enrolment on the new phone. Advised enrolling a second factor (Touch ID) to allow self-service next time."),
        ("Okta Verify keeps asking for number matching but shows no numbers",
         "Since the app update, the push prompt says 'select the number' but no numbers appear on the login screen.",
         "Okta Verify was two versions behind on the phone; updated via the app store and re-tested. Working."),
        ("Lost phone - please block Okta Verify",
         "My phone was stolen last night. Please remove it as an MFA device and make sure nobody can use it to log in.",
         "Okta Verify factor reset and all sessions revoked immediately; Intune selective wipe issued to the Outlook/Teams managed apps. New factor enrolled on replacement phone the next day."),
    ])


def t_laptop_hw(r, first, ctx):
    issue, fix = r.choice(LAPTOP_ISSUES)
    dev = r.choice(["MacBook Pro", "MacBook Air", "ThinkPad T14"])
    vendor = "Apple" if dev.startswith("MacBook") else "Lenovo"
    return (f"Laptop issue: {issue} ({dev})",
            f"My {dev} has developed a problem: {issue}. Started {r.choice(['yesterday', 'last week', 'a few days ago', 'this morning'])}. "
            f"I've restarted it {r.choice(['twice', 'a few times'])} with no change.",
            fix.replace("Apple/Lenovo service", f"{vendor} service"))


def t_peripheral(r, first, ctx):
    item = r.choice(PERIPHERALS)
    needs_approval = "second" in item
    return (f"Request: {item}",
            f"Could I get {item} for my desk on {r.choice(['floor 3', 'floor 2', 'floor 4', 'the Pune office', 'the Hyderabad office'])}? "
            + (f"{r.choice(['My manager has approved.', 'Manager approval attached.'])}" if needs_approval else "The standard one from stock is fine."),
            ("Manager approval recorded (second monitors require it per the Laptop SOP section 5). " if needs_approval else "No approval needed for standard peripherals. ")
            + f"Issued from stock and asset-tagged; collected from the Service Desk {r.choice(['same day', 'next morning'])}.")


def t_software(r, first, ctx):
    sw = r.choice(SOFTWARE)
    return (f"Software install: {sw}",
            f"Please install {sw} on my laptop - it needs admin rights which I don't have. Needed for {r.choice(['a customer demo', 'the current sprint', 'a training course', 'the AOP model', 'design reviews', 'API testing'])}.",
            r.choice([
                f"{sw} is in the Company Portal self-service catalogue - guided the user to install it from there (no admin needed). Closed.",
                f"Installed {sw} remotely via Intune; licence not required. Closed.",
                f"{sw} added to the Intune app catalogue after a quick security check and deployed to the user. Closed.",
            ]))


def t_admin_rights(r, first, ctx):
    return ("Local admin rights on laptop (engineering)",
            f"Requesting local admin on my MacBook - I need to install and manage Docker, Homebrew packages and local Kubernetes for {r.choice(['the v4 work', 'the portal build', 'data pipeline development', 'the mobile toolchain'])}. Manager approval on the ticket.",
            "Manager approval verified. Added to the Intune 'Engineering - Local Admin' group (admin via Privileges app, 30-minute elevation). Reminder about the endpoint compliance baseline. Closed.")


def t_channel(r, first, ctx):
    what = r.choice([
        ("Private Slack channel", f"#{r.choice(['proj-aop-fy27', 'hiring-panel-eng', 'vendor-review-2026', 'offsite-planning', 'sec-audit-prep', 'renewals-q3'])}",
         "Private channel created with the requested members; requester set as channel manager."),
        ("Microsoft 365 group / distribution list", f"{r.choice(['apac-sales', 'pune-office', 'hyderabad-all', 'campus-hires-2026', 'mkt-agency-contacts', 'finance-close'])}@algoworks.io",
         "Distribution list created in Exchange Online; owner set to requester; members added."),
        ("Slack Connect channel with a vendor", f"#{r.choice(['ext-talentbridge', 'ext-brightwave', 'ext-cloudnine'])}",
         "Slack Connect invitation sent and accepted; channel restricted to AlgoWorks-side file sharing."),
    ])
    return (f"{what[0]}: {what[1]}",
            f"Please create a {what[0]} - {what[1]} - for {r.choice(['a project', 'a hiring panel', 'a vendor engagement', 'the office team', 'a working group'])}. Members list attached. Manager approval on the ticket.",
            what[2])


def t_printer(r, first, ctx):
    return (f"Printer on {r.choice(['floor 3', 'floor 2', 'floor 4', 'Pune office'])} {r.choice(['jammed', 'offline', 'printing blank pages', 'not showing in the print dialog'])}",
            f"The printer near {r.choice(['the pantry', 'the meeting rooms', 'Finance', 'reception'])} is {r.choice(['jammed and showing an error', 'offline for everyone', 'printing blank pages', 'missing from my print dialog'])}. Need to print {r.choice(['vendor contracts', 'candidate documents', 'a customer PO', 'visa paperwork'])}.",
            r.choice(["Cleared the jam and replaced the toner; print queue restarted.",
                      "Printer had lost its static IP after the controller update; re-assigned and re-published via Intune. Working.",
                      "Re-added the printer via the Company Portal printer profile on the user's laptop; explained the Follow-Me print badge."]))


def t_vpn(r, first, ctx):
    return r.choice([
        ("VPN won't connect after macOS update",
         "After updating macOS last night GlobalProtect says 'could not connect to gateway'. Worked fine yesterday.",
         "macOS update disabled the GlobalProtect system extension; re-enabled it in System Settings > General > Login Items & Extensions and rebooted. Connected."),
        ("VPN very slow - Metabase takes ages to load",
         "GlobalProtect is connected but everything internal is crawling. Speed test outside VPN is fine.",
         "User was on the full-tunnel profile from a previous travel request; switched back to split-tunnel. Speeds normal."),
        ("GlobalProtect stuck on 'Connecting' forever",
         "The GlobalProtect client has been spinning on 'Connecting...' since this morning; quitting and reopening doesn't help.",
         "Stale portal cache; ran the client's 'Refresh Connection' and cleared PanGPS logs, then reconnected. Also updated client to 6.3.2."),
    ])


def t_email(r, first, ctx):
    return r.choice([
        ("Mailbox full - cannot send or receive",
         "Outlook says my mailbox is over the 50 GB limit and I'm bouncing emails. Most of it is old attachments.",
         "Enabled the online archive (auto-archive policy: items older than 2 years) which freed 30 GB overnight. Explained the retention policy."),
        ("Calendar not syncing between Outlook and phone",
         "Meetings I accept on my laptop don't show on my phone calendar, and vice versa, since last week.",
         "Outlook mobile had lost its Intune registration; re-registered via Company Portal, calendar synced within 15 minutes."),
        ("Legitimate email stuck in quarantine",
         f"An email from {r.choice(VENDORS)} with a contract attachment went to quarantine. It's genuine - please release it.",
         "Sender verified with the requester; message released from Defender quarantine and the vendor domain added to the allow list after Security review."),
        ("Need access to a shared calendar",
         f"Please give me access to the '{r.choice(['Sales Leadership', 'Meeting Rooms - Floor 3', 'Marketing Events', 'CS On-call'])}' shared calendar.",
         "Owner approved; delegated 'Reviewer' permission on the shared calendar. Visible in Outlook after restart."),
        ("Emails to a customer bouncing",
         "Every email I send to a customer's domain bounces with 'message rejected by recipient server'. Other colleagues can email them.",
         "The user's mailbox had a stale auto-forward rule created during a phishing test that triggered the recipient's DMARC policy; removed the rule, delivery restored."),
    ])


def t_access_std(r, first, ctx):
    space = r.choice(SPACES)
    return (f"Access request: {space}",
            f"Could I get access to {space}? I need it for {r.choice(['a project I have joined', 'the quarterly review', 'the audit preparation', 'a customer escalation', 'the AOP work', 'the campaign plan'])}. "
            f"Manager {r.choice(['has approved', 'approval attached', 'is copied'])}.",
            r.choice(["Manager approval recorded; owner of the space/collection approved; access granted via the corresponding Okta group. Closed within SLA.",
                      "Approved by manager; space owner added the user directly. Closed.",
                      "Manager approval recorded. Added to the group; user confirmed access."]))


def t_onboarding_misc(r, first, ctx):
    return r.choice([
        ("ID card not working on the floor 3 doors",
         "My ID card opens the main entrance but not the floor 3 doors since I moved teams.",
         "Access group updated in the door controller for the new floor; working within the hour."),
        ("Desk allocation for a new joiner",
         "My new team member starts Monday - please allocate a desk near the team on floor 3 and a locker.",
         "Desk 3-42 and locker L-118 allocated; noted on the onboarding ticket."),
        ("Name spelling wrong in email address and Slack",
         "My surname is misspelled in my email address and Slack display name (came from the HR record).",
         "Corrected in Darwinbox (HR Ops), which synced to Okta; email alias updated with the old address kept as a secondary alias. Slack display name refreshed."),
        ("Parking access for the Bengaluru office",
         "Requesting a two-wheeler parking pass for the basement.",
         "Pass issued by Facilities (basement B1, slot range T-201 to T-260); RFID tag added to the ID card."),
        ("Employee ID number needed for the bank",
         "The bank needs my employee ID and an employment letter for a salary account.",
         "Employee ID is on the Darwinbox profile; employment verification letter generated from Darwinbox letters module and emailed."),
    ])


def t_hr(r, first, ctx):
    return r.choice([
        (f"Payslip query - {r.choice(MONTHS)} payslip shows a different HRA amount",
         "My HRA on this month's payslip is lower than last month. I haven't changed my declarations.",
         "The investment declaration window closed and the proof was not uploaded, so HRA exemption was recalculated. Proof uploaded now; adjustment in next month's payroll."),
        ("PF / UAN details not visible in Darwinbox",
         "I can't see my UAN or PF contributions in Darwinbox; I need them for a transfer from my previous employer.",
         "UAN linked in Keka but the Darwinbox field mapping was empty; Payroll updated the record. PF passbook link shared."),
        ("Form 16 for the last financial year",
         "Where do I download Form 16? I need it to file my return.",
         "Form 16 is published in Darwinbox > Documents > Tax by 15 June each year. Link shared; document confirmed available."),
        ("Address change and new bank account",
         "I've moved and changed my salary bank account - how do I update both?",
         "Address updated via Darwinbox self-service (proof uploaded). Bank change requires the cancelled cheque upload and takes effect from the next payroll cut-off (20th); confirmed."),
        ("Leave balance looks wrong after my transfer",
         "After moving from Pune to Bengaluru my PL balance dropped by 3 days in Darwinbox.",
         "Location transfer re-applied the Pune holiday calendar difference; HR Ops corrected the balance manually and logged a Darwinbox support case."),
        ("Employment verification / visa letter",
         f"I need an employment letter for a {r.choice(['Schengen', 'US B1', 'UK', 'Singapore'])} visa application, addressed to the consulate.",
         "Letter generated from the Darwinbox letters module (visa template), signed by HR Ops and emailed as PDF within one business day."),
    ])


def t_finance(r, first, ctx):
    return r.choice([
        ("Expense claim status - submitted 3 weeks ago",
         f"My claim for {r.choice(['the Chennai customer visit', 'team lunch', 'the conference registration', 'a client dinner'])} was approved by my manager three weeks ago but hasn't been paid.",
         "Claim was approved by the manager after the payroll cut-off (20th), so it moves to the next run. Confirmed it is in the current run."),
        (f"Vendor payment status - {r.choice(VENDORS)} invoice",
         f"{r.choice(VENDORS)} are chasing payment of an invoice from last month. PO was raised; where is it?",
         "Invoice was received without the PO number and returned to the vendor per the Vendor SOP; vendor re-issued and it is in this Wednesday's payment run. Requester and vendor informed."),
        ("PO status - waiting for approval",
         f"My purchase request for {r.choice(['event sponsorship', 'training seats', 'office chairs', 'a marketing tool renewal'])} has been 'pending approval' for a week.",
         "Stuck at Department Head approval; reminder sent and approved the same day. PO issued."),
        ("Corporate card limit increase for a conference",
         "I'm running the booth at a logistics expo next month and need the card limit raised from Rs 2 lakh to Rs 5 lakh for the period.",
         "Temporary increase to Rs 5,00,000 for 30 days approved by Finance AP with CFO visibility; reverts automatically."),
        ("GST invoice needed for an expense",
         "The hotel invoice I uploaded doesn't have our GSTIN; Zoho flagged it. What do I do?",
         "Hotel re-issued the invoice with AlgoWorks's GSTIN (details shared); claim re-submitted and approved."),
    ])


def t_facilities(r, first, ctx):
    room = r.choice(ROOMS)
    return r.choice([
        (f"AC too cold on {r.choice(['floor 3 east', 'floor 2', 'floor 4'])}",
         "The AC near the window desks is set very low - people are wearing jackets. Can Facilities adjust it?",
         "Facilities adjusted the zone setpoint from 20 to 23 degrees; ticket kept open two days to confirm."),
        (f"Meeting room {room} - screen / video not working",
         f"The screen in {room} won't detect laptops and the Zoom Room controller is frozen.",
         "Zoom Room controller restarted and HDMI switcher power-cycled; firmware updated after hours. Working."),
        ("Broken office chair",
         "The height adjustment on my chair has failed and it sinks every few minutes.",
         "Chair swapped from Facilities stock; broken one sent for repair."),
    ])


def t_mobile(r, first, ctx):
    return r.choice([
        ("Company mobile for on-call",
         "I've joined the Cloud on-call rotation and need a company phone with PagerDuty per the On-Call policy. Manager approval attached.",
         "Department Head approval recorded; iPhone issued from stock, enrolled in Intune (full device management), PagerDuty and Okta Verify configured."),
        ("eSIM activation on company phone",
         "My company iPhone's eSIM stopped working after a carrier update - no signal.",
         "Carrier re-provisioned the eSIM; QR code installed via Intune-managed profile. Signal restored."),
    ])


def t_crm_misc(r, first, ctx):
    return r.choice([
        ("Salesforce dashboard not refreshing",
         "The 'APAC Pipeline' dashboard shows last week's numbers even after clicking Refresh.",
         "Dashboard was set to refresh as a user who left; changed the running user to the Sales Ops integration user. Refreshing correctly."),
        ("Need a Salesforce list view shared with my team",
         "Can my 'Renewals next 90 days' list view be shared with the whole CS team?",
         "List view sharing changed to the 'Customer Success' public group by the Salesforce Administrator."),
        ("Zendesk macro request",
         "Please add a macro for the 'driver app update instructions' reply - we type it 10 times a day.",
         "Macro 'Driver App - update steps' created in the Tier 1 shared macros with the approved wording from the KB article."),
    ])


def t_comp(r, first, ctx):
    return r.choice([
        ("Salary revision letter not received",
         "The annual compensation review letters went out last week but I haven't received mine in Darwinbox.",
         "Letter was generated but held for a manager sign-off that was missed; released and visible in Darwinbox > Documents. Revised CTC effective 1 April as communicated by the manager."),
        (f"Variable pay payout query - {r.choice(['Q1', 'Q2', 'H1'])}",
         f"My variable pay for the period was {r.choice(['70%', '80%', '85%'])} of target but my manager said the team hit 100%. Can you check?",
         "Payout follows the company multiplier (85%) x individual rating; calculation sheet shared privately with the employee and manager. No error found."),
        ("ESOP vesting schedule clarification",
         "My grant letter says 4-year vesting with a 1-year cliff. Does my parental leave pause vesting?",
         "Vesting continues during approved statutory leave per the ESOP plan rules (section 6.2). Confirmed in writing to the employee."),
        ("Relocation allowance - Pune to Bengaluru transfer",
         "I'm transferring to Bengaluru next month. What relocation support applies and how is it paid?",
         "One-time relocation allowance (Rs 75,000, taxable) paid with the first Bengaluru payroll plus 14 days temporary accommodation. Approved by the department head."),
    ])


def t_leave(r, first, ctx):
    return r.choice([
        ("Medical leave extension",
         "I need to extend my medical leave by two weeks following surgery; the doctor's certificate is attached.",
         "Extension approved by the manager and HR Ops; leave updated in Darwinbox and the return-to-work check-in scheduled. Certificate stored in the restricted HR file."),
        ("Maternity leave start date change",
         "My doctor has advised starting maternity leave three weeks earlier than planned. Can we change the dates?",
         "Start date moved; 26 weeks paid maternity leave unchanged. Manager informed of the new handover date; payroll notified."),
        ("Bereavement leave",
         f"{first} needs bereavement leave for a family member - please apply 5 days from Monday.",
         "5 days bereavement leave applied in Darwinbox per the Leave policy; manager informed. Condolences sent from People Ops."),
        ("Return-to-work plan after long leave",
         "Coming back from a 3-month leave next week - can we agree a phased return (4 days/week for a month)?",
         "Phased return agreed with the manager and documented; pay pro-rated for the month as per the policy."),
    ])


def t_legal(r, first, ctx):
    party = r.choice(["Ganga Freight", "SwiftHaul Logistics", "Meridian Cold Chain", "Orbit Couriers", "BlueDart Partners", "Sunrise Transport"])
    return r.choice([
        (f"NDA review - {party}",
         f"Please review the mutual NDA from {party} before the solutioning workshop next week.",
         "Reviewed: changed term from 5 to 3 years, removed the non-solicit clause; signed version filed in Ironclad."),
        (f"MSA redlines - {party}",
         f"{party} sent redlines on our MSA: liability cap at 2x fees and a 99.95% SLA credit schedule. Need Legal's position.",
         "Accepted 1.5x cap, rejected uncapped data-breach liability, offered the standard SLA credits; negotiation call held and agreed. Final MSA executed."),
        (f"Data processing agreement for {party}",
         f"{party}'s procurement needs a DPA with SCC-equivalent clauses before signature.",
         "Standard AlgoWorks DPA issued with the sub-processor list; customer accepted without changes."),
    ])


def t_security(r, first, ctx):
    return r.choice([
        ("Phishing email reported",
         f"{first} reported an email pretending to be from the CFO asking for gift cards.",
         "Confirmed phishing; sender domain blocked, 14 copies purged from mailboxes, nobody clicked. Added to the awareness newsletter."),
        ("Impossible-travel sign-in alert",
         "Okta flagged a sign-in from Frankfurt 20 minutes after a Bengaluru sign-in for the same user.",
         "User was on a corporate VPN exit node in Frankfurt; activity verified with the user, no compromise. Detection tuned for the VPN egress IPs."),
        ("Lost laptop reported",
         f"{first} lost their laptop in a cab on the way to the airport.",
         "Device remotely locked and wiped via Intune; BitLocker confirmed; replacement issued; police report filed for insurance."),
    ])


def t_product(r, first, ctx):
    return r.choice([
        ("Feature request: bulk geofence import",
         "Two enterprise customers asked for CSV import of geofences (hundreds per account). Logging for prioritisation.",
         "Added to the Maps & Geofencing backlog (Productboard insight linked to both accounts); planned for the Q4 roadmap review."),
        ("Customer feedback: driver app battery usage",
         "Field teams at a customer say the driver app drains phone batteries by mid-afternoon.",
         "Linked to the known GPS polling issue; fix shipped in driver app 5.8 (adaptive polling). Customer informed via CS."),
    ])


def t_access_review(r, first, ctx):
    return r.choice([
        (f"Quarterly access review - {r.choice(APPS)}",
         "Quarterly user access review task: confirm every user still needs access and remove leavers.",
         "Review completed by the system owner; 6 stale accounts removed; evidence attached for the ISO 27001 audit."),
    ])


TEMPLATES = [
    # (count, kind, category, group, requester filter, priority, (lo,hi) resolve days, sensitivity, builder)
    (14, "incident", "account", "IAM", {}, "P3", (0, 0), None, t_password),
    (8, "incident", "mfa", "IAM", {}, "P3", (0, 1), None, t_mfa),
    (12, "incident", "laptop", "Endpoint", {}, "P3", (0, 5), None, t_laptop_hw),
    (10, "request", "peripheral", "IT Service Desk", {}, "P4", (0, 2), None, t_peripheral),
    (10, "request", "software", "IT Service Desk", {}, "P4", (0, 2), None, t_software),
    (5, "request", "software", "Endpoint", {"depts": ["ENG", "IT"]}, "P4", (0, 1), None, t_admin_rights),
    (6, "request", "collaboration", "IT Service Desk", {"tiers": ["lead", "head"]}, "P4", (0, 1), None, t_channel),
    (4, "incident", "printer", "IT Service Desk", {}, "P4", (0, 1), None, t_printer),
    (6, "incident", "vpn", "IT Service Desk", {}, "P3", (0, 1), None, t_vpn),
    (8, "incident", "email", "IT Service Desk", {}, "P3", (0, 2), None, t_email),
    (14, "request", "access", "IAM", {}, "P3", (0, 3), None, t_access_std),
    (6, "request", "onboarding", "IT Service Desk", {}, "P4", (0, 2), None, t_onboarding_misc),
    (10, "request", "hr-query", "HR Ops", {}, "P4", (0, 3), "restricted", t_hr),
    (8, "request", "finance-query", "Finance AP", {}, "P4", (0, 4), None, t_finance),
    (5, "incident", "facilities", "IT Service Desk", {}, "P4", (0, 3), None, t_facilities),
    (3, "request", "mobile", "Endpoint", {"depts": ["IT", "ENG", "SALES"]}, "P4", (0, 3), None, t_mobile),
    (4, "request", "application", "Sales Ops", {"depts": ["SALES"]}, "P4", (0, 2), None, t_crm_misc),
    # added with the 1,000-person expansion
    (3, "request", "compensation", "Total Rewards", {}, "P4", (1, 5), None, t_comp),
    (3, "request", "leave", "HR Ops", {}, "P3", (0, 2), None, t_leave),
    (3, "request", "legal-review", "Commercial Legal", {"depts": ["SALES"]}, "P3", (2, 10), "restricted", t_legal),
    (2, "incident", "security-incident", "Security Operations", {}, "P2", (0, 2), "restricted", t_security),
    (2, "request", "product-feedback", "Product", {"depts": ["SALES"]}, "P4", (1, 10), None, t_product),
    (1, "request", "access-review", "IT GRC", {"tiers": ["lead", "head"]}, "P4", (2, 10), None, t_access_review),
]


def build_noise_tickets(reg) -> list[dict]:
    r = rng("noise-tickets")
    out = []
    for count, kind, category, group, filt, prio, (lo, hi), sens, builder in TEMPLATES:
        candidates = _emp_filter(reg, **filt)
        for _ in range(count * TICKET_SCALE):
            created = random_date(r, NOISE_START, NOISE_END)
            requester = _pick_person(r, reg, candidates, created)
            first = requester.split()[0]
            assignee = _pick_assignee(r, reg, group, created)
            if assignee == requester:
                assignee = _pick_assignee(r, reg, group, created)
            subject, desc, res = builder(r, first, {})
            days = r.randint(lo, hi)
            resolved = add_business_days(created, days) if days else created
            status = "resolved"
            # a handful of very recent tickets are still open
            if created >= "2026-09-14" and r.random() < 0.5:
                status, resolved, res = ("in_progress" if r.random() < 0.6 else "open"), None, ""
            elif r.random() < 0.85:
                status = "closed"
            # payroll queries go to Payroll rather than HR Ops
            grp = group
            if category == "hr-query" and any(k in subject.lower() for k in ("payslip", "form 16", "pf /", "bank account")):
                grp = "Payroll"
                assignee = _pick_assignee(r, reg, "Payroll", created)
            out.append(T(subject, desc, res, requester, assignee, created, status=status, resolved=resolved, group=grp,
                         priority=prio, category=category, kind=kind, sensitivity=sens))
    return out


# ---------------------------------------------------------------- Slack chatter templates
SOCIAL_CHANNELS = {"#random": None, "#food-and-chai": None, "#kudos": None, "#bengaluru-office": None, "#pune-office": ["Pune"],
                   "#hyderabad-office": ["Hyderabad"], "#general": None}


# channel -> team whose members plausibly *start* a thread there (others in the thread come from the department)
CHANNEL_TEAM = {
    "#it-helpdesk": "IT Service Desk & Endpoint", "#devops-sre": "Cloud Infrastructure & Security",
    "#eng-platform": "Platform Backend", "#eng-frontend": "Web & Mobile Frontend", "#eng-data": "Data & Analytics Engineering",
    "#eng-announcements": "Platform Backend", "#hr-announcements": "People Operations", "#people-ops": "People Operations",
    "#learning": "Learning & Development", "#sales-team": "Enterprise Sales", "#sales-ops": "Sales Operations & Deal Desk",
    "#customer-success": "Customer Success & Support", "#marketing": "Content & Brand", "#demand-gen": "Demand Generation",
    "#product-marketing": "Product Marketing", "#new-joiners": "People Operations", "#general": "People Operations",
    "#product-core": "Core Product", "#product-design": "Product Design & Research", "#legal": "Commercial Legal",
    "#compliance": "Privacy, Compliance & Audit", "#support-tier1": "Technical Support (Tier 1)",
    "#secops": "Security Operations", "#sales-apac": "APAC Sales", "#eng-mobile": "Driver Mobile Apps",
}
SLACK_REPEAT = 3  # each routine script recurs on this many different dates (with different people)


def _people_for_channel(reg, channel, date, n, r, locations=None, department=None):
    """First speaker comes from the channel's owning team; the rest from the department (or anyone for social channels)."""
    active = [e for e in reg.employees if e["status"] != "exited" and e["join_date"] <= date
              and not (e.get("leave_from") and e["leave_from"] <= date <= e.get("leave_until", "9999"))]
    if locations:
        active = [e for e in active if e["location"] in locations]
    dept_pool = [e for e in active if reg.by_id[e["department_id"]]["name"] == department] if department else active
    dept_pool = dept_pool or active
    team_name = CHANNEL_TEAM.get(channel)
    team_pool = [e for e in active if team_name and reg.by_id[e["team_id"]]["name"] == team_name] or dept_pool
    r.shuffle(team_pool)
    r.shuffle(dept_pool)
    first = team_pool[0]
    rest = [e for e in dept_pool if e["employee_id"] != first["employee_id"]][: n - 1]
    return [first["name"]] + [e["name"] for e in rest]


def build_noise_slack(reg) -> list[dict]:
    r = rng("noise-slack")
    out = []

    def conv(channel, date, lines, locations=None, department=None):
        names = _people_for_channel(reg, channel, date, 6, r, locations, department)
        msgs, t = [], r.randint(9, 16) * 60 + r.randint(0, 59)
        for who_idx, text in lines:
            t += r.randint(1, 14)
            msgs.append((names[who_idx % len(names)], ts(date, f"{t // 60:02d}:{t % 60:02d}"), text.format(*names)))
        out.append(S(channel, msgs, department=department))

    scripts = [
        ("#food-and-chai", [(0, "Biryani place near the office is doing a 20% lunch deal this week, who's in?"), (1, "in"), (2, "12:45? I have a 1pm"), (0, "12:30 then, lobby"), (3, "save me a seat, coming from a customer call")]),
        ("#food-and-chai", [(0, "Chai machine on floor 3 is out of milk again :sob:"), (1, "Facilities know, refill at 3"), (2, "floor 2 machine is fine and nobody uses it, pro tip")]),
        ("#random", [(0, "Anyone got a recommendation for a good ergonomic chair for home? My back is done."), (1, "Green Soul, the Zodiac one. Wait for a sale."), (2, "+1, had mine 2 years"), (3, "the office chairs are actually decent if you adjust the lumbar thing")]),
        ("#random", [(0, "Friday quiz is back - 5pm, Falcon room, teams of 4. Prize is bragging rights and samosas"), (1, "Team Finance will be defending the title"), (2, "you won once"), (1, "still counts")]),
        ("#random", [(0, "Cricket this Saturday at the ground near HSR - need 4 more"), (1, "count me in"), (2, "I'll come if someone brings a spare bat"), (3, "in, and I have a bat")]),
        ("#random", [(0, "PSA: the Metro is closed on the purple line this Sunday for maintenance"), (1, "thanks, was planning to come in to do the audit prep"), (0, "cab it or come Monday")]),
        ("#kudos", [(0, "Huge thanks to {1} for staying late to help with the customer demo setup yesterday - it went perfectly :clap:"), (2, "+1, {1} is a legend"), (1, "team effort! happy it landed")]),
        ("#kudos", [(0, "Shout-out to {1} and {2} for turning around the board pack numbers in one day"), (3, "the charts were :chef-kiss:"), (1, "thanks! {2} did the hard part")]),
        ("#kudos", [(0, "{1} closed the Ganga Freight renewal a week early. Well played :trophy:"), (2, "congrats {1}!"), (1, "thank you - Preeti's support on the escalation made the difference")]),
        ("#kudos", [(0, "Kudos to the Service Desk for clearing the laptop backlog before the campus hires start"), (1, "+100"), (2, "they were here till 8 on Friday")]),
        ("#bengaluru-office", [(0, "Reminder: the 4th floor is closed tomorrow morning for the carpet replacement. Boardroom bookings moved to Falcon."), (1, "does that include the 4th floor pantry?"), (0, "yes, use floor 3")]),
        ("#bengaluru-office", [(0, "Fire drill at 11:00 today - please use the stairs and assemble in the car park"), (1, "every time I'm on a customer call"), (2, "that's the point :fire:")]),
        ("#bengaluru-office", [(0, "Lost: a black Kindle in Heron room after the 3pm meeting. If found please drop at reception"), (1, "found it, it's with reception"), (0, "thank you!!")]),
        ("#bengaluru-office", [(0, "Parking update: basement B2 two-wheeler slots are now RFID - tap your ID card at the barrier"), (1, "what if the card doesn't work?"), (0, "raise an IT ticket, Facilities will map it")]),
        ("#pune-office", [(0, "Pune folks - the office is closed on Monday for Gudi Padwa. Please plan WFH."), (1, "noted"), (2, "enjoy the long weekend all")]),
        ("#pune-office", [(0, "New coffee machine has arrived in the Pune office :coffee: it does cold brew apparently"), (1, "civilisation"), (2, "testing it now for science")]),
        ("#hyderabad-office", [(0, "Hyderabad team lunch on Thursday to welcome the new joiners - 1pm at the usual place"), (1, "in"), (2, "in!"), (0, "booked for 8")]),
        ("#general", [(0, "Town hall recording and slides are up on the Company Confluence space. Q&A doc stays open till Friday."), (1, "thanks - was on a customer call"), (2, "great update on the APAC numbers")]),
        ("#general", [(0, "The Bengaluru office will be closed on 15 August (Independence Day). Pune and Hyderabad too."), (1, "and Singapore has National Day on the 9th"), (0, "correct - holiday calendar is on the HR space")]),
        ("#general", [(0, "Blood donation camp on Friday in the ground floor lobby, 10-2. Sign up sheet at reception."), (1, "signed up"), (2, "me too")]),
        ("#general", [(0, "Photos from the offsite are in the shared album (link on the HR space). Thanks everyone who made it a great two days!"), (1, "the treasure hunt was chaos and I loved it"), (2, "who won in the end?"), (1, "Finance, obviously")]),
        ("#new-joiners", [(0, "Welcome to everyone who started this week! Reminder that the new-joiner lunch is Thursday 12:30, meet at reception."), (1, "thank you! looking forward to it"), (2, "welcome all :wave:")]),
        ("#new-joiners", [(0, "Quick tip for new joiners: the IT self-service portal is the fastest way to get anything - Slack asks take longer"), (1, "and check LearnHub for the mandatory trainings, they're due in 30 days"), (2, "thanks both!")]),
        ("#eng-announcements", [(0, "Release notes for this week's platform release are on Confluence. Highlights: faster trip export, geofence bug fixes."), (1, "nice, the export one has been requested forever"), (2, "any customer-visible changes we should tell CS about?"), (0, "just the export speed - I've pinged CS")], None, "ENG"),
        ("#eng-announcements", [(0, "Reminder: the staging environment is refreshed from prod snapshots every Sunday night - don't leave test data you care about"), (1, "learned this the hard way")], None, "ENG"),
        ("#eng-announcements", [(0, "Tech talk Friday 4pm: 'What we learned running ArgoCD for 6 months' - Falcon room + Zoom"), (1, "will there be a recording?"), (0, "yes, on the ENG space")], None, "ENG"),
        ("#hr-announcements", [(0, "Open enrolment for the health insurance top-up closes on the 25th. Details on the HR space; questions to #people-ops."), (1, "does the top-up cover parents?"), (0, "yes, there's a parent add-on - see the FAQ")], None, "HR"),
        ("#hr-announcements", [(0, "The mid-year check-in window opens in Darwinbox on Monday and closes in two weeks. Managers, please schedule your conversations."), (1, "is the self-review mandatory this cycle?"), (0, "yes, one week for self-review then manager")], None, "HR"),
        ("#hr-announcements", [(0, "Holiday calendar for next year is published on the HR space. 12 holidays per location plus 2 optional."), (1, "thank you!")], None, "HR"),
        ("#learning", [(0, "New on LearnHub: 'Effective 1:1s' (45 min) for anyone managing people. Part of the manager programme but open to all."), (1, "took it yesterday, the feedback framework section is good"), (2, "adding to my list")], None, "HR"),
        ("#learning", [(0, "Reminder that Security Awareness refresh is due by end of month - 22 people still outstanding"), (1, "doing it now"), (2, "done!")], None, "HR"),
        ("#sales-team", [(0, "SwiftHaul signed - 3 years, 260 vehicles :tada: Great work {1}"), (2, "congrats!!"), (1, "thanks all, CS please prep the onboarding")], None, "SALES"),
        ("#sales-team", [(0, "Pipeline review moves to Thursday 3pm this week because of the customer visit"), (1, "noted"), (2, "ok")], None, "SALES"),
        ("#customer-success", [(0, "NPS survey results are in - 47, up from 41. Full breakdown in Metabase."), (1, "the onboarding comments improved a lot"), (2, "still getting dinged on reporting speed though")], None, "SALES"),
        ("#marketing", [(0, "New blog post is live: 'Five ways fleet telematics cuts fuel cost'. Please share on LinkedIn!"), (1, "shared"), (2, "nice one, the charts look great")], None, "MKT"),
        ("#marketing", [(0, "Webinar tomorrow at 3pm IST - 140 registrations so far. Dry run at 2."), (1, "slides are final in the shared drive"), (2, "I'll monitor the chat")], None, "MKT"),
        ("#finance", [(0, "Reminder: expense claims for the month need to be in Zoho by the 20th to make this payroll"), (1, "done"), (2, "is the 20th inclusive?"), (0, "yes, midnight on the 20th")], None, "FIN"),
        ("#finance", [(0, "Statutory auditors are on-site next Tuesday and Wednesday - please keep the AlgoWorks meeting room free"), (1, "noted, moving my 1:1s")], None, "FIN"),
        ("#it-helpdesk", [(0, "PSA: macOS update is being pushed via Intune tonight - please leave laptops plugged in and connected"), (1, "will it restart on its own?"), (0, "it'll prompt, you can defer up to 3 days")], None, "IT"),
        ("#it-helpdesk", [(0, "Wi-Fi password for AlgoWorks-Guest rotates on the 1st - new one is on the reception screen for visitors"), (1, "thanks, had a candidate ask this morning")], None, "IT"),
        ("#it-helpdesk", [(0, "Is anyone else's Zoom crashing when screen sharing from a Mac since this morning?"), (1, "yes - the 6.4 update. Roll back from Company Portal or share a window instead of the whole screen"), (0, "window share works, thanks")], None, "IT"),
        ("#it-helpdesk", [(0, "Reminder: laptops left in the office overnight must be locked in the drawer or locker, not on the desk. Security walk tonight."), (1, "noted")], None, "IT"),
        ("#it-helpdesk", [(0, "Company Portal is showing 'device not compliant' for me - what did I do?"), (1, "probably a pending OS update; install it and it clears in ~15 min"), (0, "that was it, all green now")], None, "IT"),
        ("#eng-platform", [(0, "Anyone know why the staging deploy is stuck on 'Progressing' in ArgoCD?"), (1, "image pull - the ECR token rotated, Siddharth is on it"), (2, "fixed, re-sync should work now"), (0, "green, thanks")], None, "ENG"),
        ("#eng-platform", [(0, "PR review request: PLAT-2244 pagination for the trips endpoint, ~300 lines"), (1, "on it after standup"), (1, "approved with two nits")], None, "ENG"),
        ("#eng-frontend", [(0, "Design system 2.3 is published - new date picker and the dark-mode tokens"), (1, "finally, the old date picker was cursed"), (2, "portal migration to 2.3 is in FE-812")], None, "ENG"),
        ("#eng-frontend", [(0, "iOS 26 beta breaks the map overlay in the driver app - filing it now"), (1, "known MapKit regression, there's a workaround in the Apple forums"), (0, "link?"), (1, "posted in the ticket")], None, "ENG"),
        ("#eng-data", [(0, "dbt run took 2h this morning vs the usual 40 min - anyone add a big model?"), (1, "the new sessions fact is full-refreshing every run, my bad - switching to incremental"), (0, "thanks")], None, "ENG"),
        ("#eng-data", [(0, "Metabase tip: if your question uses the Sales collection, it runs on WH_SALES now - no need to ask for a bigger warehouse for normal dashboards"), (1, "good to know")], None, "ENG"),
        ("#devops-sre", [(0, "Handover: quiet week on call, two pages (both the flaky synthetic on the status endpoint, now fixed). Datadog costs review is Thursday."), (1, "thanks, taking over")], None, "IT"),
        ("#devops-sre", [(0, "Terraform plan for the new S3 lifecycle rules is up (algoworks-infra#412), CHG goes to Tuesday CAB"), (1, "reviewed, one comment on the transition days"), (0, "fixed")], None, "IT"),
        ("#sales-ops", [(0, "Pipeline hygiene reminder: 34 opportunities have no next step in 21+ days - list in the weekly report. Please update before Thursday."), (1, "on it"), (2, "three of mine are dead, marking closed-lost")], None, "SALES"),
        ("#sales-ops", [(0, "CPQ tip: if the quote won't generate, check the price book is set on the opportunity first"), (1, "this would have saved me an hour yesterday")], None, "SALES"),
        ("#customer-success", [(0, "Meridian QBR deck is in the shared folder - please add your sections by Wednesday"), (1, "support metrics added"), (2, "usage trends in")], None, "SALES"),
        ("#people-ops", [(0, "HR queue stats for last month: 84 tickets, median 1 day to close. Top topics: letters, leave balance, payslip questions (routed to Payroll)."), (1, "nice - the Darwinbox letters module is doing its job"), (2, "can we add an FAQ for leave balance after transfers? third time this month")], None, "HR"),
        ("#demand-gen", [(0, "Webinar follow-up sequence is live in HubSpot - 3 emails over 10 days, UTM tagged"), (1, "leads go to the APAC queue if country is SG/MY/ID?"), (0, "yes, routing rule updated")], None, "MKT"),
        ("#product-marketing", [(0, "Competitor update: Cartrack launched a route-optimisation add-on; battlecard section updated"), (1, "thanks Imran - sharing with the APAC AEs")], None, "MKT"),
        # added with the 1,000-person expansion
        ("#product-core", [(0, "Roadmap review for Q4 is Thursday - please have your one-pagers in the Productboard folder by Tuesday"), (1, "dispatch one-pager is in"), (2, "geofencing one is half done, will finish tomorrow")], None, "PM"),
        ("#product-core", [(0, "Customer advisory board notes are up. Top asks: bulk geofence import, better driver-app battery usage, SSO for the driver app"), (1, "battery fix is in 5.8 already"), (0, "great, I'll tell CS to share the release note")], None, "PM"),
        ("#product-design", [(0, "Usability test sessions for the new dispatch console next week - need 5 dispatchers from 2 customers"), (1, "CS can get you Meridian and SwiftHaul"), (0, "perfect, thanks")], None, "PM"),
        ("#legal", [(0, "Reminder: use the AlgoWorks NDA template from Ironclad - customer paper NDAs need Legal review (2-day SLA)"), (1, "does that apply to partner NDAs too?"), (0, "yes, same process")], None, "LEGAL"),
        ("#legal", [(0, "New MSA template v4 is live: standard liability cap 1.5x annual fees, SLA credits table updated"), (1, "will update the sales playbook"), (2, "thanks - the old cap kept coming up")], None, "LEGAL"),
        ("#compliance", [(0, "Q3 confidential-data access review starts Monday: system owners will get ServiceNow tasks for their apps"), (1, "how long do we have?"), (0, "two weeks; evidence goes into the ISO 27001 folder")], None, "LEGAL"),
        ("#support-tier1", [(0, "Driver app 5.8 is rolling out - macro 'Driver App - update steps' has the new screenshots"), (1, "thanks, updating my canned replies"), (2, "Android rollout is at 50% today")], None, "SALES"),
        ("#support-tier1", [(0, "Queue is spiking - 40 tickets about the map tiles not loading in Hyderabad"), (1, "Maps team says it's a CDN issue, fix rolling out"), (0, "posting a status page update")], None, "SALES"),
        ("#secops", [(0, "Weekly vuln scan: 3 high findings on internet-facing hosts, tickets raised with owners, SLA 14 days"), (1, "the nginx one is patched already"), (0, "thanks, will rescan")], None, "IT"),
        ("#secops", [(0, "Phishing simulation results: 6% click rate, down from 11%. Repeat clickers get the short refresher module"), (1, "nice improvement")], None, "IT"),
        ("#sales-apac", [(0, "Jakarta logistics expo next month - we have a booth, need 2 AEs to staff it"), (1, "I can do days 1 and 2"), (2, "I'll take day 3")], None, "SALES"),
        ("#eng-mobile", [(0, "Driver app crash rate on Android 15 is 0.4% after 5.8, down from 1.1%"), (1, "the ANR fix did it"), (2, "iOS is flat at 0.2%")], None, "ENG"),
    ]
    dept_names = {"ENG": "Engineering", "HR": "Human Resources", "SALES": "Sales", "MKT": "Marketing", "FIN": "Finance",
                  "IT": "IT & Infrastructure", "PM": "Product Management", "LEGAL": "Legal & Compliance"}
    for item in scripts:
        channel, lines = item[0], item[1]
        locations = SOCIAL_CHANNELS.get(channel)
        department = dept_names[item[3]] if len(item) > 3 and item[3] else None
        for _ in range(SLACK_REPEAT):
            date = random_date(r, NOISE_START, NOISE_END)
            conv(channel, date, lines, locations=locations, department=department)
    return out
