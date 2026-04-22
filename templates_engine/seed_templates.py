"""
Seed TemplateDefinition rows for the MVP templates.

Bodies use Django template syntax. Jurisdiction-specific variants are selected
via {% if %} blocks; values are filled from org + profile context.
"""

TEMPLATES = [
    # --- Privacy Notices (per jurisdiction) ----------------------------------
    {
        'kind': 'privacy_notice', 'jurisdiction_code': 'EU',
        'name': 'Privacy Notice — GDPR (EU/EEA)',
        'description': 'GDPR-compliant privacy notice covering Arts. 12–14 disclosures.',
        'requirements': ['GDPR-Art-12'],
        'body': """# Privacy Notice

**{{ org.name }}** ("we", "us") is committed to protecting your personal data. This notice explains how we process your personal data in compliance with the **General Data Protection Regulation (Regulation (EU) 2016/679)**.

_Last updated: {{ today|date:"F j, Y" }}_

## 1. Who we are
- **Controller:** {{ org.name }}{% if org.website %} — {{ org.website }}{% endif %}
- **Country of establishment:** {{ org.country }}
- **Data Protection Officer:** [DPO contact — please update]

## 2. What personal data we collect
{% if profile %}{% for c in profile.data_categories %}- {{ c|title }}
{% endfor %}{% else %}- [List the categories of personal data collected.]{% endif %}

## 3. Why we process your data (purposes and lawful bases)
{% if profile %}{% for p in profile.processing_purposes %}- **{{ p|title }}** — lawful basis: [specify from Art. 6(1) (a)–(f)]
{% endfor %}{% endif %}

## 4. How long we keep your data
We retain personal data only as long as necessary for the purposes above and for compliance with legal obligations. A full retention schedule is available on request.

## 5. Who we share your data with
- Service providers acting as processors under a written DPA
- Competent authorities where legally required

## 6. International transfers
{% if profile and profile.cross_border_transfers %}We transfer personal data outside the EEA. Such transfers are covered by Standard Contractual Clauses (SCCs) or an adequacy decision. A copy of the safeguards is available on request.{% else %}We do not transfer personal data outside the EEA.{% endif %}

## 7. Your rights (GDPR Arts. 15–22)
You have the right of access, rectification, erasure, restriction, portability, objection, and the right not to be subject to a decision based solely on automated processing. You may withdraw consent at any time where processing is based on consent.

## 8. How to exercise your rights
Contact us at **[privacy contact email]** or the address above. We will respond within one calendar month.

## 9. Complaints
You may lodge a complaint with your local supervisory authority (e.g. the Irish Data Protection Commission, CNIL, BfDI).

---
_This notice does not constitute legal advice. Review with qualified counsel before publication._
""",
    },
    {
        'kind': 'privacy_notice', 'jurisdiction_code': 'GH',
        'name': 'Privacy Notice — Ghana Data Protection Act',
        'description': 'Ghana DPA 2012 privacy notice.',
        'requirements': ['GH-Notice'],
        'body': """# Privacy Notice (Ghana)

**{{ org.name }}** is registered (or will register) as a data controller with the **Data Protection Commission of Ghana** under the **Data Protection Act, 2012 (Act 843)**.

_Last updated: {{ today|date:"F j, Y" }}_

## 1. Controller
- {{ org.name }}{% if org.website %} — {{ org.website }}{% endif %}
- Country: Ghana (or as registered)

## 2. Personal data we process
{% if profile %}{% for c in profile.data_categories %}- {{ c|title }}
{% endfor %}{% else %}- [Categories of personal data]{% endif %}

## 3. Purposes and lawful bases
We process personal data on the bases permitted by section 20 of the Act — consent, performance of contract, legal obligation, vital interests, public interest, or legitimate interests.

## 4. Data subject rights
Under sections 32–37 of the Act you have the right to access your personal data, correct or delete inaccurate data, and object to processing. Write to us at **[privacy contact email]**.

## 5. Retention
We retain personal data only as long as necessary and as provided by law.

## 6. Security
We apply reasonable technical and organisational measures as required by section 28 of the Act.

## 7. Cross-border transfers
{% if profile and profile.cross_border_transfers %}Certain transfers are made outside Ghana; we take steps to ensure an adequate level of protection, in line with section 47 of the Act.{% else %}We do not transfer personal data outside Ghana.{% endif %}

## 8. Complaints
You may complain to the **Data Protection Commission of Ghana**.

---
_This notice does not constitute legal advice._
""",
    },
    {
        'kind': 'privacy_notice', 'jurisdiction_code': 'KE',
        'name': 'Privacy Notice — Kenya Data Protection Act',
        'description': 'Kenya DPA 2019 privacy notice.',
        'requirements': ['KE-Notice'],
        'body': """# Privacy Notice (Kenya)

This notice describes how **{{ org.name }}** ("we") processes personal data under the **Data Protection Act, 2019** (Act No. 24 of 2019).

_Last updated: {{ today|date:"F j, Y" }}_

## 1. Controller
{{ org.name }}{% if org.website %} — {{ org.website }}{% endif %}

## 2. Personal data collected
{% if profile %}{% for c in profile.data_categories %}- {{ c|title }}
{% endfor %}{% endif %}

## 3. Purposes and lawful basis (DPA §30)
- Consent / Contract / Legal obligation / Vital interests / Public interest / Legitimate interests

## 4. Rights of data subjects (DPA §26)
Access, rectification, erasure, restriction, portability, objection, and rights relating to automated decision-making. To exercise these rights contact **[privacy contact email]**.

## 5. Retention
We retain personal data only as long as necessary.

## 6. Cross-border transfers (DPA §§48–50)
{% if profile and profile.cross_border_transfers %}Transfers outside Kenya are made under adequacy, appropriate safeguards, or a permitted exception.{% else %}No cross-border transfers.{% endif %}

## 7. Complaints
You may complain to the **Office of the Data Protection Commissioner (ODPC)** — https://www.odpc.go.ke/.

---
_This notice does not constitute legal advice._
""",
    },
    {
        'kind': 'privacy_notice', 'jurisdiction_code': 'NG',
        'name': 'Privacy Notice — Nigeria Data Protection Act',
        'description': 'NDPA 2023 privacy notice.',
        'requirements': ['NG-Notice'],
        'body': """# Privacy Notice (Nigeria)

**{{ org.name }}** processes personal data in accordance with the **Nigeria Data Protection Act, 2023 (NDPA)**.

_Last updated: {{ today|date:"F j, Y" }}_

## 1. Controller / Processor of record
{{ org.name }}{% if org.website %} — {{ org.website }}{% endif %}

## 2. Personal data we process
{% if profile %}{% for c in profile.data_categories %}- {{ c|title }}
{% endfor %}{% endif %}

## 3. Lawful basis (NDPA §25)
Consent, contract, legal obligation, vital interests, public interest, or legitimate interests.

## 4. Rights (NDPA §§34–39)
Access, rectification, erasure, restriction, portability, objection, opt-out of automated decisions. Contact: **[privacy contact email]**.

## 5. Breach notifications (NDPA §40)
We notify the NDPC within 72 hours of becoming aware of a personal data breach and notify affected individuals where the breach is likely to result in high risk.

## 6. International transfers (NDPA §§41–43)
{% if profile and profile.cross_border_transfers %}International transfers are permitted on the basis of adequacy, appropriate safeguards, binding instruments, or permitted exceptions.{% else %}No international transfers.{% endif %}

## 7. Complaints
You may lodge a complaint with the **Nigeria Data Protection Commission (NDPC)** — https://ndpc.gov.ng/.

---
_This notice does not constitute legal advice._
""",
    },
    {
        'kind': 'privacy_notice', 'jurisdiction_code': 'US',
        'name': 'Privacy Notice — California (CCPA/CPRA)',
        'description': 'CCPA/CPRA California-specific notice.',
        'requirements': ['CCPA-Notice'],
        'body': """# California Privacy Notice

This California-specific notice supplements our main privacy policy for California residents whose information we collect, in compliance with the **California Consumer Privacy Act (CCPA)**, as amended by the **CPRA**.

_Last updated: {{ today|date:"F j, Y" }}_

## 1. Categories of personal information collected
We have collected the following categories in the past 12 months:
{% if profile %}{% for c in profile.data_categories %}- {{ c|title }}
{% endfor %}{% endif %}

## 2. Business or commercial purposes
{% if profile %}{% for p in profile.processing_purposes %}- {{ p|title }}
{% endfor %}{% endif %}

## 3. Categories disclosed / sold / shared
We [do / do not] sell or share personal information. Where we do, the categories and recipients are disclosed here.

## 4. Your rights
- Right to know
- Right to delete
- Right to correct
- Right to opt out of sale / sharing
- Right to limit use of sensitive personal information
- Right to non-discrimination

## 5. How to exercise your rights
- **Web:** [request form URL]
- **Toll-free:** [phone number]
- "Do Not Sell or Share My Personal Information" link: [link]

## 6. Authorised agents
You may designate an authorised agent to submit a request; we will verify the agent's authority.

## 7. Retention
We retain personal information only as long as necessary for the disclosed purposes.

## 8. Notice of Financial Incentive
If we offer any financial incentive for the collection of personal information, we provide the required disclosures.

---
_This notice does not constitute legal advice._
""",
    },

    # --- ROPA (jurisdiction-neutral template with jurisdiction badge) --------
    {
        'kind': 'ropa', 'jurisdiction_code': '',
        'name': 'Record of Processing Activities (ROPA)',
        'description': 'Template aligned with GDPR Art. 30, NDPA §29, Kenya DPA, Ghana DPA.',
        'requirements': ['GDPR-Art-30', 'NG-ROPA', 'KE-Principles', 'GH-Principles'],
        'body': """# Record of Processing Activities (ROPA)

**Controller:** {{ org.name }}{% if org.country %} • **Country:** {{ org.country }}{% endif %}
**Date generated:** {{ today|date:"F j, Y" }}

> This record is maintained under GDPR Art. 30, NDPA §29, Kenya DPA §25, and Ghana DPA §17 where applicable.

## Processing activities

| # | Activity | Purpose | Lawful basis | Categories of data | Subjects | Recipients | Retention | Transfers | Security measures |
|---|---|---|---|---|---|---|---|---|---|
| 1 | [Activity name] | [Purpose] | [Basis] | {% if profile %}{{ profile.data_categories|join:", " }}{% endif %} | [Subject groups] | [Recipients] | [Retention period] | {% if profile and profile.cross_border_transfers %}Cross-border — SCCs{% else %}Domestic{% endif %} | Encryption, access controls, logging |
| 2 | … | … | … | … | … | … | … | … | … |

## Governance sign-off

- **Reviewed by:** [Name, role]
- **Next review date:** [Date]

---
_Keep this ROPA current — update on every new processing activity. Regulators may request it with short notice._
""",
    },

    # --- DSAR response template ---------------------------------------------
    {
        'kind': 'dsar_response', 'jurisdiction_code': '',
        'name': 'Data Subject Access Request Response',
        'description': 'DSAR response template covering GDPR/NDPA/Kenya/Ghana/CCPA.',
        'requirements': ['GDPR-Art-15', 'NG-Rights', 'KE-Rights', 'GH-Rights', 'CCPA-Rights'],
        'body': """[Date: {{ today|date:"F j, Y" }}]

Dear [Data subject name],

Thank you for your request of [DD/MM/YYYY] relating to the personal data we process about you. This is the formal response from **{{ org.name }}**.

**Reference:** [Request ID]

### 1. Your request
You asked for: [copy the request verbatim].

### 2. Our verification
Before processing the request we verified your identity using [method]. We processed this request without charge.

### 3. Outcome
{% if jurisdiction_code %}Under {{ jurisdiction_code }}{% else %}Under applicable data protection law{% endif %}, we confirm:

- **Data we hold about you:** [enumerate categories]
- **Sources:** [sources]
- **Purposes:** [purposes]
- **Recipients:** [recipients]
- **Retention:** [periods]
- **Your other rights:** rectification, erasure, restriction, portability, objection, and — where applicable — to object to automated decision-making

### 4. How to challenge our response
If you are not satisfied you may complain to the supervisory authority in your country (for example, the Data Protection Commission in Ghana, the ODPC in Kenya, the NDPC in Nigeria, the lead supervisory authority in the EEA, or the California Privacy Protection Agency).

Yours sincerely,
[Name], Data Protection Officer
{{ org.name }}

---
_This response template is provided as a compliance aid and does not constitute legal advice._
""",
    },

    # --- Cookie / tracker policy --------------------------------------------
    {
        'kind': 'cookie_policy', 'jurisdiction_code': '',
        'name': 'Cookie & Tracker Policy',
        'description': 'Cookie disclosure covering strictly necessary, analytics, and marketing categories.',
        'requirements': ['GDPR-Art-12', 'GH-Notice', 'KE-Notice', 'NG-Notice', 'CCPA-Notice'],
        'body': """# Cookie & Tracker Policy

**{{ org.name }}** uses cookies and similar tracking technologies on our website and applications. This policy explains what we use them for and how you can control them.

_Last updated: {{ today|date:"F j, Y" }}_

## 1. What are cookies?
Cookies are small text files placed on your device. Similar technologies include local storage, pixels, SDKs, and fingerprinting tools. We refer to all of them as "cookies" below.

## 2. Categories of cookies we use

| Category | Purpose | Lifetime | Can you disable? |
|---|---|---|---|
| Strictly necessary | Session, authentication, security | Session | No |
| Preferences | Language, UI state | 1 year | Yes |
| Analytics | Aggregate usage measurement | 13 months | Yes |
| Marketing | Audience targeting and measurement | 13 months | Yes (opt-in required) |

## 3. Your choices
- **Consent banner** — on your first visit you can accept or reject non-essential cookies.
- **Preferences centre** — change your choices any time at [link to preferences].
- **Browser controls** — you can block or delete cookies at browser level.
- **Global Privacy Control (GPC)** — we honour GPC signals as an opt-out of sale/share for California residents.

## 4. Third-party cookies
Some cookies are set by providers we integrate with (e.g. analytics, embedded content). A full vendor list is available at [vendor list URL].

## 5. Changes to this policy
We review this policy at least annually.

## 6. Contact
Questions: **[privacy contact email]**.

---
_This policy is informational and does not constitute legal advice._
""",
    },

    # --- DPIA template ------------------------------------------------------
    {
        'kind': 'dpia', 'jurisdiction_code': '',
        'name': 'Data Protection Impact Assessment (DPIA)',
        'description': 'DPIA template structured around GDPR Art. 35 and equivalent Kenya / Nigeria requirements.',
        'requirements': ['GDPR-Art-35', 'KE-DPIA'],
        'body': """# Data Protection Impact Assessment

**Organisation:** {{ org.name }}
**Assessment date:** {{ today|date:"F j, Y" }}
**Prepared by:** [Name, role]
**Reviewed by:** [DPO / Privacy lead]

## 1. Describe the processing
- **Activity:** [Name of processing activity]
- **Purpose:** [Primary and secondary purposes]
- **Legal basis:** [Art. 6 basis; Art. 9 condition if special category]
- **Data categories:** {% if profile %}{{ profile.data_categories|join:", " }}{% else %}[List]{% endif %}
- **Data subjects:** [Employees / customers / children / vulnerable]
- **Volume:** [Estimated number of subjects / records]
- **Retention:** [How long]
- **Recipients and transfers:** [Including any cross-border]

## 2. Necessity and proportionality
- Lawful basis justification
- Less-intrusive alternatives considered
- Data minimisation measures applied
- Transparency measures (notice, signage)

## 3. Consultation
- Internal stakeholders: [teams, dates]
- External stakeholders / data subjects: [how/when]
- DPO opinion: [summary + date]

## 4. Risk assessment

| # | Risk | Likelihood (1-5) | Impact (1-5) | Inherent score | Mitigation | Residual score |
|---|---|---|---|---|---|---|
| 1 | [e.g. unauthorised disclosure of financial data] | | | | | |
| 2 | | | | | | |

## 5. Mitigations
- Technical: encryption, access control, logging
- Organisational: training, contracts, oversight
- Contractual: DPAs, flow-down clauses

## 6. Residual risk and decision

- **Residual risk level:** [Low / Moderate / High]
- **Decision:** [Proceed / Proceed with conditions / Consult regulator / Do not proceed]

## 7. Sign-off
- **DPO:** [Name, date]
- **Business owner:** [Name, date]
- **Next review:** [Date]

---
_This DPIA template is provided as a compliance aid and does not constitute legal advice._
""",
    },

    # --- Regulator breach notification --------------------------------------
    {
        'kind': 'breach_notification', 'jurisdiction_code': '',
        'name': 'Regulator Breach Notification Letter',
        'description': 'Letter template for notifying the supervisory authority within 72 hours.',
        'requirements': ['GDPR-Art-33', 'KE-Breach', 'NG-Breach'],
        'body': """[On organisation letterhead]

[Recipient: Supervisory authority — e.g. Office of the Data Protection Commissioner / NDPC / Data Protection Commission / EU lead supervisory authority]

**Subject:** Notification of Personal Data Breach — {{ org.name }}
**Reference:** [Internal case ID]
**Date:** {{ today|date:"F j, Y" }}

Dear Sir / Madam,

This notification is made under applicable data protection law (GDPR Art. 33 / Kenya DPA §43 / NDPA §40 / equivalent) within 72 hours of becoming aware of a personal data breach affecting data subjects for which {{ org.name }} is the controller.

### 1. Nature of the breach
- **Date/time of occurrence:** [ ]
- **Date/time of detection:** [ ]
- **Type of breach:** [Confidentiality / Integrity / Availability]
- **Categories of data affected:** [ ]
- **Approximate number of data subjects:** [ ]
- **Approximate number of records:** [ ]

### 2. Likely consequences
[Describe harm assessment: identity theft, discrimination, financial loss, reputational damage, etc.]

### 3. Measures taken or proposed
- Containment: [ ]
- Eradication: [ ]
- Recovery: [ ]
- Communication to affected individuals: [Planned / completed / not required because …]

### 4. Contact details
- **Data Protection Officer:** [Name, email, phone]
- **Alternative contact:** [Name, role, email]

We will supplement this notification with further information as the investigation progresses.

Yours faithfully,

[Name]
[Title]
{{ org.name }}

---
_This template is provided as a compliance aid and does not constitute legal advice._
""",
    },
]
