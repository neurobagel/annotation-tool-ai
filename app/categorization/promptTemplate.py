from langchain_core.prompts import PromptTemplate

# noqa: E501

GeneralPrompt = PromptTemplate(
    template="""Given the column data {column}: {content},
determine the category and give only the category name as output

Examples:
1. Input: "participant_id: sub-01 sub-02 sub-03"
   Output: Participant_IDs

2. Input: 'pheno_age: ["34,1", "35,3", "NA", "39,0", "22,1",
   "23,2", "21,1", "22,3", "42,5", "43,2"]'
   Output: Age

3. Input: "session_id: ses-01 ses-02"
   Output: Session_IDs

4. Input: "pheno_sex : ["F", "F", "M", "M", "missing",
   "missing", "F", "F", "M", "M"]"
   Output: Sex

5. Input: "pheno_sex : ["1", "2", "1", "2", "missing", "missing"]"
   Output: Sex

Do Not Give any explanation in the output.
Input: "{column}: {content}"
Output= <category>
""",
    input_variables=["column", "content"],
)

AssessmentToolPrompt = PromptTemplate(
    template="""Given the column data {column}: {content},
Instructions: Based on the provided information,
please evaluate if this column is an assessment tool.
Consider the following characteristics of assessment tools
in your evaluation:
In context of medical studies return yes or no for {question}
if properties of Assessment tool is as follows:
The {content} structured in a way that suggests a test,
survey, or questionnaire or evaluation metric(e.g.,IQ,scores,
Likert scale, multiple-choice, ratings) and consistent format or
scale used throughout the {content} with numerical entries
(e.g., scores out of powers of 10, ratings in a range of numbers)?
The {column} aim to measure or evaluate something specific?

Give answer No if {column}:{content} indicate a "group"
or result of a collection

If not describing a diagnosis in context of medical research answer Yes

provide yes if assessment tool or no if not.
Do not give any explanation in the output.
""",
    input_variables=["column", "content", "question"],
)

DiagnosisPrompt = PromptTemplate(
    template="""Given the column data {column}: {content},
Based on the sample data provided, please evaluate whether each
column should be categorized as a "Diagnosis".
by considering the following characteristics
Is the column intended to indicate or identify
a medical diagnosis (purpose)?
Is the data {content} structured in a way that suggests
medical diagnoses, such as ICD codes,
disease names, their common abbreviations, or conditions (format)?
Is there a consistent format or terminology for
diagnoses used throughout the data?
including disease names, diagnostic codes, and
ecurring abbreviations (consistency)?
Does the content suggest medical diagnoses, including
names of diseases, conditions, or symptoms (content)?
Are there labels, descriptions, or metadata that
indicate the purpose of the column?
related to medical diagnoses (Metadata)?
In addition, if the column content consists of numbers,
check to see if it is dichotomous,
which indicates that it may be a diagnosis column.
If the content is strings, check if it is a list of strings,
which also indicates that it may be a diagnosis column.
If the content resembles scores or ratings, it is not a
diagnostic column.
The sample data may contain assessment tools;
These are not diagnostic columns. Output only a single "yes" or "no".
Do not include any explanation in the output.
""",
    input_variables=["column", "content"],
)


AssessmentLevelPrompt = PromptTemplate(
    template="""
    You are provided with a list of assessment tools.
    Your task is to determine which of these tools is
    most frequently used in
    neuropsychological and clinical research.
    List of assessment tools: {possible_tool_terms}

    Consider the following criteria to make your decision:
    - Frequency of citation in scientific literature and
    peer-reviewed journals.
    - Adoption and recommendation by major neuropsychological
    and clinical research organizations.
    - Prevalence of use in clinical trials and research studies.
    - Recognition and validation in published neuropsychological
    and clinical assessment protocols.
    - Endorsements by leading experts and institutions in the field.
    Do not include any explanation in the output. Only respond with
    the provided name of the most frequently used assessment tool.
    """,
    input_variables=["possible_tool_terms"],
)