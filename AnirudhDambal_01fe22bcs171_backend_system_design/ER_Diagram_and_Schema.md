# ER Diagram & Schema Design

## Multi-Tenant Medical Coding System

### Design Principles
- **Multi-tenancy**: Organization-based data isolation
- **Audit Trail**: Track all changes with timestamps and user information
- **Soft Deletes**: Preserve data integrity with logical deletion
- **Versioning**: Support for medical code versioning
- **Scalability**: Optimized indexes for common queries

---

## Entity Relationship Diagram Overview

```
┌──────────────┐
│ Organization │ (1)
└──────┬───────┘
       │ (1)
       │
       │ (N)
┌──────▼───────┐
│   Provider   │ (1)
└──────┬───────┘
       │ (1)
       │
       │ (N)
┌──────▼───────┐        ┌──────────────┐
│    Patient   │◄───────┤  Encounter   │
└──────┬───────┘ (N) (1)└──────┬───────┘
       │                       │
       │                       │
       │ (N)                   │ (N)
┌──────▼───────┐        ┌──────▼───────┐
│ Encounter    │        │ EncounterCode│
│ Diagnosis    │        │ Assignment   │
└──────┬───────┘        └──────┬───────┘
       │                       │
       │ (N)                   │ (N)
┌──────▼───────┐        ┌──────▼───────┐
│ICDCodeAssign │        │CPTCodeAssign │
│     ment     │        │     ment     │
└──────────────┘        └──────────────┘
         │                      │
         │ (N)                  │ (N)
         │                      │
         └──────┬───────────────┘
                │
                │ (1)
        ┌───────▼────────┐
        │  MedicalCode   │
        │   (Abstract)   │
        └───────┬────────┘
                │
        ┌───────┴────────┐
        │                │
┌───────▼────┐   ┌───────▼────┐
│  ICDCode   │   │  CPTCode   │
└────────────┘   └───────┬────┘
                         │
                         │ (N)
                ┌────────▼────────┐
                │ CPTModifierRules│
                └─────────────────┘
```

**Modifier Rules Relationship**:
- CPT Codes have many Modifier Rules (one-to-many)
- Each rule defines valid modifier-procedure combinations
- Supports effective dates for rule changes

---

## Database Schema

### 1. Organizations Table

Represents healthcare organizations (multi-tenancy root).

```sql
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_name VARCHAR(255) NOT NULL,
    organization_code VARCHAR(50) UNIQUE NOT NULL,
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'USA',
    phone VARCHAR(20),
    email VARCHAR(255),
    tax_id VARCHAR(50),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID,
    deleted_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT organizations_status_check CHECK (status IN ('active', 'inactive', 'suspended'))
);

CREATE INDEX idx_organizations_status ON organizations(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_organizations_code ON organizations(organization_code) WHERE deleted_at IS NULL;
CREATE INDEX idx_organizations_deleted_at ON organizations(deleted_at);
```

---

### 2. Providers Table

Healthcare providers (doctors, nurses, etc.) belonging to organizations.

```sql
CREATE TABLE providers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    provider_npi VARCHAR(10) UNIQUE NOT NULL, -- National Provider Identifier
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    title VARCHAR(50), -- MD, DO, NP, etc.
    specialty VARCHAR(100),
    license_number VARCHAR(50),
    email VARCHAR(255),
    phone VARCHAR(20),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID,
    deleted_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE RESTRICT,
    CONSTRAINT providers_status_check CHECK (status IN ('active', 'inactive', 'suspended'))
);

CREATE INDEX idx_providers_organization_id ON providers(organization_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_providers_npi ON providers(provider_npi) WHERE deleted_at IS NULL;
CREATE INDEX idx_providers_name ON providers(last_name, first_name) WHERE deleted_at IS NULL;
CREATE INDEX idx_providers_status ON providers(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_providers_deleted_at ON providers(deleted_at);
```

---

### 3. Patients Table

Patients who receive care from providers.

```sql
CREATE TABLE patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    patient_mrn VARCHAR(50) NOT NULL, -- Medical Record Number (org-scoped)
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    date_of_birth DATE NOT NULL,
    gender VARCHAR(20) CHECK (gender IN ('M', 'F', 'Other', 'Unknown')),
    ssn VARCHAR(11), -- Encrypted in production
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    phone VARCHAR(20),
    email VARCHAR(255),
    insurance_provider VARCHAR(255),
    insurance_member_id VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'deceased')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID,
    deleted_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE RESTRICT,
    CONSTRAINT patients_status_check CHECK (status IN ('active', 'inactive', 'deceased')),
    CONSTRAINT patients_org_mrn_unique UNIQUE (organization_id, patient_mrn, deleted_at)
);

CREATE INDEX idx_patients_organization_id ON patients(organization_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_patients_mrn ON patients(organization_id, patient_mrn) WHERE deleted_at IS NULL;
CREATE INDEX idx_patients_name ON patients(last_name, first_name) WHERE deleted_at IS NULL;
CREATE INDEX idx_patients_dob ON patients(date_of_birth) WHERE deleted_at IS NULL;
CREATE INDEX idx_patients_status ON patients(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_patients_deleted_at ON patients(deleted_at);
```

---

### 4. Encounters Table

Clinical encounters (visits, procedures) between providers and patients.

```sql
CREATE TABLE encounters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    patient_id UUID NOT NULL,
    provider_id UUID NOT NULL,
    encounter_type VARCHAR(50) NOT NULL CHECK (encounter_type IN ('office_visit', 'hospital_visit', 'emergency', 'surgery', 'procedure', 'telemedicine', 'other')),
    encounter_date DATE NOT NULL,
    encounter_time TIME,
    chief_complaint TEXT,
    visit_status VARCHAR(20) DEFAULT 'scheduled' CHECK (visit_status IN ('scheduled', 'in_progress', 'completed', 'cancelled', 'no_show')),
    billing_status VARCHAR(20) DEFAULT 'pending' CHECK (billing_status IN ('pending', 'coded', 'submitted', 'paid', 'denied')),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID,
    deleted_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE RESTRICT,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE RESTRICT,
    FOREIGN KEY (provider_id) REFERENCES providers(id) ON DELETE RESTRICT,
    CONSTRAINT encounters_encounter_type_check CHECK (encounter_type IN ('office_visit', 'hospital_visit', 'emergency', 'surgery', 'procedure', 'telemedicine', 'other')),
    CONSTRAINT encounters_visit_status_check CHECK (visit_status IN ('scheduled', 'in_progress', 'completed', 'cancelled', 'no_show')),
    CONSTRAINT encounters_billing_status_check CHECK (billing_status IN ('pending', 'coded', 'submitted', 'paid', 'denied'))
);

CREATE INDEX idx_encounters_organization_id ON encounters(organization_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_encounters_patient_id ON encounters(patient_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_encounters_provider_id ON encounters(provider_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_encounters_date ON encounters(encounter_date DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_encounters_billing_status ON encounters(billing_status) WHERE deleted_at IS NULL;
CREATE INDEX idx_encounters_org_patient_date ON encounters(organization_id, patient_id, encounter_date DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_encounters_deleted_at ON encounters(deleted_at);
```

---

### 5. ICD Codes Table

ICD-10 diagnosis codes with versioning support.

```sql
CREATE TABLE icd_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(10) NOT NULL, -- e.g., I10, E11.9
    code_version VARCHAR(10) NOT NULL DEFAULT '2024', -- ICD-10 version year
    short_description VARCHAR(255) NOT NULL,
    long_description TEXT,
    is_valid BOOLEAN DEFAULT TRUE,
    effective_date DATE,
    end_date DATE, -- For deprecated codes
    category VARCHAR(100), -- e.g., 'Diseases of the circulatory system'
    parent_code VARCHAR(10), -- For hierarchical relationships
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT icd_codes_code_version_unique UNIQUE (code, code_version)
);

CREATE INDEX idx_icd_codes_code ON icd_codes(code);
CREATE INDEX idx_icd_codes_version ON icd_codes(code_version);
CREATE INDEX idx_icd_codes_valid ON icd_codes(is_valid) WHERE is_valid = TRUE;
CREATE INDEX idx_icd_codes_description ON icd_codes USING gin(to_tsvector('english', long_description));
CREATE INDEX idx_icd_codes_category ON icd_codes(category);
```

---

### 6. CPT Codes Table

CPT procedure codes with versioning support.

```sql
CREATE TABLE cpt_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(10) NOT NULL, -- e.g., 99213, 36415
    code_version VARCHAR(10) NOT NULL DEFAULT '2024', -- CPT version year
    short_description VARCHAR(255) NOT NULL,
    long_description TEXT,
    category VARCHAR(100), -- e.g., 'Evaluation and Management', 'Surgery'
    is_valid BOOLEAN DEFAULT TRUE,
    effective_date DATE,
    end_date DATE, -- For deprecated codes
    base_value DECIMAL(10, 2), -- Relative value units (RVU)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT cpt_codes_code_version_unique UNIQUE (code, code_version)
);

CREATE INDEX idx_cpt_codes_code ON cpt_codes(code);
CREATE INDEX idx_cpt_codes_version ON cpt_codes(code_version);
CREATE INDEX idx_cpt_codes_valid ON cpt_codes(is_valid) WHERE is_valid = TRUE;
CREATE INDEX idx_cpt_codes_description ON cpt_codes USING gin(to_tsvector('english', long_description));
CREATE INDEX idx_cpt_codes_category ON cpt_codes(category);
```

---

### 7. Encounter ICD Code Assignments Table

Links encounters to ICD diagnosis codes.

```sql
CREATE TABLE encounter_icd_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    encounter_id UUID NOT NULL,
    icd_code_id UUID NOT NULL,
    assignment_type VARCHAR(20) DEFAULT 'primary' CHECK (assignment_type IN ('primary', 'secondary', 'rule_out')),
    is_confirmed BOOLEAN DEFAULT FALSE,
    assigned_by UUID, -- Provider or coder ID
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    confidence_score DECIMAL(5, 2) CHECK (confidence_score >= 0 AND confidence_score <= 100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID,
    deleted_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (encounter_id) REFERENCES encounters(id) ON DELETE CASCADE,
    FOREIGN KEY (icd_code_id) REFERENCES icd_codes(id) ON DELETE RESTRICT,
    CONSTRAINT encounter_icd_assignments_type_check CHECK (assignment_type IN ('primary', 'secondary', 'rule_out'))
);

CREATE INDEX idx_encounter_icd_encounter_id ON encounter_icd_assignments(encounter_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_encounter_icd_code_id ON encounter_icd_assignments(icd_code_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_encounter_icd_type ON encounter_icd_assignments(assignment_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_encounter_icd_confirmed ON encounter_icd_assignments(is_confirmed) WHERE deleted_at IS NULL AND is_confirmed = TRUE;
CREATE INDEX idx_encounter_icd_deleted_at ON encounter_icd_assignments(deleted_at);
```

---

### 8. Encounter CPT Code Assignments Table

Links encounters to CPT procedure codes.

```sql
CREATE TABLE encounter_cpt_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    encounter_id UUID NOT NULL,
    cpt_code_id UUID NOT NULL,
    quantity INTEGER DEFAULT 1 CHECK (quantity > 0),
    modifier_1 VARCHAR(2), -- CPT modifiers (e.g., 25, 59)
    modifier_2 VARCHAR(2),
    modifier_3 VARCHAR(2),
    modifier_4 VARCHAR(2),
    units DECIMAL(10, 2) DEFAULT 1.0,
    is_confirmed BOOLEAN DEFAULT FALSE,
    assigned_by UUID, -- Provider or coder ID
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    confidence_score DECIMAL(5, 2) CHECK (confidence_score >= 0 AND confidence_score <= 100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID,
    deleted_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (encounter_id) REFERENCES encounters(id) ON DELETE CASCADE,
    FOREIGN KEY (cpt_code_id) REFERENCES cpt_codes(id) ON DELETE RESTRICT,
    CONSTRAINT encounter_cpt_quantity_check CHECK (quantity > 0)
);

CREATE INDEX idx_encounter_cpt_encounter_id ON encounter_cpt_assignments(encounter_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_encounter_cpt_code_id ON encounter_cpt_assignments(cpt_code_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_encounter_cpt_confirmed ON encounter_cpt_assignments(is_confirmed) WHERE deleted_at IS NULL AND is_confirmed = FALSE;
CREATE INDEX idx_encounter_cpt_deleted_at ON encounter_cpt_assignments(deleted_at);
```

---

### 9. CPT Modifier Rules Table

Defines valid modifier-procedure combinations for CPT codes. This ensures only appropriate modifiers can be assigned to specific procedures.

```sql
CREATE TABLE cpt_modifier_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cpt_code_id UUID NOT NULL,
    modifier_code VARCHAR(2) NOT NULL, -- CPT modifier code (e.g., 25, 59, 76, 77)
    modifier_description VARCHAR(255),
    is_allowed BOOLEAN DEFAULT TRUE, -- Some modifiers may be explicitly disallowed
    effective_date DATE NOT NULL,
    end_date DATE, -- For deprecated rule combinations
    notes TEXT, -- Explanation of why this modifier is valid/invalid
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cpt_code_id) REFERENCES cpt_codes(id) ON DELETE CASCADE,
    CONSTRAINT cpt_modifier_rules_unique UNIQUE (cpt_code_id, modifier_code, effective_date),
    CONSTRAINT cpt_modifier_code_format CHECK (modifier_code ~ '^[0-9]{2}$' OR modifier_code ~ '^[A-Z]{2}$')
);

CREATE INDEX idx_cpt_modifier_rules_cpt_code ON cpt_modifier_rules(cpt_code_id) WHERE is_allowed = TRUE AND (end_date IS NULL OR end_date > CURRENT_DATE);
CREATE INDEX idx_cpt_modifier_rules_modifier ON cpt_modifier_rules(modifier_code);
CREATE INDEX idx_cpt_modifier_rules_effective ON cpt_modifier_rules(effective_date, end_date);
```

---

### 10. Modifiers Table (Reference)

Reference table for all valid CPT modifiers with descriptions.

```sql
CREATE TABLE cpt_modifiers (
    code VARCHAR(2) PRIMARY KEY, -- Modifier code (e.g., 25, 59, 76, 77, LT, RT)
    description VARCHAR(255) NOT NULL,
    category VARCHAR(50), -- e.g., 'Anesthesia', 'Surgical', 'Evaluation', 'Anatomic'
    is_active BOOLEAN DEFAULT TRUE,
    effective_date DATE,
    end_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cpt_modifiers_active ON cpt_modifiers(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_cpt_modifiers_category ON cpt_modifiers(category);
```

**Sample Modifier Data:**
- `25` - Significant, separately identifiable evaluation and management service
- `59` - Distinct procedural service
- `76` - Repeat procedure by same physician
- `77` - Repeat procedure by another physician
- `LT` - Left side
- `RT` - Right side

---

### 11. Code Assignment History Table (Audit Trail)

Tracks all changes to code assignments for audit purposes.

```sql
CREATE TABLE code_assignment_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assignment_type VARCHAR(20) NOT NULL CHECK (assignment_type IN ('icd', 'cpt')),
    assignment_id UUID NOT NULL,
    encounter_id UUID NOT NULL,
    action VARCHAR(20) NOT NULL CHECK (action IN ('created', 'updated', 'deleted', 'confirmed')),
    old_value JSONB, -- Previous state
    new_value JSONB, -- New state
    changed_by UUID,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    reason TEXT,
    FOREIGN KEY (encounter_id) REFERENCES encounters(id) ON DELETE CASCADE,
    CONSTRAINT code_assignment_history_action_check CHECK (action IN ('created', 'updated', 'deleted', 'confirmed'))
);

CREATE INDEX idx_code_history_assignment ON code_assignment_history(assignment_type, assignment_id);
CREATE INDEX idx_code_history_encounter ON code_assignment_history(encounter_id);
CREATE INDEX idx_code_history_changed_at ON code_assignment_history(changed_at DESC);
CREATE INDEX idx_code_history_changed_by ON code_assignment_history(changed_by);
```

---

## Multi-Tenancy Implementation

### Row-Level Security (PostgreSQL)

```sql
-- Enable RLS on all tenant-scoped tables
ALTER TABLE providers ENABLE ROW LEVEL SECURITY;
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE encounters ENABLE ROW LEVEL SECURITY;

-- Create policy function
CREATE OR REPLACE FUNCTION get_organization_id()
RETURNS UUID AS $$
BEGIN
    RETURN current_setting('app.current_organization_id', TRUE)::UUID;
END;
$$ LANGUAGE plpgsql STABLE;

-- Example policy for patients table
CREATE POLICY patients_organization_isolation ON patients
    FOR ALL
    USING (organization_id = get_organization_id())
    WITH CHECK (organization_id = get_organization_id());

-- Similar policies for providers and encounters
```

### Application-Level Multi-Tenancy

All queries should include `organization_id` in WHERE clauses:

```sql
-- Example: Get patients for organization
SELECT * FROM patients 
WHERE organization_id = :org_id 
AND deleted_at IS NULL;
```

---

## Key Design Decisions

1. **UUID Primary Keys**: Better for distributed systems and security
2. **Soft Deletes**: Preserve data integrity and audit trails
3. **Partial Indexes**: Optimize queries on non-deleted records
4. **Version Support**: Separate version columns for code evolution
5. **Full-Text Search**: GIN indexes on descriptions for code search
6. **Audit Trail**: Separate history table for code assignment changes
7. **Check Constraints**: Enforce data integrity at database level
8. **Cascade Deletes**: Encounters delete assignments, but preserve patients/providers

---

## Sample Queries

### Get all encounters for a patient with codes:

```sql
SELECT 
    e.id,
    e.encounter_date,
    e.encounter_type,
    p.first_name || ' ' || p.last_name AS provider_name,
    json_agg(DISTINCT jsonb_build_object(
        'code', ic.code,
        'description', ic.short_description,
        'type', eica.assignment_type
    )) FILTER (WHERE eica.id IS NOT NULL) AS icd_codes,
    json_agg(DISTINCT jsonb_build_object(
        'code', cc.code,
        'description', cc.short_description,
        'quantity', eca.quantity
    )) FILTER (WHERE eca.id IS NOT NULL) AS cpt_codes
FROM encounters e
LEFT JOIN providers p ON e.provider_id = p.id
LEFT JOIN encounter_icd_assignments eica ON e.id = eica.encounter_id AND eica.deleted_at IS NULL
LEFT JOIN icd_codes ic ON eica.icd_code_id = ic.id
LEFT JOIN encounter_cpt_assignments eca ON e.id = eca.encounter_id AND eca.deleted_at IS NULL
LEFT JOIN cpt_codes cc ON eca.cpt_code_id = cc.id
WHERE e.patient_id = :patient_id
AND e.deleted_at IS NULL
GROUP BY e.id, e.encounter_date, e.encounter_type, p.first_name, p.last_name
ORDER BY e.encounter_date DESC;
```

### Search ICD codes by description:

```sql
SELECT code, short_description, long_description
FROM icd_codes
WHERE to_tsvector('english', long_description) @@ plainto_tsquery('english', :search_term)
AND is_valid = TRUE
ORDER BY ts_rank(to_tsvector('english', long_description), plainto_tsquery('english', :search_term)) DESC
LIMIT 10;
```

=