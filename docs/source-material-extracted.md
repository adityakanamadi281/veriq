# Sprint 1 Assessment Engine(1).pdf


## Page 1

Sprint 1 · Assessment Engine
Time: 12:00 PM – 2:20 PM
Objective: Build a working assessment engine exposed through FastAPI and running locally.
By the end of Sprint 1, the system should be able to take candidate context, conduct an adaptive AI-led
assessment, evaluate the responses, and return a structured readiness result.
Candidate Context → Question → Response → Evaluation → Next Question → Score →
Report
The assessment must be demonstrable independently of the frontend.
Sprint Outcome
At 2:20 PM, you should be able to demonstrate the complete assessment using FastAPI Swagger , Postman,
curl, or another simple API client.
The demonstration should show:
candidate context being submitted
an assessment being started
questions being returned through the API
candidate responses being submitted
subsequent questions adapting to the candidate and previous responses
assessment completion
readiness score
strengths and capability gaps
readiness classification
recommended pathway
concise personalized report
Build Sequence
1. Establish the Backend
Start by creating the technical foundation.
Set up:
FastAPI
PostgreSQL through Supabase
Gemini API
environment variables
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
1


## Page 2

database connection
core application structure
Confirm independently that:
FastAPI runs locally → Database connection works → Gemini responds successfully
Do not proceed with the full assessment until this foundation works.
2. Define Candidate Context
Create the minimum candidate context required to conduct a meaningful assessment.
The assessment should be able to understand relevant information such as:
education
experience level
target role
technical skills
projects
AI/coding tools used
CV or structured background information
Store the candidate and assessment state in PostgreSQL.
Design this data model with Sprint 2 in mind. The same backend will later support the candidate
application.
3. Build the Assessment Flow
Implement the core assessment loop:
Understand candidate → Ask question → Receive response → Evaluate evidence →
Decide next question
The assessment should be adaptive.
Questions should respond to:
candidate background
experience level
target role
previous answers
evidence already collected
The assessment should cover sufficient evidence across areas such as:
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
2


## Page 3

Engineering Fundamentals
Problem Solving
AI Fluency
Agentic Engineering
Practical Reasoning
Communication
The exact assessment design is part of your implementation judgment.
4. Build Response Evaluation
For every meaningful response, evaluate the candidate against explicit criteria.
The AI should help with:
understanding the response
identifying evidence
assessing capability
identifying strengths
identifying gaps
determining whether further questioning is required
Use normal application logic for deterministic calculations and state management.
Do not rely on Gemini to manage application state or perform calculations that can be handled reliably in
code.
5. Complete the Assessment
The system must determine when sufficient evidence has been collected and complete the assessment.
The final result should include:
Overall Readiness Score
Dimension-Level Assessment
Key Strengths
Capability Gaps
Readiness Classification
Recommended Pathway
Personalized Assessment Summary
• 
• 
• 
• 
• 
• 
3


## Page 4

The result should be returned as structured API data that can be consumed directly by the React application
in Sprint 2.
6. Expose the Assessment APIs
The exact API design is your decision, but the backend must support the equivalent of:
Start Assessment
Creates an assessment using candidate context and returns the first question.
Submit Response
Accepts a candidate response, evaluates it, persists it, and returns either the next question or assessment
completion.
Get Assessment
Returns the current state and progress of an assessment.
Get Result
Returns the completed score, assessment findings, report, and recommendation.
Keep the API contract clean. Sprint 2 will build the complete application on top of these APIs.
Persistence
The database should remain the source of truth.
Persist enough information to support:
candidate context
assessment
questions asked
responses
evaluations
progress
scores
final result
A candidate assessment should not depend entirely on in-memory Python state.
Sprint 1 Checkpoint
At 2:20 PM, demonstrate one complete assessment from start to finish.
• 
• 
• 
• 
• 
• 
• 
• 
4


## Page 5

The minimum successful flow is:
Candidate submitted → Assessment created → Adaptive questions answered →
Responses evaluated → Assessment completed → Structured result returned
The result should be credible enough that it could be presented to a candidate through a user interface
without redesigning the underlying assessment logic.
Break · 2:20 PM – 3:00 PM
Sprint 1 formally ends at 2:20 PM.
Participants who have completed the assessment engine can use the break normally.
Participants who need additional time may continue working during the break.
At 3:00 PM, Sprint 2 begins for everyone.
Sprint 2 will use the backend and assessment APIs created here to build the complete candidate
application, remaining application APIs, and end-to-end integration.
5


# Sprint 2 Candidate Application & Integration(1).pdf


## Page 1

Sprint 2 · Candidate Application & Integration
Time: 3:00 PM – 5:30 PM
Objective: Build the complete candidate-facing application, integrate the Assessment APIs from Sprint 1,
and deliver a working end-to-end product running locally.
Sprint 1 established the backend foundation and assessment intelligence.
Sprint 2 turns that capability into a complete product experience.
By the end of the sprint, a new candidate should be able to move independently through the full journey:
Create Account → Build Profile → Start Assessment → Complete Assessment → Receive
Result → Review Report → Understand Recommended Pathway
The application must use the assessment engine built in Sprint 1. Assessment intelligence should remain in
the backend and should not be recreated in the frontend.
Sprint Outcome
At 5:30 PM, the complete application should be running locally and ready for demonstration.
The implementation should include:
React candidate application
authentication
candidate profile
relevant background / CV input
FastAPI application APIs
Assessment API integration
complete assessment experience
persistent assessment state
results
personalized report
recommended pathway
assessment history where implemented
clear handling of loading, completion, and failure states
The final product should demonstrate one coherent end-to-end experience rather than a collection of
disconnected screens.
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
1


## Page 2

Build Sequence
1. Validate the Sprint 1 Foundation
Before building the application, confirm that the Sprint 1 backend remains operational.
Verify:
FastAPI runs locally
PostgreSQL / Supabase connection works
Gemini integration works
assessment can be started
responses can be submitted
the next question can be returned
an assessment can complete
a structured result can be retrieved
Review the Assessment API contract before building against it.
The frontend should consume the existing contract rather than introducing a second interpretation of
assessment logic.
2. Establish the React Application
Create the candidate-facing React application.
Set up:
application structure
routing
API service layer
authentication state
shared components
loading and error states
environment configuration
Confirm the basic connection:
React → FastAPI → Response displayed in React
Do this before building individual screens.
Keep frontend and backend within the same repository, consistent with the development structure already
established.
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
2


## Page 3

3. Build Account & Candidate Profile
Implement the minimum identity and candidate context required for the product.
The candidate should be able to:
sign up
log in
create or update their profile
provide education and experience
specify target role
provide technical background
provide relevant professional links
provide CV/background information where supported
Profile information should be persisted through the backend.
Do not keep candidate data solely in React state.
The profile created here becomes the candidate context passed into the assessment engine.
4. Build the Assessment Experience
Create the user interface around the Sprint 1 Assessment APIs.
The experience should support:
Start Assessment → Display Question → Capture Response → Submit Response →
Receive Next State
The application should present the assessment as a coherent interaction rather than exposing backend
implementation details.
Support the response formats required by the assessment implementation, such as:
text
voice, where implemented
multiple choice
scenario response
code review
debugging / reasoning
practical questions
The frontend is responsible for presentation and input capture.
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
3


## Page 4

The backend remains responsible for:
question selection
evaluation
assessment state
scoring
classification
report generation
recommendation
5. Integrate Assessment State
The candidate must be able to progress through the assessment reliably.
For every response:
Capture the candidate input
Submit it to FastAPI
Persist the response
Receive the updated assessment state
Render the next question or completion state
The application should clearly represent:
assessment started
assessment in progress
current progress
response being processed
next question available
assessment completed
assessment failed / retry required
PostgreSQL should remain the source of truth for assessment progress.
Refreshing the browser should not silently destroy an assessment that has already been persisted.
6. Build the Completion Experience
When the assessment completes, transition the candidate into the result experience.
The application should display the structured output generated by the backend.
At minimum:
Overall Readiness Score
Dimension-Level Results
• 
• 
• 
• 
• 
• 
• 
1. 
2. 
3. 
4. 
5. 
• 
• 
• 
• 
• 
• 
• 
4


## Page 5

Key Strengths
Capability Gaps
Readiness Classification
Personalized Assessment Summary
Recommended Pathway
The result should feel like the conclusion of the assessment, not raw API output.
Use hierarchy and presentation carefully so the candidate can immediately understand:
Where do I stand? → Why? → What should I do next?
7. Build the Recommended Pathway
Present the recommendation returned by the Assessment API.
The application should not independently decide the pathway.
It should interpret the backend result and present the appropriate experience.
Possible states may include:
Ready
Targeted capability development
Structured capability development
Foundation development
Each pathway should include:
clear recommendation
concise rationale
capability areas that led to the recommendation
appropriate next action
Keep the presentation useful and specific.
Avoid generic AI-generated career advice.
• 
• 
• 
• 
5


## Page 6

8. Complete the Remaining Application APIs
Extend the FastAPI backend only where required to support the full candidate journey.
Typical application APIs may include:
Profile
retrieve profile
update profile
Candidate Evidence
CV/background upload
professional links
Assessment
list assessments
retrieve current assessment
retrieve completed result
Report
retrieve assessment report
History
retrieve previous assessments where implemented
Application State
any additional persistence required by the candidate experience
Maintain the architecture established during Sprint 1.
Do not create a second backend or bypass FastAPI for application business logic.
9. Complete the Data Flow
The complete application should now follow one consistent architecture:
React → FastAPI → PostgreSQL / Assessment Engine → Gemini → FastAPI → React
The frontend should never call Gemini directly.
Secrets and privileged credentials must remain server-side.
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
6


## Page 7

All business state that must survive a browser refresh should be persisted.
10. Validate the Complete Journey
Once the end-to-end flow works, stop adding major functionality.
Create a new candidate account and run through the application exactly as an external user would.
Validate:
signup works
login works
profile persists
assessment starts correctly
questions render correctly
responses are accepted
adaptive questioning continues
assessment state persists
completion occurs correctly
score is returned
report displays correctly
recommendation is understandable
no developer intervention is required
Fix complete-flow issues before improving secondary functionality.
Product Quality
Once the complete journey is operational, use remaining time to improve the areas that materially affect
the demonstration.
Prioritize:
Clarity
The user should always understand:
where they are
what is being asked
what is happening
what happens next
Reliability
Handle:
API failures
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
7


## Page 8

missing candidate information
invalid input
Gemini failures
interrupted assessment state
duplicate submissions
loading states
UX
Improve:
hierarchy
spacing
readability
form clarity
assessment progress
results presentation
mobile responsiveness where practical
Do not spend time adding visual decoration that does not improve the candidate journey.
Engineering Discipline
Keep Business Logic in the Backend
React should not contain:
assessment scoring logic
readiness classification logic
recommendation rules
Gemini prompts
secret credentials
Persist Important State
Use PostgreSQL for:
candidate profile
assessment state
responses
results
Do not depend on browser memory for state that matters.
Keep API Integration Centralized
Use a common frontend API/service layer rather than making arbitrary HTTP calls throughout components.
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
8


## Page 9

Keep Secrets Private
Do not expose:
Gemini API keys
database service credentials
backend secrets
Use environment variables as defined in the setup guide.
Sprint 2 Checkpoint
At 5:30 PM, the application should be demo-ready locally.
The required journey is:
New Candidate → Account → Profile → Assessment → Adaptive Questions →
Completion → Readiness Result → Personalized Report → Recommended Pathway
The application should be usable without:
manually modifying the database
manually triggering backend functions
changing code during the demonstration
using developer-only shortcuts
explaining around broken parts of the core journey
Submission Readiness
Before 5:30 PM:
commit the latest working code
confirm frontend runs locally
confirm FastAPI runs locally
confirm database connection works
confirm Gemini works
confirm the complete journey works with a new candidate
update README where required
ensure .env and credentials are not committed
prepare the application in a clean state for demonstration
Deployment is optional unless already completed.
A reliable local implementation is preferable to a partially working deployed application.
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
9


## Page 10

Demo Preparation · 5:30 PM – 5:50 PM
Use this period only to prepare and verify the demonstration.
The demonstration should follow the product journey rather than a tour of the source code:
Candidate enters → Candidate is understood → Assessment adapts → Responses are
evaluated → Readiness is determined → Result and recommendation are presented
Be prepared to explain the major technical decisions after demonstrating the working product.
Sprint 2 Completion Standard
Sprint 2 is complete when the assessment capability created in Sprint 1 has been transformed into a
coherent candidate-facing product.
The final implementation should demonstrate:
Frontend + Backend + Database + AI + Product Experience working together as one
system.
10


# Candidate Application UI & Experience Brief(2).pdf


## Page 1

Candidate Application · UI & Experience Brief
Purpose: Define the visual and interaction direction for the candidate-facing application.
This document should be used alongside the Sprint 1 and Sprint 2 briefs as product context when designing
and building the application with Google Antigravity.
The objective is not to reproduce prescribed screens pixel-for-pixel. The objective is to create a coherent,
high-quality candidate experience that follows the principles and hierarchy below.
1. Experience Principle
The application should feel like a premium professional assessment product.
It should not feel like:
an edtech course marketplace
a recruitment portal
a traditional online examination
a gamified learning product
a generic AI application
The candidate should feel that the system is:
understanding them → assessing them intelligently → producing an evidence-based
view of their readiness
The interface should remain calm and largely disappear behind the assessment experience.
2. Visual Direction
The overall aesthetic should be:
Minimal · Modern · Professional · Intelligent · Premium
Recommended visual characteristics:
warm white or off-white background
near-black primary text
one restrained dark accent colour
modern sans-serif typography
medium-weight headings
generous whitespace
clear hierarchy
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
1


## Page 2

subtle borders
restrained use of cards
consistent spacing
strong mobile responsiveness
Avoid:
gradients
excessive colour
decorative illustrations
cartoon AI imagery
large icon sets
oversized shadows
gamification
unnecessary dashboards
visual clutter
generic "future of work" aesthetics
The design should feel credible to both a young candidate and a professional employer .
3. Product Navigation
Keep navigation deliberately small.
For the initial candidate application:
Home
Assessments
Profile
Do not introduce navigation for products that are not required for the current experience.
The assessment should remain the centre of the application.
4. Landing Experience
The landing page should communicate the product immediately.
Primary message
Find out how ready you are for an AI-first engineering role.
Supporting copy should explain the outcome in one short sentence.
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
2


## Page 3

For example:
Understand your strengths, identify capability gaps, and receive a personalized readiness
assessment.
Primary action
Start Assessment
Supporting information may include:
adaptive AI assessment
practical evaluation
personalized readiness report
Keep the page focused.
The user should understand the proposition and primary action within seconds.
5. Candidate Profile
The profile experience should collect only information that improves the assessment.
Typical inputs:
name
education
graduation year
experience
target role
technical background
GitHub
LinkedIn
CV
Prefer progressive disclosure over displaying a long form at once.
Where information can be extracted from the CV, avoid requiring the candidate to enter the same
information again.
The profile experience should feel like:
Help us understand you before we begin.
Not:
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
3


## Page 4

Complete this registration form.
6. Candidate Introduction
The introduction should create a clear transition from profile setup into the assessment.
Primary prompt
Introduce yourself
Supporting prompt:
Tell us what you have built, what you are good at, and the kind of engineering work you want
to do.
Preferred interaction:
Voice response
Secondary option:
Type instead
The experience should feel conversational and personal rather than form-based.
7. Assessment Experience
This is the most important part of the interface.
One question at a time
Do not display the assessment as a long questionnaire.
Each screen should focus on one task or question.
Example structure:
Assessment
Engineering Fundamentals · Question 3
You mentioned building a React application with a FastAPI backend. Walk through what
happens from the moment a user submits a form until the data is stored.
Response area:
4


## Page 5

Speak
or
Type your answer
Primary action:
Continue
Assessment progress
Use a restrained progress indicator .
The candidate should know they are progressing without turning the experience into a traditional timed
examination.
Adaptive experience
Questions may differ based on:
candidate background
experience
projects
previous responses
evidence already collected
The UI should support this naturally.
Do not expose the underlying assessment logic to the candidate.
8. Practical Questions
The same assessment shell should support different question formats without making the application feel
fragmented.
Potential formats include:
written response
voice response
multiple choice
scenario
code review
debugging
practical reasoning
agent instruction improvement
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
5


## Page 6

Code-related questions should use a clean code presentation appropriate for technical content.
The surrounding visual structure should remain consistent.
9. Response Processing
When a response requires AI evaluation, provide a clear processing state.
Avoid conversational gimmicks such as:
AI is thinking...
Use professional language such as:
Evaluating response
or
Preparing next question
Keep loading states calm and short.
The candidate should never wonder whether the application has stopped working.
10. Assessment Completion
Once sufficient evidence has been collected, clearly transition from assessment to results.
Recommended state:
Preparing your assessment
Supporting text:
Reviewing your responses across the assessed capability areas.
Capability areas may be shown simply:
Engineering Fundamentals
Problem Solving
AI Fluency
Agentic Engineering
Communication
Do not display fake precision or artificial progress percentages.
• 
• 
• 
• 
• 
6


## Page 7

11. Results Experience
The result is the highest-value moment in the application.
The first screen should answer three questions immediately:
Where do I stand?
Why?
What should I do next?
Primary hierarchy
Display the overall readiness score prominently.
Example:
72
Readiness Score
Followed by the readiness classification.
Example:
Developing
Then provide a concise assessment summary.
You demonstrate strong engineering fundamentals and problem-solving ability. Your largest
current gap is applying AI agents systematically across implementation, testing, and
verification.
Dimension results
Present individual capability areas clearly.
For example:
Engineering Fundamentals
82
Problem Solving
78
7


## Page 8

AI Fluency
64
Agentic Engineering
57
Communication
76
Use simple bars, rows, or restrained data visualization.
Avoid turning every score into a large card.
12. Strengths & Development Areas
After the primary result, show the evidence that makes the score useful.
Strengths
Focus on a small number of specific findings.
Examples:
Strong understanding of API and application flow
Clear technical reasoning
Good approach to validating generated code
Development Priorities
Identify the highest-value areas for improvement.
Examples:
Limited practical use of autonomous coding agents
Inconsistent testing and verification workflow
Further development required in production debugging
Avoid generic feedback.
Every finding should feel connected to the assessment.
13. Recommended Pathway
The recommendation should be visually clear but not aggressively commercial.
Present:
• 
• 
• 
• 
• 
• 
8


## Page 9

Recommended next step
Then:
pathway
short explanation
why it has been recommended
key capability areas it addresses
Possible pathway types:
Ready
Targeted Capability Development
Structured Capability Development
Foundation Development
The recommendation should feel like the logical conclusion of the assessment, not a sales promotion.
14. Personalized Report
The detailed report should use a clean, document-like presentation.
Think closer to a well-designed Notion page than a dashboard.
Suggested structure:
• 
• 
• 
• 
9


## Page 10

Your Assessment
Summary
Readiness
Strengths
Development Areas
Evidence
Recommended Pathway
Learning Priorities
The report should be something the candidate would reasonably want to save, revisit, or share.
15. Assessment History
Where implemented, previous assessments should be presented simply.
Show:
assessment date
readiness score
classification
report
progression between assessments
The purpose is to make improvement visible over time.
Avoid building a complex analytics dashboard.
16. Interaction Standards
Forms
Keep forms short and well spaced.
Use clear labels rather than relying only on placeholders.
• 
• 
• 
• 
• 
10


## Page 11

Buttons
Maintain one obvious primary action per screen.
Error states
Explain what happened and what the user should do next.
Loading
Always show a clear state when the application is waiting on the backend or AI.
Mobile
Core candidate flows should remain usable on a mobile-width viewport.
Accessibility
Maintain:
readable typography
sufficient contrast
visible focus states
clear form labels
sensible keyboard navigation
17. Design Consistency
Use a small design system throughout the application.
Define consistently:
typography
spacing
button styles
input styles
borders
page width
section spacing
response states
score presentation
Do not independently redesign each screen.
The product should feel like one system.
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
11


## Page 12

18. Product Quality Standard
The application should feel finished even if the feature set is deliberately small.
Prioritize:
Clarity over decoration
Hierarchy over density
Consistency over novelty
Evidence over generic AI language
One complete experience over many incomplete screens
19. Design Reference
Use the design quality and restraint associated with modern product companies such as:
Stripe
Linear
Notion
These are references for:
typography
restraint
spacing
hierarchy
interaction quality
They are not templates to copy.
The final interface should be an original interpretation appropriate to the assessment experience.
20. Final Experience Standard
A candidate should be able to move through the product without explanation:
Understand the proposition → Provide context → Complete the assessment →
Understand the result → Know the next step
• 
• 
• 
• 
• 
12


## Page 13

The interface should make the technology feel simple.
The intelligence should be visible through the quality of the interaction and result, not through decorative
AI branding.
13


# Hackathon Developer Setup Guide(1).pdf


## Page 1

Hackathon | Developer Setup Guide
Goal: Build a working end-to-end application independently using the standard stack below.
Each participant will work independently using personal accounts and their own development environment.
1. How We Are Working
For the hackathon, each participant should:
Build their own implementation
Use their own personal accounts
Create their own private GitHub repository
Create their own database
Use their own API credentials
Run their own application independently
Do not use shared company infrastructure or credentials.
At the end of the hackathon, all implementations will be reviewed and one codebase may be selected for
further development.
2. Standard Technology Stack
Layer Technology
AI DevelopmentGoogle Antigravity
Frontend React
Backend FastAPI
Database PostgreSQL via Supabase
Authentication Supabase Auth, if required
LLM Gemini API
AI Testing Google AI Studio
Backend HostingRender
Frontend HostingVercel
Source Control GitHub
• 
• 
• 
• 
• 
• 
1


## Page 2

Keep the architecture simple
Do not introduce additional technologies unless they are genuinely required.
For this build, you should generally not need:
LangChain
Pinecone
ChromaDB
AWS
Kubernetes
Microservices
Message queues
Multiple databases
Focus on getting the core workflow working end-to-end first.
3. Accounts to Create
You can use personal accounts for all services.
Google
Use your personal Google account for:
Google Antigravity
Google AI Studio
Gemini API
GitHub
Create a private repository.
Recommended format:
hackathon-yourname
Example:
hackathon-john
Supabase
Create your own Supabase project.
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
2


## Page 3

Use it for:
PostgreSQL database
Authentication, if required
File storage, if required
Render
Use Render if backend deployment is required.
Deploy the FastAPI application as a Web Service.
Vercel
Use Vercel if frontend deployment is required.
Deployment is optional during development. A working local application is acceptable.
4. Recommended Project Structure
project/
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── backend/
│   ├── app/
│   ├── main.py
│   └── requirements.txt
│
├── README.md
├── .gitignore
└── .env.example
Keep frontend and backend in the same repository unless there is a clear reason not to.
5. Environment Variables
Do not hardcode credentials or API keys.
Create a local .env file.
• 
• 
• 
3


## Page 4

Example:
GEMINI_API_KEY=
SUPABASE_URL=
SUPABASE_ANON_KEY=
DATABASE_URL=
Commit:
.env.example
Do not commit:
.env
Your .gitignore should include:
.env
.env.*
node_modules/
__pycache__/
.venv/
You may explicitly retain .env.example.
6. Recommended Development Flow
Step 1
Start the React frontend locally.
Step 2
Start the FastAPI backend locally.
Step 3
Connect React to FastAPI.
4


## Page 5

Step 4
Create the Supabase database.
Step 5
Connect the backend to PostgreSQL.
Step 6
Connect Gemini.
Step 7
Implement the primary product workflow.
Step 8
Get one complete workflow working end-to-end.
Step 9
Improve UX, validation, and error handling.
Step 10
Deploy if useful for the final demonstration.
7. Engineering Principles
Build vertically
Prioritize a complete workflow:
User Input → Backend → AI / Logic → Database → Output
A complete working flow is more valuable than several partially completed features.
Keep the code understandable
Another engineer should be able to open your repository and understand:
What the application does
How it is structured
How to run it
• 
• 
• 
5


## Page 6

Where the main application logic sits
Use AI where AI is useful
Use Gemini for:
Language understanding
Reasoning
Extraction
Classification
Generation
Interpretation
Use normal application code for:
Validation
Calculations
Database operations
Permissions
Deterministic rules
Do not use an LLM for logic that can be implemented reliably in code.
8. Security Rules
These rules are mandatory.
Do not:
Commit API keys
Commit passwords
Hardcode credentials
Share credentials with other participants
Use company production credentials
Use real customer data
Make the GitHub repository public
Use environment variables for all secrets.
9. Final Submission
Your submission should include:
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
6


## Page 7

Working Application
The primary workflow should work end-to-end.
Private GitHub Repository
The repository should contain the complete source code.
README
Your README should explain:
What you built
Architecture
Setup instructions
Required environment variables
How to run the frontend
How to run the backend
Known limitations
Demo
Be prepared to demonstrate the complete product workflow.
10. Evaluation
Implementations will be reviewed based on:
Area What Matters
Product Does the core workflow actually work?
EngineeringIs the code clean and understandable?
ArchitectureIs the solution appropriately simple?
AI Is AI being used effectively?
UX Is the experience clear and usable?
Reliability Does the application work consistently?
Reasoning Were sensible technical decisions made?
Final Principle
Build the simplest solution that proves the product works.
• 
• 
• 
• 
• 
• 
• 
7


## Page 8

Prioritize working software, clean code, good reasoning, and a complete end-to-end
experience.
8
