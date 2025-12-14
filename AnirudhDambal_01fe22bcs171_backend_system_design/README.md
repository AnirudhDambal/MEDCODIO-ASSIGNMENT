# Backend System Design Assignment

## 📋 Overview

This assignment presents a complete backend system design for a **multi-tenant medical coding platform**. The system enables healthcare organizations to manage providers, patients, clinical encounters, and extract medical codes (ICD-10, CPT) with full audit trails and versioning support.

## 🎯 Objectives

- Design a scalable, multi-tenant database schema
- Create RESTful APIs for medical coding operations
- Implement data isolation and security best practices
- Support code versioning and audit trails
- Enable efficient code retrieval and management

## 📁 Assignment Contents

This assignment includes three comprehensive documents:

### 1. ER Diagram & Schema Design (`ER_Diagram_and_Schema.md`)

**Contents**:
- Complete Entity Relationship Diagram (ERD)
- Detailed SQL DDL for all 11 database tables
- Multi-tenancy implementation strategies
- Indexing strategies for performance
- Sample queries and data validation

**Key Tables**:
- `organizations` - Healthcare organizations (tenant root)
- `providers` - Healthcare providers
- `patients` - Patient records
- `encounters` - Clinical visits/procedures
- `icd_codes` - ICD-10 diagnosis codes (versioned)
- `cpt_codes` - CPT procedure codes (versioned)
- `encounter_icd_assignments` - Links encounters to ICD codes
- `encounter_cpt_assignments` - Links encounters to CPT codes (with modifiers)
- `cpt_modifier_rules` - Valid modifier-procedure combinations ⭐
- `cpt_modifiers` - Reference table for all modifiers ⭐
- `code_assignment_history` - Audit trail for all changes

### 2. API Design (`API_Design.md`)

**Contents**:
- Complete REST API specifications
- Endpoint documentation with request/response examples
- Authentication and authorization
- Error handling and status codes
- Rate limiting and versioning

**API Groups**:
- **Organizations APIs**: Create, read, update organizations
- **Providers APIs**: Manage healthcare providers
- **Patients APIs**: Patient record management
- **Encounters APIs**: Clinical encounter management
- **Medical Codes APIs**: ICD/CPT code search and retrieval
- **Code Assignment APIs**: Assign codes to encounters (with modifier validation)
- **Modifier Rule APIs**: Get valid modifiers per CPT code, validate modifiers ⭐
- **Audit APIs**: Access assignment history

### 3. Design Decisions (`Design_Decisions.md`)

**Contents**:
- Multi-tenancy approach and rationale
- Database design choices (UUIDs, soft deletes, etc.)
- API design patterns
- Versioning strategy
- Security and privacy considerations
- Scalability planning
- Future extensibility

## 🏗️ Architecture Highlights

### Multi-Tenancy

- **Organization-Based Isolation**: All tenant data scoped by `organization_id`
- **Row-Level Security**: Database-level policies for data isolation
- **Application-Level Filtering**: Middleware ensures tenant isolation

### Code Versioning

- **Versioned Code Tables**: Support for multiple ICD/CPT code versions
- **Historical Accuracy**: Past encounters retain original code versions
- **Backward Compatibility**: Queries support version filtering

### Audit Trail

- **Complete History**: Track all code assignment changes
- **User Attribution**: Record who made changes and when
- **Before/After States**: JSONB storage for flexible audit data

### Security

- **Data Isolation**: Complete tenant separation
- **Soft Deletes**: Preserve data for compliance
- **Encryption**: Support for sensitive data encryption
- **Access Control**: Role-based access patterns

## 📊 Database Schema Overview

```
┌──────────────┐
│ Organization │ (Root - Multi-tenancy)
└──────┬───────┘
       │
       ├───┐
       │   │
┌──────▼───▼──────┐
│   Providers     │
│   Patients      │
│   Encounters    │
└──────┬──────┬───┘
       │      │
       │      │
┌──────▼──┐ ┌─▼────────────┐
│ICD Codes│ │ CPT Codes    │
└────┬────┘ └─┬────────────┘
     │        │
     └───┬────┘
         │
  ┌──────▼──────────────┐
  │ Code Assignments    │
  │ (ICD & CPT)         │
  └──────┬──────────────┘
         │
  ┌──────▼──────────────┐
  │ Assignment History  │
  │ (Audit Trail)       │
  └─────────────────────┘
```

## 🚀 Getting Started

### Reading the Documents

1. **Start with ER Diagram & Schema**: Understand the database structure
2. **Review API Design**: See how to interact with the system
3. **Read Design Decisions**: Understand the rationale behind choices

### Visualization

**ER Diagram**: 
- The ER diagram is described textually with CREATE TABLE statements
- You can visualize it using:
  - Database design tools (MySQL Workbench, pgAdmin, DBeaver)
  - Online ERD tools (dbdiagram.io, draw.io)
  - Convert SQL to visual diagram

**API Design**:
- All endpoints are documented with examples
- Use tools like Postman or Swagger to test APIs
- Code examples included for common operations

## 📝 Key Design Principles

1. **Scalability**: Designed to handle thousands of organizations
2. **Security**: HIPAA-compliant data isolation
3. **Auditability**: Complete change tracking
4. **Flexibility**: Support for code versioning and extensions
5. **Performance**: Optimized indexes and query patterns

## 🔑 Features

### Core Functionality

- ✅ Multi-tenant data isolation
- ✅ Organization, provider, and patient management
- ✅ Clinical encounter tracking
- ✅ ICD-10 and CPT code assignment
- ✅ Code search and retrieval
- ✅ Assignment history and audit trails

### Advanced Features

- ✅ Code versioning (support for annual code updates)
- ✅ Soft deletes (data preservation)
- ✅ Bulk operations (batch code assignment)
- ✅ Full-text search (code descriptions)
- ✅ Confidence scoring (for AI-generated codes)
- ✅ Assignment confirmation workflow

## 💻 Technology Stack (Recommended)

- **Database**: PostgreSQL 14+ (recommended) or MySQL 8+
- **API Framework**: FastAPI, Django REST Framework, or Express.js
- **Authentication**: JWT tokens with organization context
- **Caching**: Redis for code lookups
- **Search**: PostgreSQL full-text search or Elasticsearch

## 📋 API Examples

### Create Encounter

```http
POST /v1/organizations/{org_id}/encounters
Content-Type: application/json

{
  "patient_id": "770e8400-e29b-41d4-a716-446655440002",
  "provider_id": "660e8400-e29b-41d4-a716-446655440001",
  "encounter_type": "office_visit",
  "encounter_date": "2024-01-20",
  "chief_complaint": "Chest pain and shortness of breath"
}
```

### Assign ICD Code

```http
POST /v1/organizations/{org_id}/encounters/{encounter_id}/icd-codes
Content-Type: application/json

{
  "icd_code_id": "bb0e8400-e29b-41d4-a716-446655440006",
  "assignment_type": "primary",
  "is_confirmed": true,
  "confidence_score": 95.5
}
```

### Search ICD Codes

```http
GET /v1/medical-codes/icd?search=hypertension&version=2024&page=1&limit=20
```

## 🔒 Security Considerations

1. **Authentication**: All endpoints require Bearer token
2. **Authorization**: Users can only access their organization's data
3. **Data Isolation**: Database-level and application-level checks
4. **Audit Logging**: All changes tracked with user attribution
5. **Encryption**: Sensitive fields (SSN) should be encrypted at rest

## 📈 Scalability

### Database Sharding
- Designed for horizontal sharding by `organization_id`
- Can scale to separate databases per tenant group

### Caching Strategy
- Cache code lookups (rarely change)
- Cache frequently accessed patient/provider data
- Use Redis for distributed caching

### Read Replicas
- Use read replicas for reporting queries
- Separate analytics workloads

## 🧪 Testing Recommendations

1. **Unit Tests**: Test each API endpoint
2. **Integration Tests**: Test multi-tenant isolation
3. **Load Tests**: Test with multiple organizations
4. **Security Tests**: Verify data isolation
5. **Audit Tests**: Validate history tracking

## 📚 Additional Resources

### Documentation Files

- `ER_Diagram_and_Schema.md` - Complete database design with modifier rules
- `API_Design.md` - Full API specifications including modifier APIs
- `Design_Decisions.md` - Architecture rationale (comprehensive)
- `MODIFIER_RULES_DESIGN.md` - Detailed modifier rule system design ⭐

### Key Sections in Each Document

**ER Diagram**:
- Table schemas with all columns
- Foreign key relationships
- Indexes and constraints
- Sample queries

**API Design**:
- Endpoint URLs and methods
- Request/response formats
- Error codes and handling
- Authentication details

**Design Decisions**:
- Multi-tenancy rationale
- Database choices explained
- API design patterns
- Security considerations
- Scalability planning

## 🔮 Future Enhancements

- [ ] Support for HCPCS codes
- [ ] Code modifier management
- [ ] AI/ML integration for code suggestions
- [ ] Real-time code validation
- [ ] Workflow management for code review
- [ ] Reporting and analytics APIs
- [ ] Integration with EHR systems
- [ ] FHIR compliance

## 📝 Submission Format

These documents are provided in Markdown format and can be:

1. **Read Directly**: Markdown renders nicely in most viewers
2. **Converted to Word**: Use Pandoc or online converters
3. **Visualized**: Import SQL DDL into database design tools

## ✅ Assignment Requirements Checklist

### Requirement 1: ER Diagram ✅
- [x] Visual ER diagram (ASCII format in document)
- [x] Shows Organizations, Providers, Patients, Encounters
- [x] Shows Diagnosis and Procedure tables
- [x] Shows Modifier tables (cpt_modifier_rules, cpt_modifiers)
- [x] Clear PK/FK relationships documented
- [x] Many-to-many relationships resolved (junction tables)

### Requirement 2: Database Schema Definition ✅
- [x] Complete table-by-table schema (11 tables)
- [x] Field names and data types specified
- [x] Primary & Foreign keys defined
- [x] Constraints (CHECK, UNIQUE, NOT NULL) included
- [x] Versioning support for code sets (version columns)
- [x] Modifier-rule tables (cpt_modifier_rules, cpt_modifiers)

### Requirement 3: REST API Design ✅
- [x] Complete list of endpoints (50+ endpoints)
- [x] HTTP methods (GET, POST, PUT, DELETE) used appropriately
- [x] Request & response JSON examples for all endpoints
- [x] Logical endpoint grouping by resource type
- [x] Error handling and status codes documented

### Requirement 4: Modifier Rule Design ✅
- [x] Data model for valid modifier-procedure combinations
  - `cpt_modifier_rules` table defined
  - `cpt_modifiers` reference table defined
- [x] Lookup API for valid modifiers per CPT code
  - `GET /medical-codes/cpt/{id}/valid-modifiers`
  - `POST /medical-codes/cpt/{id}/validate-modifier`
- [x] Separate design document: `MODIFIER_RULES_DESIGN.md`

### Requirement 5: Multi-Tenancy Strategy Explanation ✅
- [x] Tenant isolation approach documented
  - Organization-based row-level isolation
  - Application-level filtering
  - Row-Level Security (RLS) policies
- [x] Organization-based data scoping explained
- [x] Security considerations detailed
  - HIPAA compliance
  - Data segregation
  - Access control

### Requirement 6: Versioning Strategy Explanation ✅
- [x] Effective dates for ICD/CPT/Modifier codes
  - `effective_date` and `end_date` columns
  - Version column in code tables
- [x] Handling historical encounters explained
  - Old encounters retain original code versions
  - Assignment tables reference code by ID (includes version)
- [x] Safe upgrades of code sets documented
  - New versions don't affect existing assignments
  - Backward compatibility maintained

### Requirement 7: Short Explanation Document ✅
- [x] Design decisions explained (Design_Decisions.md)
- [x] Trade-offs discussed (UUID vs integers, soft deletes, etc.)
- [x] Scalability considerations covered
  - Sharding strategy
  - Caching approach
  - Read replicas
- [x] Real-world healthcare alignment addressed
  - HIPAA compliance
  - Audit requirements
  - Billing accuracy

## 👤 Author

Assignment submission for MEDCODIO AI Engineer position.

---

**Questions?** All design decisions are explained in detail in `Design_Decisions.md`.
