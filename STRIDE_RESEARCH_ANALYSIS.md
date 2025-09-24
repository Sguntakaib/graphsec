# STRIDE Threat Modeling Research & Analysis
## Context-Aware Mapping Strategy for WebApp Questionnaires

---

## **Executive Summary**

Our current STRIDE implementation applies threats **generically** to all WebApps regardless of context, leading to false positives and security noise. This research proposes a **context-aware, conditional mapping strategy** that only applies threats where they are genuinely relevant based on:

1. **Application Architecture** (static vs dynamic, read-only vs interactive)
2. **Attack Surface** (exposed endpoints, data processing capabilities)
3. **Data Sensitivity** (public content vs confidential data)
4. **Existing Controls** (infrastructure protection, architectural boundaries)

---

## **Current Problem Analysis**

### **Issue 1: Generic Threat Application**
- **Problem**: All WebApps receive same threats regardless of actual risk
- **Example**: Static marketing site gets "Input Validation Tampering" threat
- **Result**: 7 STRIDE findings for optimal security configuration

### **Issue 2: No Architectural Context**
- **Problem**: No consideration of deployment architecture
- **Example**: App behind WAF/CDN gets DoS threats as if directly exposed
- **Result**: Irrelevant mitigation recommendations

### **Issue 3: Missing Contextual Questions**
- **Problem**: Basic questionnaire lacks questions to determine app characteristics
- **Example**: No questions about data sensitivity, user interaction patterns, or infrastructure

---

## **Research Findings: STRIDE Categories & Web Application Context**

### **S - Spoofing (Identity Authentication)**
**When Relevant:** Only for applications that:
- Have user authentication (`webapp_authentication_method` != "No Authentication")  
- Manage user sessions or identity  
- Process user-specific actions or data

**When NOT Relevant:**
- Public static websites with no authentication
- Read-only content sites
- Anonymous applications

### **T - Tampering (Data Integrity)**
**When Relevant:** Only for applications that:
- Accept user input (`webapp_input_validation` questions relevant)
- Connect to databases (`webapp_database_connection` = True)
- Expose API endpoints (`webapp_api_endpoints` = True)
- Handle file uploads or form submissions

**When NOT Relevant:**
- Static content delivery (no user input processing)
- Read-only applications
- Content-only websites (blogs, documentation)

### **R - Repudiation (Non-repudiation)**
**When Relevant:** Only for applications that:
- Require audit trails for compliance
- Process business transactions
- Handle sensitive user actions
- Need forensic capabilities

**When NOT Relevant:**
- Public content websites
- Anonymous applications
- Applications without business impact from user actions

### **I - Information Disclosure (Data Confidentiality)**
**When Relevant:** Only for applications that:
- Handle sensitive/confidential data
- Process personal information (PII)
- Manage authentication credentials
- Store or transmit proprietary information

**When NOT Relevant:**
- Public marketing/information websites
- Applications serving only public data
- Static content sites with no sensitive information

### **D - Denial of Service (Availability)**
**When Relevant:** Only for applications that:
- Are directly exposed to internet (not behind CDN/WAF)
- Handle resource-intensive operations
- Are business-critical for availability
- Lack infrastructure-level DoS protection

**When NOT Relevant:**
- Applications behind robust CDN/WAF protection
- Non-critical information sites
- Applications with infrastructure-level rate limiting

### **E - Elevation of Privilege (Authorization)**
**When Relevant:** Only for applications that:
- Have user roles or permissions
- Implement access controls
- Manage privileged operations
- Handle different user permission levels

**When NOT Relevant:**
- Applications with no authorization model
- Single-permission level applications
- Public content with no user roles

---

## **WebApp Questionnaire Analysis & Mapping Strategy**

### **Basic Questions Analysis (10 questions)**

| Question ID | STRIDE Relevance | Context Conditions |
|------------|------------------|-------------------|
| `webapp_authentication_method` | **S** | Always relevant if not "No Authentication" |
| `webapp_input_validation` | **T** | Only if processes input (DB connection OR API endpoints OR form handling) |
| `webapp_https_enforcement` | **I** | Only if handles sensitive data (authentication OR DB connection OR encryption needs) |
| `webapp_database_connection` | *Context Setter* | Enables T, I threats for other questions |
| `webapp_api_endpoints` | *Context Setter* | Enables T, D, E threats for other questions |
| `webapp_session_management` | **S, E** | Only if has authentication (not "No Authentication") |
| `webapp_error_handling` | **I** | Only if could expose sensitive system information |
| `webapp_logging_monitoring` | **R** | Only if requires audit trails or compliance |
| `webapp_data_encryption` | **I** | Only if handles sensitive/confidential data |
| `webapp_security_headers` | **I, T** | Only if serves dynamic content or handles user interaction |

### **Advanced Questions (Should be included based on context)**

| Question ID | STRIDE Relevance | When to Include |
|------------|------------------|-----------------|
| `webapp_authorization_model` | **E** | Only if has authentication + multiple user types |
| `webapp_rate_limiting` | **D** | Only if exposed to public + no infrastructure protection |
| `webapp_csrf_protection` | **T** | Only if has authentication + state-changing operations |
| `webapp_xss_protection` | **T, I** | Only if accepts user input or serves dynamic content |
| `webapp_sql_injection_protection` | **T** | Only if has database connection |

---

## **Proposed Implementation Strategy**

### **Phase 1: Application Context Detection**
Add contextual questions to determine application characteristics:

```yaml
# New Context Detection Questions
- id: "webapp_application_type"
  question: "What type of web application is this?"
  type: "single_choice" 
  options: ["Static content site", "Dynamic web application", "API service", "E-commerce platform", "Internal business application"]

- id: "webapp_data_sensitivity"
  question: "What is the highest sensitivity of data handled?"
  type: "single_choice"
  options: ["Public information only", "Internal business data", "Personal information (PII)", "Financial/payment data", "Highly confidential"]

- id: "webapp_user_interaction"
  question: "What user interactions does the application support?"
  type: "multiple_choice"
  options: ["Read-only content viewing", "Form submissions", "File uploads", "User registration/login", "Content management", "Financial transactions"]

- id: "webapp_infrastructure_protection"
  question: "What infrastructure protection is in place?"
  type: "multiple_choice"
  options: ["CDN (Cloudflare, AWS CloudFront)", "Web Application Firewall (WAF)", "API Gateway", "Load balancer with DDoS protection", "None"]
```

### **Phase 2: Context-Aware Threat Logic**
Implement conditional threat application:

```python
def should_apply_tampering_threats(responses: Dict) -> bool:
    """Only apply tampering threats if app processes user input"""
    return (
        responses.get("webapp_database_connection") == "True" or
        responses.get("webapp_api_endpoints") == "True" or
        "Form submissions" in responses.get("webapp_user_interaction", []) or
        "File uploads" in responses.get("webapp_user_interaction", [])
    )

def should_apply_information_disclosure_threats(responses: Dict) -> bool:
    """Only apply info disclosure threats if handles sensitive data"""
    sensitivity = responses.get("webapp_data_sensitivity")
    return sensitivity not in ["Public information only", "Unknown"]

def should_apply_dos_threats(responses: Dict) -> bool:
    """Only apply DoS threats if lacks infrastructure protection"""
    protection = responses.get("webapp_infrastructure_protection", [])
    has_protection = any(p in protection for p in ["CDN", "Web Application Firewall", "DDoS protection"])
    return not has_protection
```

### **Phase 3: Enhanced Threat Descriptions**
Make threats more specific and actionable:

```python
# Instead of generic "Basic Validation Provides Limited Protection"
# Use context-aware descriptions:
if database_connected:
    title = "Basic Input Validation Insufficient for Database Protection"
    description = "Application connects to database but uses basic validation, vulnerable to SQL injection"
    mitigations = ["Implement parameterized queries", "Add comprehensive server-side validation"]
elif api_endpoints:
    title = "Basic Input Validation Insufficient for API Security" 
    description = "Application exposes API endpoints but uses basic validation, vulnerable to injection attacks"
    mitigations = ["Implement schema validation", "Add API input sanitization"]
```

### **Phase 4: Risk Scoring Enhancement**
Adjust risk scores based on context:

```python
def calculate_contextual_risk(base_risk: float, context: Dict) -> float:
    """Adjust risk based on application context"""
    multiplier = 1.0
    
    # Higher risk for sensitive data
    if context["data_sensitivity"] == "Financial/payment data":
        multiplier *= 1.3
    elif context["data_sensitivity"] == "Personal information (PII)":
        multiplier *= 1.2
    
    # Lower risk if protected by infrastructure
    if context["has_infrastructure_protection"]:
        multiplier *= 0.7
        
    # Higher risk for public-facing apps
    if context["exposed_to_public"]:
        multiplier *= 1.1
        
    return min(10.0, base_risk * multiplier)
```

---

## **Expected Benefits**

### **1. Reduced False Positives**
- Static sites won't get input validation threats
- Public content sites won't get sensitive data threats  
- Protected infrastructure won't get DoS threats

### **2. More Actionable Results**
- Threats matched to actual attack surface
- Context-specific mitigation recommendations
- Risk scores reflecting real-world exposure

### **3. Better User Experience**
- 2-4 relevant threats instead of 7 generic ones
- Clear understanding of why threats apply
- Focused security improvements

---

## **Implementation Timeline**

### **Week 1: Context Detection**
- Add new contextual questions to webapp.yaml
- Update questionnaire UI to handle context questions
- Test context detection logic

### **Week 2: Conditional Threat Logic** 
- Implement context-aware threat application
- Update existing threat mappings with conditions
- Create contextual risk scoring

### **Week 3: Enhanced Descriptions**
- Rewrite threat titles and descriptions to be context-specific
- Update mitigation recommendations based on application type
- Add threat reasoning/justification

### **Week 4: Testing & Validation**
- Test different application types (static, dynamic, API)
- Validate threat relevance and accuracy
- Performance testing and optimization

---

## **Success Metrics**

1. **Threat Relevance**: 95%+ of threats should be genuinely applicable
2. **False Positive Reduction**: <10% false positive rate
3. **User Satisfaction**: Clear understanding of threat applicability
4. **Actionable Results**: Context-specific mitigations

---

## **Risk Mitigation**

- **Fallback Logic**: If context detection fails, use conservative defaults
- **Gradual Rollout**: Phase implementation with A/B testing
- **User Feedback**: Collection mechanism for threat relevance feedback
- **Expert Review**: Security expert validation of threat logic

---

## **Request for Approval**

This research-based approach will transform our STRIDE implementation from generic threat application to intelligent, context-aware security analysis. 

**Do you approve this strategy and implementation plan?**

**Any specific aspects you'd like modified or enhanced?**